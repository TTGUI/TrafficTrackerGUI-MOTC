from PySide2.QtCore import Slot
from PySide2.QtWidgets import QFileDialog
import os
from config import conf
from logs import logger
from .ui_BaseManager import BaseManager, ScheduleItem
from Model.tool import TrackIntegrityVerificationTool

class ScheduleManager(BaseManager):
    """本類別處理 Schedule 的文字、功能綁定、功能函數"""
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        
        self.initText()     # 初始化按鈕文字
        self.bind_buttons() # 綁定按鈕與槽
        
    def initText(self):
        self.main_window._window.ScheduleMode_btn.setText('Schedule Mode <OFF>')
        self.main_window._window.StartSchedule_btn.setText('Start Schedule')
        self.main_window._window.GetSchedule_btn.setText('Get Schedule')
        self.main_window._window.GetSchedule_btn.setToolTip('Load current schedule item\nto workspace setting.')
        self.main_window._window.SetSchedule_btn.setText('Set Schedule')
        self.main_window._window.SetSchedule_btn.setToolTip('Replace current schedule item\nwith workspace setting.')
        self.main_window._window.DeleteSchedule_btn.setText('Delete Schedule')
        self.main_window._window.DeleteSchedule_btn.setToolTip('Delete current schedule item.')
        self.main_window._window.LoadScheduleFile_btn.setText('Load Schedule File')
        self.main_window._window.SaveScheduleFile_btn.setText('Save Schedule File')

    def bind_buttons(self):
        self.main_window._window.ScheduleMode_btn.clicked.connect(self.ScheduleMode)
        self.main_window._window.StartSchedule_btn.clicked.connect(self.StartSchedule)
        self.main_window._window.GetSchedule_btn.clicked.connect(self.GetSchedule)
        self.main_window._window.SetSchedule_btn.clicked.connect(self.SetSchedule)
        self.main_window._window.DeleteSchedule_btn.clicked.connect(self.DeleteSchedule)
        self.main_window._window.LoadScheduleFile_btn.clicked.connect(self.loadSchedule)
        self.main_window._window.SaveScheduleFile_btn.clicked.connect(self.saveSchedule)

    Slot()
    def ScheduleMode(self):
        if self.main_window.scheduleType == 'edit' :
            self.main_window.scheduleType = 'off'
            self.main_window._window.ScheduleMode_btn.setText('Schedule Mode <OFF>')
            self.set_button_text_color(self.main_window._window.ScheduleMode_btn, "block")
        else:
            self.main_window.scheduleType = 'edit'
            self.main_window._window.ScheduleMode_btn.setText('Schedule Mode <EDIT>')
            self.set_button_text_color(self.main_window._window.ScheduleMode_btn, "blue")
        self.renewScheduleBoard()
    Slot()
    def StartSchedule(self):
        self.main_window.scheduleType = 'run'
        self.main_window._window.ScheduleMode_btn.setText('Schedule Mode <RUN>')
        cuurentTIVT = TrackIntegrityVerificationTool.TIVT()
        ScheduTIVList = []
        ScheduTIVList.append(cuurentTIVT.retTitle())
        logger.info(f"[Start Schedule][{self.main_window.scheduleName}]")

        for i in range(self.main_window.currentScheduleIndex ,len(self.main_window.ScheduleList)):
            self.main_window.currentScheduleIndex = i
            self.displayInfo(3)

            sch = '==================[Schedule ' + str(i+1) +' / ' + str(len(self.main_window.ScheduleList))+' ]'
            self.main_window.displayType = self.main_window.ScheduleList[i].DisplayID
            self.main_window.show = self.main_window.ScheduleList[i].Show
            
            self.main_window.actionName = self.main_window.ScheduleList[i].actionName
            self.main_window.resultPath = self.main_window.ScheduleList[i].resultPath
            self.main_window.droneFolderPath = self.main_window.ScheduleList[i].droneFolderPath
            self.flashActionName()

            if self.main_window.ScheduleList[i].step == 0:
                logger.info(sch + " - [STEP 0]==================")
                self.main_window.StepManager.step0()
                return
            elif self.main_window.ScheduleList[i].step == 1:
                logger.info(sch + " - [STEP 1]==================")
                self.main_window.StepManager.step1()
            elif self.main_window.ScheduleList[i].step == 2:
                logger.info(sch + " - [STEP 2]==================")
                self.main_window.StepManager.step2()
            elif self.main_window.ScheduleList[i].step == 3:
                logger.info(sch + " - [STEP 3]==================")
                self.main_window.StepManager.step3()                
            elif self.main_window.ScheduleList[i].step == 4:
                logger.info(sch + " - [STEP 4]==================")
                self.main_window.StepManager.step4()                
            elif self.main_window.ScheduleList[i].step == 5:
                logger.info(sch + " - [STEP 5]==================")
                self.main_window.StepManager.step5()
            elif self.main_window.ScheduleList[i].step == 6:
                logger.info(sch + " - [STEP 6]==================")
                self.main_window.StepManager.step6()
            elif self.main_window.ScheduleList[i].step == 7:
                logger.info(sch + " - [STEP 7]==================")
                self.main_window.StepManager.step7()
            elif self.main_window.ScheduleList[i].step == 8:
                logger.info(sch + " - [STEP 8 - TIV]==================")
                self.main_window.StepManager.step8_singleTIV()
            elif self.main_window.ScheduleList[i].step == 9:
                logger.info(sch + " - [STEP 9 - TIVP]==================")
                self.main_window.StepManager.step9_TIVPrinter()
        
        if self.main_window.scheduleTIVFolderPath == "" :
            self.main_window.scheduleTIVFile = "./result/" + "/" + self.main_window.scheduleName + "_TIV.csv"
        else :
            self.main_window.scheduleTIVFile = self.main_window.scheduleTIVFolderPath + "/" + self.main_window.scheduleName + "_TIV.csv"

        base, extension = os.path.splitext(self.main_window.scheduleTIVFile)
        k = 0
        while os.path.exists(self.main_window.scheduleTIVFile):
            k += 1
            self.main_window.scheduleTIVFile = f"{base}_{k}{extension}"

        fp = open( self.main_window.scheduleTIVFile, "w")

        for i in range (0,len(ScheduTIVList)):
            fp.write(ScheduTIVList[i])
            fp.write("\n")
        fp.close()

        print ("ALL Schedule Done.")

        self.main_window.scheduleType = 'off'
        self.main_window._window.ScheduleMode_btn.setText('Schedule Mode <OFF>')
    Slot()
    def GetSchedule(self):
        self.loadCurrentScheduleItem()
    Slot()
    def loadCurrentScheduleItem(self):
        self.main_window.actionName = self.main_window.ScheduleList[self.main_window.currentScheduleIndex].actionName
        self.main_window.resultPath = self.main_window.ScheduleList[self.main_window.currentScheduleIndex].resultPath
        self.main_window.droneFolderPath = self.main_window.ScheduleList[self.main_window.currentScheduleIndex].droneFolderPath
        self.main_window.show = self.main_window.ScheduleList[self.main_window.currentScheduleIndex].Show
        self.main_window.displayType = self.main_window.ScheduleList[self.main_window.currentScheduleIndex].DisplayID

        if self.main_window.show:
            self.main_window._window.show_btn.setText('Show')
        else :
            self.main_window._window.show_btn.setText('BackGround')
        if self.main_window.displayType:
            self.main_window._window.DisplayType_btn.setText('Display ID')
        else :
            self.main_window._window.DisplayType_btn.setText('Hide ID')
        self.flashActionName()
    Slot()
    def SetSchedule(self):
        tempItem = ScheduleItem()
        tempItem.DisplayID = self.main_window.displayType 
        tempItem.Show = self.main_window.show 
        
        tempItem.actionName = self.main_window.actionName
        tempItem.resultPath = self.main_window.resultPath
        tempItem.droneFolderPath = self.main_window.droneFolderPath
        tempItem.step = self.main_window.currentStep
        self.main_window.ScheduleList[self.main_window.currentScheduleIndex] = tempItem
        self.displayInfo(3)
    Slot()
    def DeleteSchedule(self):
        if self.main_window.scheduleType == 'off' and self.main_window.TIVPmode == 3 : # TIVP real time mode edit by user.
            if len(self.main_window.TIVIsampleList) > 0 :
                self.main_window.TIVIsampleList.pop(self.main_window.currentIssueIndex)
                if self.main_window.currentIssueIndex > 0:
                    self.main_window.currentIssueIndex = self.main_window.currentIssueIndex -1
                self.displayInfo(4)
        else :                                                 # Schedule edit mode.
            if len(self.main_window.ScheduleList) > 0 :
                self.main_window.ScheduleList.pop(self.main_window.currentScheduleIndex)
                if self.main_window.currentScheduleIndex > 0:
                    self.main_window.currentScheduleIndex = self.main_window.currentScheduleIndex -1
                self.displayInfo(3)
    Slot()
    def loadSchedule(self):
        if self.main_window.scheduleType == 'off' and self.main_window.TIVPmode == 3 and self.main_window.currentStep == 9:     # Load TIVP Issue
            self.loadTIVIssue()
        else:                                                                               # Normal Schedule Load
            self.main_window.scheduleLoadPath, filetype = QFileDialog.getOpenFileName(self.main_window._window,"Select Schedule File.", self.main_window.resultPath)
            
            if not self.main_window.scheduleLoadPath :
                print ("[Cancel] Schedule Load Cancel.")
            else:
                print ("Load Schedule File : " + self.main_window.scheduleLoadPath)
                self.main_window.scheduleName = self.main_window.scheduleLoadPath.split("/")[-1][:-13]
                self.main_window.scheduleTIVFolderPath = os.path.dirname(self.main_window.scheduleLoadPath)
                self.readScheduleFile()
                self.main_window.scheduleType = 'edit'
                self.set_button_text_color(self.main_window._window.ScheduleMode_btn, "blue")
                self.main_window._window.ScheduleMode_btn.setText('Schedule Mode <EDIT>')
                self.loadCurrentScheduleItem()
                self.displayInfo(3)
                self.renewScheduleBoard()

    def readScheduleFile(self):
        def encodeFile():
            encodings = ['utf-8', 'cp950']
            for e in encodings:
                try:
                    with open(self.main_window.scheduleLoadPath, 'r', encoding=e) as f:
                        return f.readlines()
                except UnicodeDecodeError:
                    pass
            print(f'Could not read {self.main_window.scheduleLoadPath} with any encoding.')
            return None
        # f = open(self.main_window.scheduleLoadPath, 'r', encoding='utf-8')
        lineData = encodeFile()
        self.main_window.ScheduleList = []

        for i in range(0, len(lineData)) :
            tempSchedule = ScheduleItem()
            counter = 0
            tempIndex = ""

            for c in range(0,len(lineData[i])):
                char = lineData[i][c]
                if char == '\t' or char == '\n':
                    if counter == 0 : # Step
                        tempSchedule.step = int(tempIndex)
                    elif counter == 1 : # Display Boolen
                        if tempIndex == '1':
                            tempSchedule.DisplayID = True
                        else :
                            tempSchedule.DisplayID = False
                    elif counter == 2 : # Show Boolen
                        if tempIndex == '1':
                            tempSchedule.Show = True
                        else :
                            tempSchedule.Show = False
                    elif counter == 3 : # actionName
                        tempSchedule.actionName = tempIndex
                    elif counter == 4 : # resultPath
                        tempSchedule.resultPath = tempIndex
                    elif counter == 5 : # droneFolderPath
                        tempSchedule.droneFolderPath = tempIndex
                             
                    counter = counter + 1
                    tempIndex = ""
                else:
                    tempIndex = tempIndex + char

            self.main_window.ScheduleList.append(tempSchedule)
    Slot()
    def saveSchedule(self):
        if self.main_window.scheduleType == 'off' and self.main_window.TIVPmode == 3 and self.main_window.currentStep == 9:     # Save TIVP Issue
            self.saveTIVIssue()
        else:                                                                               # Normal Schedule Save
            filetype = ("_Schedule.txt")
            temp = QFileDialog.getSaveFileName(self.main_window._window,"Save Schedule File.", "", filetype)
            if temp[0] != "":
                self.main_window.scheduleSavePath = temp[0] + temp[1]
                self.main_window.scheduleName = temp[0].split("/")[-1]
                self.writeScheduleFile()
                print ("Save Schedule File : " + self.main_window.scheduleSavePath)
                self.main_window.scheduleTIVFolderPath = os.path.dirname(self.main_window.scheduleSavePath)
                self.displayInfo(3)
            else :
                print ("[Cancel] Schedule Save Cancel.")

    def writeScheduleFile(self):
        for i in range(0, len(self.main_window.ScheduleList)):
            f = open(self.main_window.scheduleSavePath, 'w', encoding='utf-8')

            for i in range(0,len(self.main_window.ScheduleList)) :
                if self.main_window.ScheduleList[i].DisplayID:
                    display = 1
                else:
                    display = 0

                if self.main_window.ScheduleList[i].Show:
                    show = 1
                else :
                    show = 0

                out = ''
                out = out + str(self.main_window.ScheduleList[i].step) + '\t'
                out = out + str(display) + '\t'
                out = out + str(show) + '\t'
                out = out + self.main_window.ScheduleList[i].actionName + '\t'
                out = out + self.main_window.ScheduleList[i].resultPath + '\t'
                out = out + self.main_window.ScheduleList[i].droneFolderPath + '\n'
                
                f.write(out)
            f.close()
    Slot()
    def loadTIVIssue(self):
        self.main_window.singelTIVpath, filetype = QFileDialog.getOpenFileName(self.main_window._window,"Select TIV.csv.", self.main_window.resultPath )

        if not self.main_window.singelTIVpath :
            print ("[Cancel] TIV Load Cancel.")
        else:
            print ("Load TIV File : " + self.main_window.singelTIVpath)        
            
            self.renewScheduleBoard()
            self.main_window.resultPath = os.path.dirname(self.main_window.singelTIVpath) + '/'
            self.TIVfileLoad()           # 再Loda TIV
            self.displayInfo(4)
    Slot()
    def TIVfileLoad(self):
        self.main_window.show = False
        if self.main_window.scheduleType == 'off' and self.main_window.TIVPmode == 3 and self.main_window.currentStep == 9 : # TIVP real time mode edit by user.
            self.main_window._window.show_btn.setToolTip('[S9] Show yolo detect.')
        else:
            self.main_window._window.show_btn.setToolTip('[S1,3,7] Show process frame or background.')
        self.main_window._window.show_btn.setText('Hide Yolo detact.')
        self.main_window.PlayerManager.set_video(2) # Step 9 TIVP Real Time Mode
        self.main_window.currentIssueIndex = 0
        f = open(self.main_window.singelTIVpath, 'r', encoding='utf-8')
        tivLines = f.readlines()
        f.close()

        self.main_window.TIVIsampleList = []
        index = 0 
        while index < len(tivLines) and tivLines[index] != "SameIOCar\n" :
            index += 1

        index += 1
        while index < len(tivLines) and tivLines[index] != "SameIOMotor\n" :
            self.main_window.TIVIsampleList.append(tivLines[index])
            index += 1

        index += 1
        while index < len(tivLines) and tivLines[index] != "UserOrder\n" :
            self.main_window.TIVIsampleList.append(tivLines[index])
            index += 1

        index += 1
        while index < len(tivLines) :
            self.main_window.TIVIsampleList.append(tivLines[index])
            index += 1

        fio = open(self.main_window.gateLineIO_txt, 'r')
        self.main_window.TIVioLines = fio.readlines()
        fio.close()

        fp = open(self.main_window.gate_tracking_csv, "r") 
        
        lines = fp.readlines()
        fp.close()
        self.main_window.PlayerManager.V = []
        for j in range(0, len(lines)):
            self.main_window.PlayerManager.V.append([])
            T = lines[j].split(",")
            for k in range(0, len(T)):
                self.main_window.PlayerManager.V[j].append(T[k])

        self.displayInfo(4)
    Slot()
    def saveTIVIssue(self):
        filetype = ("_TIV.csv")
        temp = QFileDialog.getSaveFileName(self.main_window._window,"Save TIV File.", "", filetype)
        if temp[0] != "":
            outputTIV = temp[0] + temp[1]

            r = open(self.main_window.singelTIVpath, 'r', encoding='utf-8')

            ORtiv = r.readlines()
            r.close()
            f = open(outputTIV, 'w', encoding='utf-8')
            f.write(ORtiv[0])
            f.write(ORtiv[1])
            
            index = 0
            SameIOCarID = []
            SameIOMotorID = []
            while index < len(ORtiv) and ORtiv[index] != "SameIOCar\n" :
                index += 1

            index += 1
            while index < len(ORtiv) and ORtiv[index] != "SameIOMotor\n" :
                SameIOCarID.append(ORtiv[index].split(',')[0])
                index += 1

            index += 1
            while index < len(ORtiv) :
                SameIOMotorID.append(ORtiv[index].split(',')[0])
                index += 1

            f.write("SameIOCar\n")
            for i in range(0, len(self.main_window.TIVIsampleList)):
                if (self.main_window.TIVIsampleList[i].split(',')[0] in SameIOCarID) :
                    out = self.main_window.TIVIsampleList[i]
                    f.write(out)
            f.write("SameIOMotor\n")
            for i in range(0, len(self.main_window.TIVIsampleList)):
                if (self.main_window.TIVIsampleList[i].split(',')[0] in SameIOMotorID) :
                    out = self.main_window.TIVIsampleList[i]
                    f.write(out)
            f.write("UserOrder\n")
            for i in range(0, len(self.main_window.TIVIsampleList)):
                if (self.main_window.TIVIsampleList[i].split(',')[0] not in SameIOCarID) and (self.main_window.TIVIsampleList[i].split(',')[0] not in SameIOMotorID) :
                    out = self.main_window.TIVIsampleList[i]
                    f.write(out)
                    f.write("\n")

            f.close()
            print ("Save TIV File : " + outputTIV)
            self.displayInfo(4)
        else :
            print ("[Cancel] TIV Save Cancel.")

