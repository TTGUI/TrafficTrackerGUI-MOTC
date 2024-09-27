import sys
from PySide2 import QtCore, QtGui, QtWidgets
import os  # 新增，用於取得檔案名稱

class ImageViewer(QtWidgets.QGraphicsView):
    pointAdded = QtCore.Signal()
    pointRemoved = QtCore.Signal()
    pointsUpdated = QtCore.Signal()  # 當點集更新時發出

    def __init__(self, parent=None):
        super(ImageViewer, self).__init__(parent)
        self.setRenderHints(QtGui.QPainter.Antialiasing)
        self._scene = QtWidgets.QGraphicsScene(self)
        self.setScene(self._scene)
        self._pixmap_item = None
        self._polygon_item = None
        self.points = []
        self.point_items = []  # 用於儲存黃色點的圖形項目
        self.is_closing = False
        self.setMouseTracking(True)
        self._scale = 1.0

    def load_image(self, image_path):
        pixmap = QtGui.QPixmap(image_path)
        if self._pixmap_item:
            self._scene.removeItem(self._pixmap_item)
        self._pixmap_item = self._scene.addPixmap(pixmap)
        self.setSceneRect(pixmap.rect())
        self.points.clear()
        self.update_polygon()
        self.resetTransform()
        self._scale = 1.0

    def update_polygon(self):
        # 移除先前的多邊形
        if self._polygon_item:
            self._scene.removeItem(self._polygon_item)
        # 移除先前的點圖形項目
        for item in self.point_items:
            self._scene.removeItem(item)
        self.point_items.clear()
        # 繪製新的多邊形和點
        if self.points:
            polygon = QtGui.QPolygon(self.points)  # 使用 QPolygon，支援整數座標
            self._polygon_item = self._scene.addPolygon(polygon, pen=QtGui.QPen(QtCore.Qt.red, 2))
            # 為每個頂點新增黃色的點
            for point in self.points:
                ellipse = QtWidgets.QGraphicsEllipseItem(point.x() - 3, point.y() - 3, 6, 6)
                ellipse.setBrush(QtGui.QBrush(QtCore.Qt.yellow))
                self._scene.addItem(ellipse)
                self.point_items.append(ellipse)
        else:
            self._polygon_item = None
        self.pointsUpdated.emit()  # 發出點集更新的訊號

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            pos = self.mapToScene(event.pos())
            pos_int = QtCore.QPoint(int(pos.x()), int(pos.y()))  # 座標轉為整數
            if event.modifiers() & QtCore.Qt.ControlModifier:
                self.is_closing = True
                self.update_polygon()
            else:
                self.points.append(pos_int)
                self.update_polygon()
                self.pointAdded.emit()
        elif event.button() == QtCore.Qt.RightButton:
            if self.points:
                self.points.pop()
                self.update_polygon()
                self.pointRemoved.emit()
        super(ImageViewer, self).mousePressEvent(event)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if event.modifiers() & QtCore.Qt.ControlModifier:
            factor = 1.2 if delta > 0 else 0.8
            self._scale *= factor
            self.scale(factor, factor)
        elif event.modifiers() & QtCore.Qt.ShiftModifier:
            h_scroll = self.horizontalScrollBar()
            h_scroll.setValue(h_scroll.value() - delta)
        else:
            v_scroll = self.verticalScrollBar()
            v_scroll.setValue(v_scroll.value() - delta)

    def set_points_from_text(self, text):
        try:
            coords = eval(text)
            self.points = [QtCore.QPoint(int(x), int(y)) for x, y in coords]  # 確保座標為整數
            self.update_polygon()
            # 因為點集可能整體改變，發出點集更新的訊號
            self.pointsUpdated.emit()
        except:
            pass

    def get_points_text(self):
        return str([(int(p.x()), int(p.y())) for p in self.points])  # 輸出整數座標

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.viewer = ImageViewer()
        self.setCentralWidget(self.viewer)
        self.create_actions()
        self.create_toolbar()
        self.create_input_panel()
        # 連接 pointsUpdated 訊號
        self.viewer.pointsUpdated.connect(self.update_point_text)
        self.setWindowTitle("Polygon Drawing Tool")
        self.current_image_path = None  # 用於儲存當前圖片路徑

    def create_actions(self):
        self.load_action = QtWidgets.QAction("Load Image", self)
        self.load_action.triggered.connect(self.load_image)

    def create_toolbar(self):
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.addAction(self.load_action)

    def create_input_panel(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        self.point_input = QtWidgets.QLineEdit()
        self.set_points_button = QtWidgets.QPushButton("Set Points")
        self.set_points_button.clicked.connect(self.set_points)
        layout.addWidget(QtWidgets.QLabel("Points:"))
        layout.addWidget(self.point_input)
        layout.addWidget(self.set_points_button)
        widget.setLayout(layout)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, QtWidgets.QDockWidget("", self, widget=widget))

    def load_image(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Image", "",
                                                             "Image Files (*.png *.jpg *.jpeg)")
        if file_name:
            self.viewer.load_image(file_name)
            self.current_image_path = file_name
            # 更新視窗標題，顯示當前圖片檔案名稱
            base_name = os.path.basename(file_name)
            self.setWindowTitle(f"Polygon Drawing Tool - {base_name}")

    def set_points(self):
        text = self.point_input.text()
        self.viewer.set_points_from_text(text)

    def update_point_text(self):
        self.point_input.setText(self.viewer.get_points_text())

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
