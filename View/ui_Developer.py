from PySide2.QtCore import Slot, QFile
from PySide2.QtWidgets import QFileDialog, QDialog
from config import conf
from PySide2.QtUiTools import QUiLoader
from .ui_BaseManager import BaseManager
from Cont import controller
class DeveloperManager(BaseManager):
    """本類別處理 Developer Options 的文字、功能綁定、功能函數"""
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        
        self.initText()     # 初始化按鈕文字
        self.bind_buttons() # 綁定按鈕與槽
        
    def initText(self):
        """初始化按鈕文字"""
        self.main_window._window.bar_1.setText('Run Pedestrian Detection')
        if conf.getStabMode() == 'CPU':
            self.main_window._window.bar_2.setText("Change Stabilazation Mode | [ CPU ]")
        elif conf.getStabMode() == 'GPU':
            self.main_window._window.bar_2.setText("Change Stabilazation Mode | [ GPU ]")
        self.main_window._window.bar_3.setText('Change YOLO Model')
        if self.main_window.TIVPmode == 1:
            self.main_window._window.bar_4.setText("Change TIVP Mode | [ Video ]")
        elif self.main_window.TIVPmode == 2:
            self.main_window._window.bar_4.setText("Change TIVP Mode | [ Image ]")
        elif self.main_window.TIVPmode == 3:
            self.main_window._window.bar_4.setText("Change TIVP Mode | [ Real Time Display ]")
        self.main_window._window.Change_Tracking_Setting.setText('Change Tracking Settings')
        self.main_window._window.Change_Section_Mode.setText('Change Section Mode')

    def bind_buttons(self):
        """將所有按鈕與槽綁定"""
        self.main_window._window.bar_1.triggered.connect(self.runPedestrian)
        self.main_window._window.bar_2.triggered.connect(self.change_stab_mode)
        self.main_window._window.bar_3.triggered.connect(self.changeYoloModel)
        self.main_window._window.bar_4.triggered.connect(self.changeTIVPbMode)
        self.main_window._window.Change_Tracking_Setting.triggered.connect(self.changeTrackingSet)
        self.main_window._window.Change_Section_Mode.triggered.connect(self.changeSectionMode)
        self.main_window._window.Change_Output_WxH.triggered.connect(self.changeOutputWH)
        self.main_window._window.TIV_Setting.triggered.connect(self.changeTIVsetting)

    """按鈕功能"""
    Slot()
    def runPedestrian(self):
        print("PedestrianDataMaker")
        controller.con_DO1(self.main_window.droneFolderPath, self.main_window.resultPath, self.main_window.cutinfo_txt, self.main_window.actionName)
    @Slot()
    def change_stab_mode(self):
        if self.main_window.stabMode == 'CPU':
            self.main_window.stabMode = 'GPU'
            conf.setStabMode('GPU')
            self.main_window._window.bar_2.setText("Change Stabilization Mode | [ GPU ]")
            self.main_window._window.step1_btn.setText('[STEP 1] (G)\nStable')
        elif self.main_window.stabMode == 'GPU':
            self.main_window.stabMode = 'CPU'
            conf.setStabMode('CPU')
            self.main_window._window.bar_2.setText("Change Stabilization Mode | [ CPU ]")
            self.main_window._window.step1_btn.setText('[STEP 1] (C)\nStable')
        self.main_window._window.title.setText(str(conf.RTVersion()) + " | " + self.main_window.stabMode + " | " + self.main_window.yoloModel + " | " + self.main_window.section)
    @Slot()
    def changeYoloModel(self):
        actName = QFileDialog.getOpenFileName(self.main_window._window, 'Select file to set Yolo Model.', "./Model/YOLOv4/weights")
        tempName = actName[0].split('/')
        if tempName[-1] != '':
            print(tempName[-1])
            self.main_window.yoloModel = tempName[-1]
            self.main_window._window.title.setText(str(conf.RTVersion()) + " | " + self.main_window.stabMode + " | " + self.main_window.yoloModel + " | " + self.main_window.section)
            conf.setYoloModel(self.main_window.yoloModel)
        else :
            print("[CANCEL] YoloModel change cancel.")
    @Slot()
    def changeTIVPbMode(self):
        if self.main_window.TIVPmode == 1:
            self.main_window.TIVPmode = 2
            conf.setTIVPMode(2)
            self.main_window._window.bar_4.setText("Change TIVP Mode | [ Image ]")
            self.main_window._window.TIVPrinter_btn.setText('[STEP 9]\nTIV Printer (I)')
        elif self.main_window.TIVPmode == 2:
            self.main_window.TIVPmode = 3
            conf.setTIVPMode(3)
            self.main_window._window.bar_4.setText("Change TIVP Mode | [ Real Time Display ]")
            self.main_window._window.TIVPrinter_btn.setText('[STEP 9]\nTIV Printer (R)')
        elif self.main_window.TIVPmode == 3:
            self.main_window.TIVPmode = 1
            conf.setTIVPMode(1)
            self.main_window._window.bar_4.setText("Change TIVP Mode | [ Video ]")
            self.main_window._window.TIVPrinter_btn.setText('[STEP 9]\nTIV Printer (V)')

        # from .ui_Schedule import ScheduleManager
        # ScheduleManager.renewScheduleBoard(self)  
        self.renewScheduleBoard()            
    @Slot()
    def changeTrackingSet(self):
        self.CTS_dialog = QDialog()
        ui_file_name = './View/CTS_dialog.ui'
        file = QFile(ui_file_name)
        loader = QUiLoader()
        self.CTS_dialog = loader.load(file)
        file.close()
        self.CTS_dialog.setWindowTitle('change Tracking Setting')
        self.CTS_dialog.CTS_trackingSetText.setText('Enter tracking setting : max_age, min_hits, iou_threshold')
        self.CTS_dialog.CTS_label_Trk1.setText(f'大車 (汽車,卡車,公車) Set\nDefault : (10, 2, 0.05)\nCurrent : {conf.getTrk1_Set()}')
        self.CTS_dialog.CTS_label_Trk2.setText(f'小車 (人,機車,自行車) Set\nDefault : (10, 2, 0.1)\nCurrent : {conf.getTrk2_Set()}')
        self.CTS_dialog.CTS_trackingSetText2.setText('Ex : max_age=10, min_hits=2, iou_threshold=0.01, type `10,2,0.01`.')
        self.CTS_dialog.CTS_submitButton.setText('Submit')
        self.CTS_dialog.CTS_submitButton.clicked.connect(self.submitTrackingSet)

        self.CTS_dialog.show()
    @Slot()
    def submitTrackingSet(self):
        if self.CTS_dialog.CTS_Edit_1.text() != '':
            trk1 = self.CTS_dialog.CTS_Edit_1.text()
            print("Trackers1 Set Changed : ",trk1.replace(" ", ""))
            conf.setTrk1_Set(trk1)

        if self.CTS_dialog.CTS_Edit_2.text() != '':
            trk2 = self.CTS_dialog.CTS_Edit_2.text()        
            conf.setTrk2_Set(trk2)
            print("Trackers2 Set Changed : ",trk2.replace(" ", ""))

        self.CTS_dialog.close()
    @Slot()
    def changeSectionMode(self):
        if self.main_window.section == "intersection":
            self.main_window.section = "roadsection"
            conf.setSection_mode(self.main_window.section)
        elif self.main_window.section == "roadsection":
            self.main_window.section = "intersection"
            conf.setSection_mode(self.main_window.section)
        self.main_window._window.title.setText(str(conf.RTVersion()) + " | " + self.main_window.stabMode + " | " + self.main_window.yoloModel + " | " + self.main_window.section)
        if self.main_window.section == 'intersection':
            self.main_window._window.step5_btn.setText('[STEP 5] (I)\nDrawIO')
        elif self.main_window.section == 'roadsection':
            self.main_window._window.step5_btn.setText('[STEP 5] (R)\nDrawIO')
    @Slot()
    def changeOutputWH(self):
        self.WH_dialog = QDialog()
        ui_file_name = './View/WH_dialog.ui'
        file = QFile(ui_file_name)
        loader = QUiLoader()
        self.WH_dialog = loader.load(file)
        file.close()
        self.WH_dialog.setWindowTitle('Change output video width & height')
        self.WH_dialog.WH_Height.setText(f'{conf.getOutput_height()}')
        self.WH_dialog.WH_Width.setText(f'{conf.getOutput_width()}')
        self.WH_dialog.WH_ok_btn.clicked.connect(self.setOutputWH)
        self.WH_dialog.show()
    @Slot()
    def setOutputWH(self):
        if self.WH_dialog.WH_HeightEdit.text() != '':
            height = self.WH_dialog.WH_HeightEdit.text()
            conf.setOutput_height(height)
            print(f"output height change to : {height}")
        if self.WH_dialog.WH_WidthEdit.text() != '':
            width = self.WH_dialog.WH_WidthEdit.text()
            conf.setOutput_width(width) 
            print(f"output width change to : {width}")
        self.WH_dialog.WH_Height.setText(f'{conf.getOutput_height()}')
        self.WH_dialog.WH_Width.setText(f'{conf.getOutput_width()}')
    @Slot()
    def changeTIVsetting(self):        
        self.TIV_dialog = QDialog()
        ui_file_name = './View/TIV_dialog.ui'
        file = QFile(ui_file_name)
        loader = QUiLoader()
        self.TIV_dialog = loader.load(file)
        file.close()
        self.TIV_dialog.setWindowTitle('Change TIV Setting')
        self.TIV_dialog.TIV_IingoreFrames.setText(f'{conf.getTIV_ignoreFrame()}')
        self.TIV_dialog.TIV_ExtendPrintFrame.setText(f'{conf.getTIVP_ExtendPrintFrame()}')
        self.TIV_dialog.TIV_ok_btn.clicked.connect(self.setTIVSetting)
        self.TIV_dialog.show()
    @Slot()
    def setTIVSetting(self):
        if self.TIV_dialog.TIV_IingoreFramesEdit.text() != '':
            Iingore = self.TIV_dialog.TIV_IingoreFramesEdit.text()
            conf.setTIV_ignoreFrame(Iingore)
            print(f"TIV Iingore Frames change to : {Iingore}")
        if self.TIV_dialog.TIV_ExtendPrintFrameEdit.text() != '':
            ExtendPrintFrame = self.TIV_dialog.TIV_ExtendPrintFrameEdit.text()
            conf.setTIVP_ExtendPrintFrame(ExtendPrintFrame) 
            print(f"output width change to : {ExtendPrintFrame}")
        self.TIV_dialog.TIV_IingoreFrames.setText(f'{conf.getTIV_ignoreFrame()}')
        self.TIV_dialog.TIV_ExtendPrintFrame.setText(f'{conf.getTIVP_ExtendPrintFrame()}')
