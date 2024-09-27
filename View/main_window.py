
import numpy as np
from PySide2 import QtCore

from PySide2.QtWidgets import QFileDialog, QMessageBox

from logs import logger
from config import conf

import cv2
import os

from .ui_setup import load_ui
from .ui_setupFont import set_window_title, set_font, reset_ui_labels
from .ui_Schedule import *
from .ui_Developer import DeveloperManager
from .ui_Schedule import ScheduleManager
from .ui_Step import StepManager
from .ui_DisplayInfo import DisplayinfoManager
from .ui_Player import PlayerManager

class MainWindow(object):

    def __init__(self, parent=None):
        """Main window, holding all user interface including.
        Args:
          parent: parent class of main window
        Returns:
          None
        Raises:
          None
        """
        # Main Setting
        self.actionName = "inital_action_name"
        self.resultPath = "./result/"

        # Deveploer Bar
        self.stabMode = conf.getStabMode() # 'CPU' 'GPU'
        self.yoloModel = conf.getYoloModel() #  20211109172733_last_200_1920.pt / ect.
        self.TIVPmode = conf.getTIVPMode() # <1> <2>

        # schedule
        self.scheduleType = 'off' # 'off' 'edit' 'run'
        self.currentScheduleIndex = 0
        self.ScheduleList = []
        self.scheduleLoadPath = ""
        self.scheduleSavePath = ""
        self.scheduleName = "Default"
        self.scheduleTIVFolderPath = ""
        self.scheduleTIVFile = ""

        # player
        self.play_bool = False
        self.currentStep = -1
        self.page = 0
        self.pageLen = 10

        # Prepare
        self.video_init = False
        self.droneFolderPath = "./data"
        self.cutinfo_txt = self.resultPath + self.actionName + "_cutInfo.txt"
        self.currentStartID = -1
        self.currentEndID = -1

        # Kstabilization
        self.stab_input = self.droneFolderPath
        self.stab_output = self.resultPath + self.actionName + "_stab.mp4"
        self.show = True
        
        # Mtracking 
        self.stab_video = self.stab_output
        self.yolo_txt = self.resultPath+ self.actionName +"_stab_8cls.txt"
        self.tracking_csv = self.resultPath + self.actionName + ".csv"

        # NBackground
        self.background_img = self.resultPath+ self.actionName +"_background.jpg" # English Path only....

        # OdrawIO & PIOadded
        self.section = conf.getSection_mode()
        self.gateLineIO_txt = self.resultPath + self.actionName + "_IO.txt"
        self.gate_tracking_csv = self.resultPath + self.actionName + "_gate.csv"

        # QReplay
        self.result_video = self.resultPath + self.actionName + "_result.avi"
        self.displayType = True

        # TIV
        self.singelTIVpath = self.resultPath + self.actionName + "_TIV.csv"
        self.showTrackingBool = True

        # UI
        self._window = None
        self.setup_ui()

        """
        YOU ALOS NEED TO MODIFY FUNCTION 'changeActionName'
        """

    @property
    def window(self):
        """The main window object"""
        return self._window

    def setup_ui(self):
        self._window = load_ui(self._window)
        self.set_font()
        self.DeveloperManager = DeveloperManager(self)
        self.ScheduleManager = ScheduleManager(self)
        self.StepManager = StepManager(self)
        self.DisplayinfoManager = DisplayinfoManager(self)
        self.PlayerManager = PlayerManager(self)

    def set_font(self):
        """Set window title, icon, and fonts"""
        set_window_title(self._window, self.stabMode, self.yoloModel, self.section)
        set_font(self._window)
        reset_ui_labels(self._window)
