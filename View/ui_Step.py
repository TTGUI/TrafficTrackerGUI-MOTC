from PySide2.QtCore import Slot, QProcess
from PySide2.QtWidgets import QFileDialog
import os
from .ui_BaseManager import BaseManager, ScheduleItem
from Cont import controller
from config import conf
from logs import logger

class StepManager(BaseManager):
    """本類別處理 Step 的文字、功能綁定、功能函數"""
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_windowmain_window = main_window
        
        self.initText()     # 初始化按鈕文字
        self.bind_buttons() # 綁定按鈕與槽

    def initText(self):
        self.main_window._window.DroneFolder_btn.setText('Set Drone Folder')
        self.main_window._window.openFolder_btn_2.setText('O\np\ne\nn')
        self.main_window._window.setResultFolder_btn.setText('Set Result Folder\n[./result/]')
        self.main_window._window.openFolder_btn.setText('O\np\ne\nn')
        self.main_window._window.step0_btn.setText('[STEP 0]\nVideo Cut Set')
        if self.main_window.stabMode == 'CPU':
            self.main_window._window.step1_btn.setText('[STEP 1] (C)\nStable')
        elif self.main_window.stabMode == 'GPU':
            self.main_window._window.step1_btn.setText('[STEP 1] (G)\nStable')
        self.main_window._window.step2_btn.setText('[STEP 2]\nYolo')
        self.main_window._window.step3_btn.setText('[STEP 3]\nTracking')
        self.main_window._window.step4_btn.setText('[STEP 4]\nBackground')
        if self.main_window.section == 'intersection':
            self.main_window._window.step5_btn.setText('[STEP 5] (I)\nDrawIO')
        elif self.main_window.section == 'roadsection':
            self.main_window._window.step5_btn.setText('[STEP 5] (R)\nDrawIO')
        self.main_window._window.step6_btn.setText('[STEP 6]\nIO Added')
        self.main_window._window.step7_btn.setText('[STEP 7]\nReplay')
        self.main_window._window.TIV_btn.setText("[STEP 8]\nTrackIntegrityVerification")
        if self.main_window.TIVPmode == 1:
            self.main_window._window.TIVPrinter_btn.setText('[STEP 9]\nTIV Printer (V)')
        elif self.main_window.TIVPmode == 2:
            self.main_window._window.TIVPrinter_btn.setText('[STEP 9]\nTIV Printer (I)')
        elif self.main_window.TIVPmode == 3:
            self.main_window._window.TIVPrinter_btn.setText('[STEP 9]\nTIV Printer (R)')
        self.main_window._window.show_btn.setText('Show')
        self.main_window._window.show_btn.setToolTip('[S1,3,7] Show process frame or background.')
        self.main_window._window.DisplayType_btn.setText('Display ID')
        self.main_window._window.DisplayType_btn.setToolTip('[S7,9] Show tracking ID or not.')
        self.main_window._window.showTracking_btn.setText('Show Tracking')
        self.main_window._window.showTracking_btn.setToolTip('[S9] Show tracking info or not.')
        self.main_window._window.ActionName_btn.setText('Edit Action Name\n[]')
        self.main_window._window.selectName_btn.setText('Select Action Name from File')
        
    def bind_buttons(self):
        self.main_window._window.DroneFolder_btn.clicked.connect(self.droneFolder)
        self.main_window._window.openFolder_btn_2.clicked.connect(self.openDroneFolder)
        self.main_window._window.setResultFolder_btn.clicked.connect(self.setResultFolder)
        self.main_window._window.openFolder_btn.clicked.connect(self.openResultFolder)
        self.main_window._window.step0_btn.clicked.connect(self.step0)
        self.main_window._window.step1_btn.clicked.connect(self.step1)
        self.main_window._window.step2_btn.clicked.connect(self.step2)
        self.main_window._window.step3_btn.clicked.connect(self.step3)
        self.main_window._window.step4_btn.clicked.connect(self.step4)
        self.main_window._window.step5_btn.clicked.connect(self.step5)        
        self.main_window._window.step6_btn.clicked.connect(self.step6)
        self.main_window._window.step7_btn.clicked.connect(self.step7)
        self.main_window._window.TIV_btn.clicked.connect(self.step8_singleTIV)
        self.main_window._window.TIVPrinter_btn.clicked.connect(self.step9_TIVPrinter)
        self.main_window._window.show_btn.clicked.connect(self.show_btn_act)
        self.main_window._window.DisplayType_btn.clicked.connect(self.changeDisplayType)
        self.main_window._window.showTracking_btn.clicked.connect(self.showTracking)
        self.main_window._window.ActionName_btn.clicked.connect(self.changeActionName)
        self.main_window._window.selectName_btn.clicked.connect(self.selectName)
    Slot()
    def droneFolder(self):
        folderpath = QFileDialog.getExistingDirectory(self.main_window._window, 'Select Folder of Drone Video', self.main_window.resultPath)
        if folderpath == "" :
            print("[CANCEL] Set Drone Folder Cancel.")
        else :
            flist = os.listdir(folderpath)
            if len(flist) == 0:
                print("<< Warinig : Your Drone Folder Has NO VIDEOS.")
            else:
                self.main_window.actionName = flist[0]
                self.main_window._window.ActionName_edit.setText(self.main_window.actionName)

            self.main_window.droneFolderPath = folderpath
            self.setDroneFolderBtnText()
            logger.info(f"[Set droneFolder] ->> {self.main_window.droneFolderPath}")
            self.changeActionName()
    Slot()
    def setDroneFolderBtnText(self):
        out = ""
        counter = 0
        for i in range(0,len(self.main_window.droneFolderPath)):
            out = out + self.main_window.droneFolderPath[i]
            counter = counter + 1
            if counter == 40 :
                out = out + '\n'
                counter = 0

        self.main_window._window.DroneFolder_btn.setText('Set Drone Folder\n['+ out +']')
    Slot()
    def openDroneFolder(self):
        if os.path.isdir(self.main_window.droneFolderPath) :
            if os.name == 'nt' :
                QProcess.startDetached('explorer', [os.path.normpath(self.main_window.droneFolderPath)])
            else :
                subprocess.call(['xdg-open', os.path.normpath(self.main_window.droneFolderPath)])
        else :
            print("<< Warinig : Your Result Folder is not exist.")
    Slot()
    def setResultFolder(self):
        temp = QFileDialog.getExistingDirectory(self.main_window._window, 'Select Folder to Result.', self.main_window.resultPath)
    
        if not temp:
            print("[CANCEL] Set Result Folder Cancel.")
        else:
            # Ensure there is a trailing separator
            self.main_window.resultPath = os.path.join(temp, '')
            self.main_window.setResultFolderBtnText()
            logger.info(f"[Set resultFolder] ->> {self.main_window.resultPath}")
            self.changeActionName()
    Slot()           
    def setResultFolderBtnText(self):
        out = ""
        counter = 0
        for i in range(0,len(self.main_window.resultPath)):
            out = out + self.main_window.resultPath[i]
            counter = counter + 1
            if counter == 40 :
                out = out + '\n'
                counter = 0

        self.main_window._window.setResultFolder_btn.setText('Set Result Folder\n['+ out +']')
    Slot()      
    def openResultFolder(self):
        if os.path.isdir(self.main_window.resultPath):
            normalized_path = os.path.normpath(self.main_window.resultPath)
            if os.name == 'nt':
                QProcess.startDetached('explorer', [normalized_path])
            else:
                QProcess.startDetached('xdg-open', [normalized_path])
        else:
            print("<< Warning: Your Result Folder does not exist.")
    Slot()
    def changeActionName(self) : # user odering actionName.

        self.main_window.actionName = self.main_window._window.ActionName_edit.text()

        self.main_window.cutinfo_txt = self.main_window.resultPath + self.main_window.actionName + "_cutInfo.txt"
        self.main_window.stab_input = self.main_window.droneFolderPath
        self.main_window.stab_output = self.main_window.resultPath + self.main_window.actionName + "_stab.avi"
        self.main_window.stab_video = self.main_window.stab_output
        self.main_window.yolo_txt = self.main_window.resultPath+ self.main_window.actionName +"_stab_8cls.txt"
        self.main_window.tracking_csv = self.main_window.resultPath + self.main_window.actionName + ".csv"
        self.main_window.gateLineIO_txt = self.main_window.resultPath + self.main_window.actionName + "_IO.txt"
        self.main_window.gate_tracking_csv = self.main_window.resultPath + self.main_window.actionName + "_gate.csv"
        self.main_window.result_video = self.main_window.resultPath + self.main_window.actionName + "_result.avi"
        self.main_window.background_img = self.main_window.resultPath+ self.main_window.actionName +"_background.jpg"
        self.main_window.singelTIVpath = self.main_window.resultPath + self.main_window.actionName + "_TIV.csv"

        self.setActionNameBtnText()

        logger.info(f"[ChangeActionName] ->> <{self.main_window.actionName}>")
    Slot()
    def setActionNameBtnText(self):
        out = ""
        counter = 0
        for i in range(0,len(self.main_window.actionName)):
            out = out + self.main_window.actionName[i]
            counter = counter + 1
            if counter == 23 :
                out = out + '\n'
                counter = 0

        self.main_window._window.ActionName_btn.setText("Edit Action Name\n[" + out + ']')
    Slot()
    def selectName(self):
        actName = QFileDialog.getOpenFileName(self.main_window._window, 'Select file to set Action Name', self.main_window.resultPath)

        tempName = actName[0]
        if tempName == "" :
            print("[CANCEL] Select Action Name Cancel.")
        else :
            tempName = self.RT_actionNameWhitoutBackword(tempName)

            self.main_window._window.ActionName_edit.setText(os.path.basename(tempName))
            self.changeActionName()
    def RT_actionNameWhitoutBackword(self, inputAname) :
        tempName = inputAname
        backword = ["_gate.csv", "_TIV.csv", ".csv", "_background.jpg", "_cutInfo.txt", "_IO.txt", "_result.avi", "_result.mp4", "_stab.avi", "_stab.mp4", "_stab_8cls.txt" ]
        for i in range(0,len(backword)):
            backLen = -len(backword[i])
            if tempName[backLen:] == backword[i] :
                tempName = tempName[0:backLen]
        return tempName     
    Slot()
    def step0(self):
        self.changeStep(0)
        if self.main_window.scheduleType == 'edit' :
            print("Current Schedule Item Step >> 0 ")            
            self.AddScheudle()
        elif self.precursorCheck():
                self.main_window.currentEndID = -1
                self.main_window.currentStartID = len(os.listdir(self.main_window.droneFolderPath))

                self.main_window.PlayerManager.set_video(1)
                self.main_window.PlayerManager.play()
    Slot()
    def step1(self):
        self.changeStep(1)
        if self.main_window.scheduleType == 'edit' :
            print("Current Schedule Item Step >> 1 ")            
            self.AddScheudle()
        else :
            if self.precursorCheck():
                controller.con_step1(self.main_window.stab_input, 
                                     self.main_window.stab_output, 
                                     self.main_window.show, 
                                     self.main_window.cutinfo_txt, 
                                     self.main_window.stabMode, 
                                     self.main_window.PlayerManager.qtFrameDisplay)
    Slot()
    def step2(self): # Yolo
        self.changeStep(2)
        if self.main_window.scheduleType == 'edit' :
            print("Current Schedule Item Step >> 2 ")            
            self.AddScheudle()
        else :
            if self.precursorCheck():
                controller.con_step2(self.main_window.stab_video, 
                                     self.main_window.yolo_txt, 
                                     self.main_window.yoloModel )
    Slot()
    def step3(self): # Tracking
        self.changeStep(3)
        if self.main_window.scheduleType == 'edit' :
            print("Current Schedule Item Step >> 3 ")
            self.AddScheudle()
        else :
            if self.precursorCheck():
                controller.con_step3(self.main_window.yolo_txt,
                                     self.main_window.tracking_csv,
                                     self.main_window.show, 
                                     self.main_window.PlayerManager.qtFrameDisplay, 
                                     conf.getTrk1_Set(), 
                                     conf.getTrk2_Set(),
                                     self.main_window.stab_video)
    Slot()
    def step4(self): # BackGround
        self.changeStep(4)
        if self.main_window.scheduleType == 'edit' :
            print("Current Schedule Item Step >> 4 ")            
            self.AddScheudle()
        else :
            if self.precursorCheck():
                controller.con_step4(self.main_window.stab_video, 
                                     self.main_window.background_img, 
                                     self.main_window.PlayerManager.qtFrameDisplay)
    Slot()
    def step5(self): # DrawIO
        self.changeStep(5)
        if self.main_window.scheduleType == 'edit' :
            print("Current Schedule Item Step >> 5 ")            
            self.AddScheudle()
        else :  
            if self.precursorCheck():
                controller.con_step5(self.main_window.gateLineIO_txt, self.main_window.background_img)
    Slot()
    def step6(self): # IO added
        self.changeStep(6)
        if self.main_window.scheduleType == 'edit' :
            print("Current Schedule Item Step >> 6 ")            
            self.AddScheudle()
        else :
            if self.precursorCheck():    
                controller.con_step6(self.main_window.gateLineIO_txt, 
                                     self.main_window.tracking_csv, 
                                     self.main_window.gate_tracking_csv)
    Slot()
    def step7(self): # Replay
        self.changeStep(7)
        if self.main_window.scheduleType == 'edit' :
            print("Current Schedule Item Step >> 7 ")            
            self.AddScheudle()
        else :
            if self.precursorCheck():
                controller.con_step7(self.main_window.stab_video, 
                                     self.main_window.result_video, 
                                     self.main_window.gate_tracking_csv, 
                                     self.main_window.gateLineIO_txt, 
                                     self.main_window.displayType, 
                                     self.main_window.show, 
                                     self.main_window.PlayerManager.qtFrameDisplay)
    Slot()
    def step8_singleTIV(self):
        self.changeStep(8)
        if self.main_window.scheduleType == 'edit' :
            print("Current Schedule Item Step >> TIV ")            
            self.AddScheudle()
        elif self.precursorCheck():
                return controller.con_TIVT(self.main_window.gate_tracking_csv, self.main_window.singelTIVpath)
    Slot()  
    def step9_TIVPrinter(self):
        self.changeStep(9)
        if self.main_window.scheduleType == 'edit' :
            print("Current Schedule Item Step >> TIVPrinter ")
            self.AddScheudle()
        else :
            if self.main_window.TIVPmode == 3 and self.precursorCheck():
                    print("[STEP 9 - TIVP-R]")
                    def read_file(file_name):
                        with open(file_name, 'r') as f:
                            lines = f.readlines()
                        return lines
                    
                    self.main_window.currentTIVP8cls = read_file(self.main_window.yolo_txt)
                    self.main_window.ScheduleManager.TIVfileLoad()
            elif self.precursorCheck():
                    controller.con_TIVP(self.main_window.singelTIVpath, 
                                        self.main_window.gateLineIO_txt, 
                                        self.main_window.stab_video, 
                                        self.main_window.resultPath, 
                                        self.main_window.actionName, 
                                        self.main_window.gate_tracking_csv, 
                                        self.main_window.background_img )  
    Slot()  
    def AddScheudle(self):
        tempItem = ScheduleItem()
        tempItem.DisplayID = self.main_window.displayType 
        tempItem.Show = self.main_window.show         
        tempItem.actionName = self.main_window.actionName
        tempItem.resultPath = self.main_window.resultPath
        tempItem.droneFolderPath = self.main_window.droneFolderPath
        tempItem.step = self.main_window.currentStep
        self.main_window.ScheduleList.insert(self.main_window.currentScheduleIndex +1, tempItem)
        if len(self.main_window.ScheduleList) == 1 :
            self.main_window.currentScheduleIndex = 0
        else :
            self.main_window.currentScheduleIndex = self.main_window.currentScheduleIndex +1

        self.displayInfo(3)
        
        
        print("AddSchedule "+ str(self.main_window.currentScheduleIndex+1) +" : [Step "+str(tempItem.step) + "] - [" + tempItem.actionName +"]")
    Slot()
    def changeStep(self, sp):
        self.main_window.currentStep = sp
        self.renewScheduleBoard()
    Slot()
    def show_btn_act(self):
        if self.main_window.scheduleType == 'off' and self.main_window.TIVPmode == 3 and self.main_window.currentStep == 9 : # TIVP real time mode edit by user.
            self.main_window._window.show_btn.setToolTip('[S9] Show yolo detect.')
        else:
            self.main_window._window.show_btn.setToolTip('[S1,3,7] Show process frame or background.')

        if self.main_window.show:
            self.main_window.show = False
            if self.main_window.scheduleType == 'off' and self.main_window.TIVPmode == 3 and self.main_window.currentStep == 9 : # TIVP real time mode edit by user.
                self.main_window._window.show_btn.setText('Hide Yolo detact.')
            else:
                self.main_window._window.show_btn.setText('BackGround')

        else :
            self.main_window.show = True
            if self.main_window.scheduleType == 'off' and self.main_window.TIVPmode == 3 and self.main_window.currentStep == 9 : # TIVP real time mode edit by user.
                self.main_window._window.show_btn.setText('Display Yolo detact.')
            else:
                self.main_window._window.show_btn.setText('Show')
        if self.main_window.scheduleType == 'off' and self.main_window.TIVPmode == 3 and self.main_window.currentStep == 9 and self.main_window.PlayerManager.capReadRet :
            tempFrame = self.main_window.PlayerManager.capFrame.copy()
            self.main_window.PlayerManager.frameDisplay(tempFrame)
    Slot()
    def changeDisplayType(self) :

        if self.main_window.displayType:
            self.main_window.displayType = False
            self.main_window._window.DisplayType_btn.setText('Hide ID')

        else :
            self.main_window.displayType = True
            self.main_window._window.DisplayType_btn.setText('Display ID')
        if self.main_window.scheduleType == 'off' and self.main_window.TIVPmode == 3 and self.main_window.currentStep == 9 and self.main_window.PlayerManager.capReadRet :
            tempFrame = self.main_window.PlayerManager.capFrame.copy()
            self.main_window.PlayerManager.frameDisplay(tempFrame)
    Slot()
    def showTracking(self):
        if self.main_window.showTrackingBool :
            self.main_window.showTrackingBool = False
            self.main_window._window.showTracking_btn.setText('Hide Tracking')

        else :
            self.main_window.showTrackingBool = True
            self.main_window._window.showTracking_btn.setText('Show Tracking')
        if self.main_window.scheduleType == 'off' and self.main_window.TIVPmode == 3 and self.main_window.currentStep == 9 and self.main_window.PlayerManager.capReadRet :
            tempFrame = self.main_window.PlayerManager.capFrame.copy()
            self.main_window.PlayerManager.frameDisplay(tempFrame)





