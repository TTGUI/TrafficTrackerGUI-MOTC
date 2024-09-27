from PySide2.QtGui import QIcon, QFont
from pathlib import Path
from logs import logger
from config import conf
from PySide2.QtWidgets import QSizePolicy
from PySide2 import QtCore

def set_window_title(window,  stab_mode, yolo_model, section, icon_path = './View/icon.png'):
    """Setup window icon and title"""
    
    if Path(icon_path).is_file():
        window.setWindowIcon(QIcon(icon_path))
    else:
        logger.warning(f" Icon file not found: [{icon_path}]")
    
    section = conf.getSection_mode()
    section_text = "intersection" if section == "intersection" else "roadsection"
    
    window.title.setText(f"{conf.RTVersion()} | {stab_mode} | {yolo_model} | {section_text}")
    window.setWindowTitle(conf.RTVersion())

def set_font(window):
    """Set the default font for the window"""
    title_font = QFont("Arial", 15, QFont.Bold)
    window.title.setFont(title_font)

    default_font = QFont("Arial", 11)
    window.setFont(default_font)

    window.display.setMinimumSize(0, 0)
    window.display.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
    window.display.setScaledContents(False)
    window.display.setAlignment(QtCore.Qt.AlignCenter)
    window.display.setStyleSheet("background-color: black;")
    window.display.setScaledContents(True)

def reset_ui_labels(window):
    """Clear/reset specific labels in the window"""
    window.cutinfo.setText('')
    window.display.setText('')
    window.FPS.setText('')
    window.ActionName_edit.setText('inital_action_name')
