from PySide2.QtCore import QObject, QTimer
from PySide2.QtWidgets import QMessageBox
from PySide2.QtGui import QPalette, QColor
from pathlib import Path
import os
import cv2
from logs import logger

class BaseManager(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def renewScheduleBoard(self):
        if self.main_window.scheduleType == 'off' and self.main_window.TIVPmode == 3 and self.main_window.currentStep == 9:
            self.main_window._window.DeleteSchedule_btn.setText('Delete TIV Issue')
            self.main_window._window.LoadScheduleFile_btn.setText('Load TIV File')
            self.main_window._window.SaveScheduleFile_btn.setText('Save TIV File')
            chColor2 = "blue"
        else:
            self.main_window._window.DeleteSchedule_btn.setText('Delete Schedule')
            self.main_window._window.LoadScheduleFile_btn.setText('Load Schedule File')
            self.main_window._window.SaveScheduleFile_btn.setText('Save Schedule File')
            chColor2 = "black"

        self.set_button_text_color(self.main_window._window.SaveScheduleFile_btn, chColor2)
        self.set_button_text_color(self.main_window._window.LoadScheduleFile_btn, chColor2)
        self.set_button_text_color(self.main_window._window.DeleteSchedule_btn, chColor2)
        self.set_button_text_color(self.main_window._window.show_btn, chColor2)
        self.set_button_text_color(self.main_window._window.DisplayType_btn, chColor2)
        self.set_button_text_color(self.main_window._window.showTracking_btn, chColor2)
        self.set_button_text_color(self.main_window._window.play_btn, chColor2)
        self.set_button_text_color(self.main_window._window.pause_btn, chColor2)
        self.set_button_text_color(self.main_window._window.jump_btn, chColor2)

        chColor = "blue" if self.main_window.scheduleType == 'edit' else "black"
        self.set_button_text_color(self.main_window._window.step0_btn, chColor)
        self.set_button_text_color(self.main_window._window.step1_btn, chColor)
        self.set_button_text_color(self.main_window._window.step2_btn, chColor)
        self.set_button_text_color(self.main_window._window.step3_btn, chColor)
        self.set_button_text_color(self.main_window._window.step4_btn, chColor)
        self.set_button_text_color(self.main_window._window.step5_btn, chColor)
        self.set_button_text_color(self.main_window._window.step6_btn, chColor)
        self.set_button_text_color(self.main_window._window.step7_btn, chColor)
        self.set_button_text_color(self.main_window._window.TIV_btn, chColor)
        self.set_button_text_color(self.main_window._window.TIVPrinter_btn, chColor)

    def flashActionName(self) : # program change actionName itself.
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
        self.setDroneFolderBtnText()
        self.setResultFolderBtnText()

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

    def displayInfo(self, type):

        if type == 1:  # display Step 0 CutInfo with pagination
            # 計算當前頁面
            self.page = int(self.main_window.currentVideoIndex / self.main_window.pageLen)
            pageStart = self.page * self.main_window.pageLen

            # 確定當前頁面的結束索引
            if (self.page + 1) * self.main_window.pageLen > self.main_window.videoLen:
                pageEnd = self.main_window.videoLen
            else:
                pageEnd = (self.page + 1) * self.main_window.pageLen

            out = '\tCutInfo  ( ' + str(self.main_window.currentVideoIndex + 1) + ' / ' + str(self.main_window.videoLen) + ' )\n'
            out += f"Page {self.page + 1}/{(self.main_window.videoLen - 1) // self.main_window.pageLen + 1}\n"  # 添加頁數顯示

            # 遍歷當前頁面範圍內的內容
            for i in range(pageStart, pageEnd):
                if i == self.main_window.currentVideoIndex:
                    out = out + "=>"
                else:
                    out = out + "    "
                out = out + "[" + str(i + 1) + ']'
                out = out + str(self.main_window.cutInfoLsit[i].getKey()) + '\t'
                out = out + str(self.main_window.cutInfoLsit[i].getStart()) + '\t'
                out = out + str(self.main_window.cutInfoLsit[i].getEnd())
                out = out + '\n'

            self.main_window._window.cutinfo.setText(out)
        elif type == 2 : # display Step 0 Video List
            out = 'Video List :\n'
            for i in range(0,self.main_window.videoLen) :
                out = out + '[' + str(i+1) +'] '+ self.main_window.videolist[i] + '\n'            
            self.main_window._window.cutinfo.setText(out)
        elif type == 3: # display Schedule Lsit

            self.page = int (self.main_window.currentScheduleIndex /self.main_window.pageLen)
            pageStart = self.page * self.main_window.pageLen

            if (self.page+1)*self.main_window.pageLen > len(self.main_window.ScheduleList) :
                pageEnd = len(self.main_window.ScheduleList) 
            else:
                pageEnd = (self.page+1)*self.main_window.pageLen

            out = '\t'+ self.main_window.scheduleName +' Schedule  (' + str(self.page+1) + '/' +  str(int((len(self.main_window.ScheduleList)-1) / self.main_window.pageLen ) +1 ) + ')\n'

            for i in range(pageStart, pageEnd) :
                if i == self.main_window.currentScheduleIndex :
                    out = out + "=>"
                else:
                    out = out + "     "
                out = out + str(i+1) + ' <' + str(self.main_window.ScheduleList[i].step) + '> '
                out = out + self.main_window.ScheduleList[i].getShortActionName() + '\n'

            self.main_window._window.cutinfo.setText(out)
        elif type == 4 : # display TIVP Issue List
            self.page = int (self.main_window.currentIssueIndex / self.main_window.pageLen)
            pageStart = self.page * self.main_window.pageLen
            if (self.page+1)*self.main_window.pageLen > len(self.main_window.TIVIsampleList) :
                pageEnd = len(self.main_window.TIVIsampleList) 
            else:
                pageEnd = (self.page+1)*self.main_window.pageLen

            out = '\t' +' TIVP Issue  (' + str(self.page+1) + '/' +  str(int((len(self.main_window.TIVIsampleList)-1) / self.main_window.pageLen ) +1 ) + ')\n'

            for i in range(pageStart, pageEnd) :
                temp = self.main_window.TIVIsampleList[i].split(',')
                if i == self.main_window.currentIssueIndex :
                    self.main_window.PlayerManager.cap.set(cv2.CAP_PROP_POS_FRAMES, int(int(temp[1]) ))
                    out = out + "=>"
                else:
                    out = out + "    "

                out += f"{i+1} [{temp[0]}] <{temp[5]}> {temp[3]}{temp[4]} {temp[1]}-{temp[2]} \n" 
            self.main_window._window.cutinfo.setText(out)

    def precursorCheck(self):
        step = -1
        
        if self.main_window.currentStep == 9 :
            if self.main_window.TIVPmode == 3 :
                step = 10
            else :
                step = self.main_window.currentStep
        elif self.main_window.currentStep == 3 :
            if self.main_window.show == False :
                step = 11
            else:
                step = self.main_window.currentStep
        else:
            step = self.main_window.currentStep

        paths = self.pathsExistCheck(self.RT_stepPrecursors(step))


        if len(paths) != 0 :
            msgBox = QMessageBox()
            msgBox.setWindowTitle(f"Step Presursor Warning : [Step {self.main_window.currentStep}]")
            text = f"Precursors not found : [Step {self.main_window.currentStep}][ACN:{self.main_window.actionName}]\n"
            for i in range(0, len(paths)) :
                text += f"{i+1}. <{paths[i]}> doesn't exist.\n"
            msgBox.setText(text)
            logger.warning(text)
            if self.main_window.scheduleType == 'run' :
                QTimer.singleShot(5000, msgBox.accept) 
            msgBox.exec()
            return False
        else :
            return True
    
    def RT_stepPrecursors(self, step):
        precursor = [
            self.main_window.droneFolderPath,   # 0
            self.main_window.cutinfo_txt,       # 1
            self.main_window.stab_input,        # 2
            self.main_window.stab_output,       # 3
            self.main_window.stab_video,        # 4
            self.main_window.yolo_txt,          # 5
            self.main_window.tracking_csv,      # 6
            self.main_window.background_img,    # 7
            self.main_window.gateLineIO_txt,    # 8
            self.main_window.gate_tracking_csv, # 9
            self.main_window.result_video,      # 10
            self.main_window.displayType,       # 11
            self.main_window.singelTIVpath,     # 12
            Path("./Model/YOLOv4/weights") / self.main_window.yoloModel          # 13
        ]
        stepNeeds = [
            [0, ],                  #0 Step 0
            [2, 1],                 #1 Step 1
            [4, 13],                #2 Step 2
            [4, 5],                 #3 Step 3
            [4],                    #4 Step 4
            [7],                    #5 Step 5
            [8, 6],                 #6 Step 6
            [4, 9, 8],              #7 Step 7
            [9],                    #8 Step 8
            [12, 8, 4, 9, 7],       #9 Step 9   (Video or Image mode)
            [12, 9, 8, 4, 5],          #10 Step 9  (RealTime mode)
            [5],                    #11 Step 3  (No show mode)
        ]

        ans = []
        for i in range(0, len(stepNeeds[step])):
            ans.append(precursor[stepNeeds[step][i]])
        
        return ans
    
    def pathsExistCheck(self, pathList):
        errList = []
        for i in range(0, len(pathList)):
            if os.path.exists(pathList[i]) == False:
                errList.append(pathList[i])
        
        return errList
    def set_button_text_color(self, button, color):
        palette = button.palette()
        palette.setColor(QPalette.ButtonText, QColor(color))
        button.setPalette(palette)

class ScheduleItem():
    def __init__(self):
        self.step = -1
        self.DisplayID = False
        self.Show = False
        
        self.actionName = ""
        self.resultPath = ""
        self.droneFolderPath = ""

    def setActionName(self, newName):
        self.actionName = newName
    
    def setResultPath(self, newPath):
        self.resultPath = newPath
    
    def setdroneFolderPath(self, newOrgin):
        self.droneFolderPath = newOrgin
    
    def getShortActionName(self):
        out = ""
        if len(self.actionName) > 12:
            out =self.actionName[0:12]+'...'+self.actionName[-4:]
        else:
            out = self.actionName
        return out