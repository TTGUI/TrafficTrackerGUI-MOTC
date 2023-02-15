from logs import logger
from View.main_window import MainWindow
import sys
from PySide2 import QtWidgets

class mainWindowStart() :
    def __init__(self, parent=None) :
        self.app = QtWidgets.QApplication(sys.argv)
        self.mainwindow = MainWindow()
        self.mainwindow.window.show()

        ret = self.app.exec_()
        sys.exit(ret)



    