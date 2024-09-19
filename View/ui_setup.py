from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile

def load_ui(window, ui_path='./View/my_window.ui'):
    loader = QUiLoader()
    file = QFile(ui_path)
    file.open(QFile.ReadOnly)
    window = loader.load(file)
    file.close()
    return window