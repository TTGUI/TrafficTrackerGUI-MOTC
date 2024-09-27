import sys
import os
from PySide2.QtWidgets import (
    QApplication, QMainWindow, QAction, QFileDialog, QToolBar,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
)
from PySide2.QtGui import QPixmap, QPen, QColor, QPolygonF, QIcon, QPainter
from PySide2.QtCore import Qt, QPointF, QRectF

class ImageViewer(QGraphicsView):
    def __init__(self, parent=None):
        super(ImageViewer, self).__init__(parent)
        self._zoom = 0
        self._empty = True
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self._image = None

    def hasImage(self):
        return not self._empty

    def fitInView(self):
        rect = QRectF(self._image.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            self._zoom = 0
            self.resetTransform()
            self.scale(1, 1)

    def setImage(self, pixmap):
        self.scene.clear()
        self._image = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self._image)
        self._empty = False
        self.fitInView()

    def wheelEvent(self, event):
        if self.hasImage():
            if event.modifiers() == Qt.ControlModifier:
                if event.angleDelta().y() > 0:
                    factor = 1.25
                    self._zoom += 1
                else:
                    factor = 0.8
                    self._zoom -= 1
                self.scale(factor, factor)
            elif event.modifiers() == Qt.ShiftModifier:
                scroll_amount = event.angleDelta().y()
                self.horizontalScrollBar().setValue(
                    self.horizontalScrollBar().value() - scroll_amount)
            else:
                scroll_amount = event.angleDelta().y()
                self.verticalScrollBar().setValue(
                    self.verticalScrollBar().value() - scroll_amount)
        else:
            super(ImageViewer, self).wheelEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.viewer = ImageViewer()
        self.setCentralWidget(self.viewer)
        self.createActions()
        self.createToolBar()
        self.setWindowTitle("YOLO Dataset Viewer")

        self.image_paths = []
        self.current_image_index = -1

    def createActions(self):
        self.loadImageAct = QAction(QIcon.fromTheme("document-open"), "Load Image", self)
        self.loadImageAct.triggered.connect(self.loadImage)

        self.loadFolderAct = QAction(QIcon.fromTheme("folder-open"), "Load Folder", self)
        self.loadFolderAct.triggered.connect(self.loadFolder)

        self.nextImageAct = QAction(QIcon.fromTheme("go-next"), "Next Image", self)
        self.nextImageAct.triggered.connect(self.nextImage)

        self.prevImageAct = QAction(QIcon.fromTheme("go-previous"), "Previous Image", self)
        self.prevImageAct.triggered.connect(self.prevImage)

        # New Action for Saving All Images with Polygons
        self.saveAllAct = QAction(QIcon.fromTheme("document-save-all"), "Save All with Polygons", self)
        self.saveAllAct.triggered.connect(self.saveAllImagesWithPolygons)

    def createToolBar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        toolbar.addAction(self.loadImageAct)
        toolbar.addAction(self.loadFolderAct)
        toolbar.addSeparator()
        toolbar.addAction(self.prevImageAct)
        toolbar.addAction(self.nextImageAct)
        toolbar.addSeparator()
        toolbar.addAction(self.saveAllAct)

    def loadImage(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Images (*.jpg *.jpeg *.bmp)")
        if fileName:
            self.image_paths = [fileName]
            self.current_image_index = 0
            self.loadCurrentImage()

    def loadFolder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.image_paths = [
                os.path.join(folder, file)
                for file in os.listdir(folder)
                if file.lower().endswith(('.jpg', '.jpeg', '.bmp'))
            ]
            self.image_paths.sort()
            self.current_image_index = 0
            self.loadCurrentImage()

    def loadCurrentImage(self):
        if self.image_paths:
            image_path = self.image_paths[self.current_image_index]
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                self.viewer.setImage(pixmap)
                self.loadAnnotations(image_path)
            else:
                print("Failed to load image.")

    def loadAnnotations(self, image_path):
        txt_file = os.path.splitext(image_path)[0] + '.txt'
        if os.path.exists(txt_file):
            with open(txt_file, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) >= 3 and len(parts[1:]) % 2 == 0:
                        coords = list(map(float, parts[1:]))
                        self.drawPolygon(coords)

    def drawPolygon(self, coords):
        pixmap = self.viewer._image.pixmap()
        width = pixmap.width()
        height = pixmap.height()
        points = [
            QPointF(coords[i] * width, coords[i + 1] * height)
            for i in range(0, len(coords), 2)
        ]
        self.viewer.scene.addPolygon(
            QPolygonF(points), QPen(QColor(255, 0, 0), 2)
        )

    def nextImage(self):
        if self.image_paths and self.current_image_index < len(self.image_paths) - 1:
            self.current_image_index += 1
            self.loadCurrentImage()

    def prevImage(self):
        if self.image_paths and self.current_image_index > 0:
            self.current_image_index -= 1
            self.loadCurrentImage()

    # New Method to Save All Images with Polygons
    def saveAllImagesWithPolygons(self):
        if not self.image_paths:
            return

        for image_path in self.image_paths:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                painter = QPainter(pixmap)
                self.drawAnnotationsOnPixmap(painter, pixmap, image_path)
                painter.end()
                # Save the pixmap with "_Polygon.jpg" suffix
                save_path = os.path.splitext(image_path)[0] + '_Polygon.jpg'
                pixmap.save(save_path, 'JPG')
            else:
                print(f"Failed to load image {image_path}")

        print("All images have been saved with polygons.")

    def drawAnnotationsOnPixmap(self, painter, pixmap, image_path):
        width = pixmap.width()
        height = pixmap.height()
        txt_file = os.path.splitext(image_path)[0] + '.txt'
        if os.path.exists(txt_file):
            with open(txt_file, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) >= 3 and len(parts[1:]) % 2 == 0:
                        coords = list(map(float, parts[1:]))
                        points = [
                            QPointF(coords[i] * width, coords[i + 1] * height)
                            for i in range(0, len(coords), 2)
                        ]
                        polygon = QPolygonF(points)
                        pen = QPen(QColor(255, 0, 0), 2)
                        painter.setPen(pen)
                        painter.drawPolygon(polygon)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
