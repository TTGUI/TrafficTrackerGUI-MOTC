from PySide2.QtGui import QIcon, QFont
from pathlib import Path
from logs import logger
from config import conf

def set_window_title(window, conf, stab_mode, yolo_model, section, icon_path = './View/icon.png'):
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

def reset_ui_labels(window):
    """Clear/reset specific labels in the window"""
    window.cutinfo.setText('')
    window.display.setText('')
    window.FPS.setText('')
    window.ActionName_edit.setText('inital_action_name')
