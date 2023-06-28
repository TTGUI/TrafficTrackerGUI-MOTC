import PySide2
from PySide2 import QtCore
from PySide2.QtCore import Qt, QUrl
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QFont, QImage, QPixmap
from PySide2.QtWidgets import QFileDialog, QInputDialog, QLineEdit, QWidget, QMessageBox, QDialog, QVBoxLayout, QLabel, QPushButton 
from Model.tool import TrackIntegrityVerificationTool

# https://github.com/vispy/vispy/blob/main/vispy/app/backends/_pyside2.py
from PySide2 import QtTest
if not hasattr(QtTest.QTest, 'qWait'):
    @staticmethod
    def qWait(msec):
        import time
        start = time.time()
        PySide2.QtWidgets.QApplication.processEvents()
        while time.time() < start + msec * 0.001:
            PySide2.QtWidgets.QApplication.processEvents()
    QtTest.QTest.qWait = qWait
import numpy as np

from logs import logger
from config import conf
from Cont import controller

import cv2
import os
import random

'''WARNING : def_setResultFolder() have a potentiality error for path setting when code running on LunixOS'''

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
        self.actionName = "inital_action_name"
        self.resultPath = "./result/"
        
        self.scheduleType = False
        self.currentStep = -1
        self.currentScheduleIndex = 0
        self.ScheduleList = []
        self.scheduleLoadPath = ""
        self.scheduleSavePath = ""
        self.scheduleName = "Default"
        self.scheduleTIVpath = ""
        self.scheduleTIVFile = ""
        self.singelTIVpath = self.resultPath + self.actionName + "_TIV.csv"
        self.page = 0
        self.pageLen = 10

        self.stabMode = conf.getStabMode() # 'CPU' 'GPU'
        self.yoloModel = conf.getYoloModel() #  20211109172733_last_200_1920.pt / ect.
        self.TIVPmode = conf.getTIVPMode() # <1> <2>

        self._window = None
        self.setup_ui()

        # Prepare
        self.originDataList = "./data"
        self.cutinfo_txt = self.resultPath + self.actionName + "_cutInfo.txt"

        # Kstabilization
        self.stab_input = self.originDataList
        self.stab_output = self.resultPath + self.actionName + "_stab.mp4"
        self.show = True

        # Mtracking 
        self.stab_video = self.stab_output
        self.yolo_txt = self.resultPath+ self.actionName +"_stab_8cls.txt"
        self.tracking_csv = self.resultPath + self.actionName + ".csv"

        # NBackground
        self.background_img = self.resultPath+ self.actionName +"_background.jpg" # English Path only....

        # OdrawIO & PIOadded

        self.gateLineIO_txt = self.resultPath + self.actionName + "_IO.txt"
        self.gate_tracking_csv = self.resultPath + self.actionName + "_gate.csv"

        # QReplay
        self.result_video = self.resultPath + self.actionName + "_result.avi"
        self.displayType = True

        """
        YOU ALOS NEED TO MODIFY FUNCTION 'changeActionName'
        """

    @property
    def window(self):
        """The main window object"""
        return self._window

    def setup_ui(self):
        loader = QUiLoader()
        file = QFile('./View/my_window.ui')
        file.open(QFile.ReadOnly)
        self._window = loader.load(file)
        file.close()

        self.set_title()
        self.set_buttons()

        self.video_init = False
        
    def set_title(self):
        """Setup label"""
        self._window.title.setText(str(conf.RTVersion()) + " | " + self.stabMode + " | " + self.yoloModel)
        self._window.setWindowTitle(conf.RTVersion())
        self._window.cutinfo.setText('')
        self._window.display.setText('')
        self._window.FPS.setText('')
        self._window.ActionName_edit.setText('inital_action_name')

        # set font
        font = QFont("Arial", 15, QFont.Bold)
        self._window.title.setFont(font)
        # set widget size (x, y, width, height)
        # self._window.title.setGeometry(0, 0, 300, 30)
        # set alignment
        # self._window.title.setAlignment(Qt.AlignBottom | Qt.AlignCenter)

    def set_buttons(self):
        """Setup buttons"""
        self._window.bar_1.triggered.connect(self.runPedestrian)

        self._window.bar_2.triggered.connect(self.changeStabMode)
        if self.stabMode == 'CPU':
            self._window.bar_2.setText("Change Stabilazation Mode | [ CPU ]")
        elif self.stabMode == 'GPU':
            self._window.bar_2.setText("Change Stabilazation Mode | [ GPU ]")

        self._window.bar_3.triggered.connect(self.changeYoloModel)

        self._window.bar_4.triggered.connect(self.changeTIVPbMode)
        if self.TIVPmode == 1:
            self._window.bar_4.setText("Change TIVP Mode | [ Video ]")
        elif self.TIVPmode == 2:
            self._window.bar_4.setText("Change TIVP Mode | [ Image ]")
        elif self.TIVPmode == 3:
            self._window.bar_4.setText("Change TIVP Mode | [ Real Time Display ]")

        self._window.Change_Tracking_Setting.triggered.connect(self.changeTrackingSet)

        self._window.DroneFolder_btn.setText('Set Drone Folder')
        self._window.DroneFolder_btn.clicked.connect(self.droneFolder)

        self._window.setResultFolder_btn.setText('Set Result Folder\n[./result/]')
        self._window.setResultFolder_btn.clicked.connect(self.setResultFolder)

        self._window.step0_btn.setText('[STEP 0]\nVideo Cut Set')
        self._window.step0_btn.clicked.connect(self.step0)
        
        if self.stabMode == 'CPU':
            self._window.step1_btn.setText('[STEP 1] (C)\nStable')
        elif self.stabMode == 'GPU':
            self._window.step1_btn.setText('[STEP 1] (G)\nStable')
        self._window.step1_btn.clicked.connect(self.step1)

        self._window.step2_btn.setText('[STEP 2]\nYolo')
        self._window.step2_btn.clicked.connect(self.step2)

        self._window.step3_btn.setText('[STEP 3]\nTracking')
        self._window.step3_btn.clicked.connect(self.step3)

        self._window.step4_btn.setText('[STEP 4]\nBackground')
        self._window.step4_btn.clicked.connect(self.step4)

        self._window.step5_btn.setText('[STEP 5]\nDrawIO')
        self._window.step5_btn.clicked.connect(self.step5)

        self._window.step6_btn.setText('[STEP 6]\nIO Added')
        self._window.step6_btn.clicked.connect(self.step6)

        self._window.step7_btn.setText('[STEP 7]\nReplay')
        self._window.step7_btn.clicked.connect(self.step7)

        self._window.TVI_btn.setText("<TrackIntegrityVerification>")
        self._window.TVI_btn.clicked.connect(self.step8_singleTIV)

        if self.TIVPmode == 1:
            self._window.TVIPrinter_btn.setText('<TIV Printer> (V)')
        elif self.TIVPmode == 2:
            self._window.TVIPrinter_btn.setText('<TIV Printer> (I)')
        elif self.TIVPmode == 3:
            self._window.TVIPrinter_btn.setText('<TIV Printer> (R)')
        self._window.TVIPrinter_btn.clicked.connect(self.step9_TVIPrinter)

        #########################################################
        self._window.show_btn.setText('Show')
        self._window.show_btn.clicked.connect(self.show)

        self._window.DisplayType_btn.setText('Display ID information')
        self._window.DisplayType_btn.clicked.connect(self.DisplayType)

        self._window.ActionName_btn.setText('Edit Action Name')
        self._window.ActionName_btn.clicked.connect(self.changeActionName)

        self._window.selectName_btn.setText('Select Action Name from File')
        self._window.selectName_btn.clicked.connect(self.selectName)        

        #########################################################

        self._window.ScheduleMode_btn.setText('Schedule Mode <OFF>')
        self._window.ScheduleMode_btn.clicked.connect(self.ScheduleMode)

        self._window.StartSchedule_btn.setText('Start Schedule')
        self._window.StartSchedule_btn.clicked.connect(self.StartSchedule)

        self._window.GetSchedule_btn.setText('Get Scheudle')
        self._window.GetSchedule_btn.clicked.connect(self.GetSchedule)

        self._window.SetSchedule_btn.setText('Set Scheudle')
        self._window.SetSchedule_btn.clicked.connect(self.SetSchedule)

        self._window.DeleteSchedule_btn.setText('Delete Schedule')
        self._window.DeleteSchedule_btn.clicked.connect(self.DeleteSchedule)

        self._window.LoadScheduleFile_btn.setText('Load Schedule File')
        self._window.LoadScheduleFile_btn.clicked.connect(self.loadSchedule)       

        self._window.SaveScheduleFile_btn.setText('Save Schedule File')
        self._window.SaveScheduleFile_btn.clicked.connect(self.saveSchedule)    

        self._window.ForwardPage_btn.setText('<<== Page')
        self._window.ForwardPage_btn.clicked.connect(self.forwardPage)

        self._window.NextPage_btn.setText('Page ==>>')
        self._window.NextPage_btn.clicked.connect(self.nextPage)

        #########################################################

        self._window.pause_btn.setText('Pause')
        self._window.pause_btn.clicked.connect(self.pause)

        self._window.play_btn.setText('Play')
        self._window.play_btn.clicked.connect(self.play)

        self._window.stop_btn.setText('Stop')
        self._window.stop_btn.clicked.connect(self.stop)

        self._window.fpsback_btn.setText('<')
        self._window.fpsback_btn.clicked.connect(self.fpsback)

        self._window.fpsnext_btn.setText('>')
        self._window.fpsnext_btn.clicked.connect(self.fpsnext)

        self._window.jump_btn.setText('Jump')
        self._window.jump_btn.clicked.connect(self.jump)

        self._window.timingSlider.sliderMoved.connect(self.video_position)

        self._window.Back_btn.setText('▲ Back')
        self._window.Back_btn.clicked.connect(self.back)

        self._window.Next_btn.setText('▼ Next')
        self._window.Next_btn.clicked.connect(self.next)

        self._window.SetStartFrame_btn.setText('SetStartFrame')
        self._window.SetStartFrame_btn.clicked.connect(self.setStartFrame)

        self._window.SetEndFrame_btn.setText('SetEndFrame')
        self._window.SetEndFrame_btn.clicked.connect(self.setEndFrame)

    def set_video(self, type):
        if type == 1 : # Step 0 Cut Info Player Mode
            self.video_init = True
            self.play_bool = False
            self.currentVideoIndex = 0
            self.videolist = os.listdir(self.originDataList)
            self.videolist.sort()
            self.videoLen = len(self.videolist)
            self.cutInfoLsit = []
            for i in range( 0 ,self.videoLen ):
                tempCut = CutInfo()            
                
                currentVideo = self.videolist[i]
                cap = cv2.VideoCapture(os.path.join( os.path.abspath(self.originDataList), currentVideo))

                tempCut.setStart(1)
                tempCut.setEnd(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
                cap.release()
                self.cutInfoLsit.append(tempCut)

            self.displayInfo(2)

            out = ''
            for i in range(0,self.videoLen) :
                out = out + '[' + str(i+1) +'] '+ self.videolist[i] + '\n'

            msgBox = QMessageBox()
            msgBox.setWindowTitle("Video Load")
            msgBox.setText(out)
            msgBox.exec()

            self.load()
        elif type == 2 : # Step 9 TVIP Real Time Display Mode
            self.video_init = True
            self.play_bool = False
            self.cap = cv2.VideoCapture(self.stab_video)
            print("LOAD : " + str(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))+ ' frames')
            self.allFream = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

            
            
    @QtCore.Slot()
    def frameDisplay(self, frame) :
        fps = str(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        cv2.putText(frame, fps, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 6, cv2.LINE_AA)
        cv2.putText(frame, fps, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3, cv2.LINE_AA)
        self._window.FPS.setText(fps[:-2])
        nowFream = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        self._window.timingSlider.setValue(int((nowFream/self.allFream)*100))  

        show = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        showImage = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
        self._window.display.setScaledContents(True) # 自適應邊框  
        self._window.display.setPixmap(QPixmap.fromImage(showImage))
        
    @QtCore.Slot()
    def selectName(self):
        actName = QFileDialog.getOpenFileName(self._window, 'Select file to set Action Name', self.resultPath)

        tempName = actName[0]
        if tempName == "" :
            print("[CANCEL] Select Action Name Cancel.")
        else :
            backword = ["_gate.csv", "_TIV.csv", ".csv", "_background.jpg", "_cutInfo.txt", "_IO.txt", "_result.avi", "_result.mp4", "_stab.avi", "_stab.mp4", "_stab_8cls.txt" ]
            for i in range(0,len(backword)):
                backLen = -len(backword[i])
                if tempName[backLen:] == backword[i] :
                    tempName = tempName[0:backLen]

            self._window.ActionName_edit.setText(os.path.basename(tempName))
            self.changeActionName()

    @QtCore.Slot()
    def load(self):
        if self.video_init == False :
            self._window.cutinfo.setText('Error : video are not set yet.')
            return

        self.displayInfo(1)
        currentVideo = self.videolist[self.currentVideoIndex]
        self.cap = cv2.VideoCapture(os.path.join( os.path.abspath(self.originDataList), currentVideo))
        print("LOAD : " + str(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))+ ' frames')
        self.allFream = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.video_init = True

    @QtCore.Slot()
    def play(self):       
        self.play_bool = True

        video_FPS = 0
        if self.cap.isOpened() :
            video_FPS = int(self.cap.get(cv2.CAP_PROP_FPS))

        # print(video_FPS)
        while self.cap.isOpened() :
            
            ret, frame = self.cap.read()
            if not ret :
                break
            nowFream = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            # print(nowFream)
            if not self.scheduleType and self.TIVPmode == 3 and self.currentStep == 9 :
                frame = self.issueFramePrint(frame)
            else :        
                cv2.putText(frame, str(nowFream), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3, cv2.LINE_AA)
            
            self.frameDisplay(frame)
            QtTest.QTest.qWait(video_FPS)

            if not self.play_bool :
                break           

    @QtCore.Slot()
    def pause(self):
        self.play_bool = False

    @QtCore.Slot()
    def stop(self):

        if self.scheduleType :
            self.currentScheduleIndex = self.currentScheduleIndex + 1
            self.displayInfo(3)
            self.StartSchedule()
        else :

            self.cap.release()
            cv2.destroyAllWindows()
            print("stop")

    @QtCore.Slot()
    def fpsback(self) :
        if not self.TIVPmode == 3 :
            self.play_bool = False
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.cap.get(cv2.CAP_PROP_POS_FRAMES) - 101 )
        if self.cap.isOpened() :
            ret, frame = self.cap.read()
            if ret:                
                self.frameDisplay(frame)

    @QtCore.Slot()
    def fpsnext(self) :
        if not self.TIVPmode == 3 :
            self.play_bool = False
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.cap.get(cv2.CAP_PROP_POS_FRAMES) + 99 )
        if self.cap.isOpened() :
            ret, frame = self.cap.read()
            if ret:                
                self.frameDisplay(frame)

    @QtCore.Slot()
    def jump(self) :
        self.play_bool = False
        jumpframe = 0
        if self.TIVPmode == 3 and self._window.FPS.text()[0] == 'i':
            # 添加手動設定目標track id進 issue list
            print(f"Add Tracking ID [{self._window.FPS.text()[1:]}] to TVIP Issue list.")
            
            temp = ""
            for i in range(0, len(self.V)):
                if self.V[i][0] == self._window.FPS.text()[1:]:
                    for m in range(0,6) :
                        temp += self.V[i][m] + ","
                    jumpframe = int(self.V[i][1])
            if temp == "" :
                print(f"Error >> Tracking ID invalid : {self._window.FPS.text()[1:]}")
            else :
                self.TIVIsampleList.append(temp)
                self.currentIssueIndex = len(self.TIVIsampleList) - 1
                self.displayInfo(4)

        else :
            jumpframe = int(self._window.FPS.text()) -1
            if jumpframe > self.cap.get(cv2.CAP_PROP_FRAME_COUNT) :
                jumpframe = self.cap.get(cv2.CAP_PROP_FRAME_COUNT) -1

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, jumpframe)
        if self.cap.isOpened() :
            ret, frame = self.cap.read()
            if ret:                
                self.frameDisplay(frame)

    @QtCore.Slot()
    def video_position(self, video_position):
        fream = int((self.allFream/100)*video_position)     
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, fream)
        if self.cap.isOpened() :
            ret, frame = self.cap.read()

            fps = str(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            cv2.putText(frame, fps, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3, cv2.LINE_AA)
            self._window.FPS.setText(fps)
            self.frameDisplay(frame)

    @QtCore.Slot()
    def displayInfo(self,type):

        if type == 1 : # display Step 0 CutInfo
            out = '\tCutInfo  ( ' + str(self.currentVideoIndex + 1) + ' / ' + str(self.videoLen) + ' )\n'
            for i in range(0,self.videoLen) :
                if i == self.currentVideoIndex :
                    out = out + "=>"
                else :
                    out = out + "    "
                out = out + "[" + str(i+1) + ']'
                out = out + str(self.cutInfoLsit[i].getKey()) + '\t'
                out = out + str(self.cutInfoLsit[i].getStart()) + '\t'
                out = out + str(self.cutInfoLsit[i].getEnd())
                out = out + '\n'
            
            self._window.cutinfo.setText(out)
        elif type == 2 : # display Step 0 Video List
            out = 'Video List :\n'
            for i in range(0,self.videoLen) :
                out = out + '[' + str(i+1) +'] '+ self.videolist[i] + '\n'            
            self._window.cutinfo.setText(out)
        elif type == 3: # display Schedule Lsit

            self.page = int (self.currentScheduleIndex /self.pageLen)
            pageStart = self.page * self.pageLen

            if (self.page+1)*self.pageLen > len(self.ScheduleList) :
                pageEnd = len(self.ScheduleList) 
            else:
                pageEnd = (self.page+1)*self.pageLen

            out = '\t'+ self.scheduleName +' Schedule  (' + str(self.page+1) + '/' +  str(int((len(self.ScheduleList)-1) / self.pageLen ) +1 ) + ')\n'

            for i in range(pageStart, pageEnd) :
                if i == self.currentScheduleIndex :
                    out = out + "=>"
                else:
                    out = out + "    "
                out = out + str(i+1) + ' <' + str(self.ScheduleList[i].step) + '>' + '\t'
                out = out + self.ScheduleList[i].getShortActionName() + '\n'

            self._window.cutinfo.setText(out)
        elif type == 4 : # display TIVP Issue List
            self.page = int (self.currentIssueIndex / self.pageLen)
            pageStart = self.page * self.pageLen
            if (self.page+1)*self.pageLen > len(self.TIVIsampleList) :
                pageEnd = len(self.TIVIsampleList) 
            else:
                pageEnd = (self.page+1)*self.pageLen

            out = '\t' +' TVIP Issue  (' + str(self.page+1) + '/' +  str(int((len(self.TIVIsampleList)-1) / self.pageLen ) +1 ) + ')\n'

            for i in range(pageStart, pageEnd) :
                temp = self.TIVIsampleList[i].split(',')
                if i == self.currentIssueIndex :
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, int(int(temp[1]) ))
                    out = out + "=>"
                else:
                    out = out + "    "

                out += f"{i+1} [{temp[0]}] <{temp[5]}> {temp[3]}{temp[4]} {temp[1]}-{temp[2]} \n" 
            self._window.cutinfo.setText(out)

    @QtCore.Slot()
    def back(self):
        if self.scheduleType : # 在Schedule 編輯模式
            if self.currentScheduleIndex > 0 :
                self.currentScheduleIndex = self.currentScheduleIndex - 1
                
                self.displayInfo(3)
        elif self.TIVPmode == 3 : # 在TIVP Realtime 模式
            if self.currentIssueIndex > 0 :
                self.currentIssueIndex -= 1
                self.displayInfo(4)  
        elif self.currentVideoIndex > 0 : # 在Step 0 模式
            self.currentVideoIndex = self.currentVideoIndex - 1
            self.displayInfo(2) 
            self.load()
            self.save()

    @QtCore.Slot()
    def next(self):

        if self.scheduleType : # 在Schedule 編輯模式
            if self.currentScheduleIndex < len(self.ScheduleList) - 1 :
                self.currentScheduleIndex = self.currentScheduleIndex + 1
                
                self.displayInfo(3)
        elif self.currentStep == 9 and self.TIVPmode == 3 : # 在TIVP Realtime 模式
            if self.currentIssueIndex < len(self.TIVIsampleList) - 1:
                self.currentIssueIndex += 1
                self.displayInfo(4)
        elif self.currentVideoIndex < self.videoLen - 1 : # 在Step 0 模式
            self.currentVideoIndex = self.currentVideoIndex + 1
            self.displayInfo(2) 
            self.load()
            self.save()

    @QtCore.Slot()
    def forwardPage(self):
        if self.scheduleType : # 在Schedule 編輯模式
            if self.page > 0:
                self.page = self.page -1
                self.currentScheduleIndex = self.page * self.pageLen
            elif self.page == 0 :
                self.currentScheduleIndex = 0
            self.displayInfo(3)
        elif self.currentStep == 9 and self.TIVPmode == 3 : # 在TIVP Realtime 模式
            if self.page > 0:
                self.page = self.page -1
                self.currentIssueIndex = self.page * self.pageLen
            elif self.page == 0 :
                self.currentIssueIndex = 0
            self.displayInfo(4)
        else: # 在Step 0 模式
            if self.page > 0:
                self.page = self.page -1
                self.currentVideoIndex = self.page * self.pageLen
            elif self.page == 0 :
                self.currentVideoIndex = 0
            self.displayInfo(2)

    @QtCore.Slot()
    def nextPage(self):
        if self.scheduleType  :
            if self.page < int((len(self.ScheduleList)-1) / self.pageLen ):
                self.page = self.page + 1
                self.currentScheduleIndex = self.page * self.pageLen
            self.displayInfo(3)
        elif self.TIVPmode == 3 :           

            if self.page < int((len(self.TIVIsampleList)-1) / self.pageLen ):
                self.page = self.page + 1
                self.currentIssueIndex = self.page * self.pageLen
            self.displayInfo(4)
        else:
            if self.page < int((self.videoLen-1) / self.pageLen ):
                self.page = self.page + 1
                self.currentVideoIndex = self.page * self.pageLen
            self.displayInfo(2)
        

    @QtCore.Slot()
    def setKey(self):
        self.cutInfoLsit[self.currentVideoIndex].setKey(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        for i in range(self.currentVideoIndex+1,len(self.cutInfoLsit)) :
            self.cutInfoLsit[i].setKey(-1)
            self.cutInfoLsit[i].setStart(1)

        self.displayInfo(1)

    @QtCore.Slot()
    def resetSetKeyFrame(self):
        self.cutInfoLsit[self.currentVideoIndex].setKey(-1)
        self.displayInfo(1)

    @QtCore.Slot()
    def setStartFrame(self):
        for i in range(0,self.currentVideoIndex) :
            # before start frame, ignore Videos.
            self.cutInfoLsit[i].setKey(-1)
            self.cutInfoLsit[i].setStart(-1)
            self.cutInfoLsit[i].setEnd(-1)
        
        self.cutInfoLsit[self.currentVideoIndex].setStart(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        
        self.displayInfo(1)
        self.setKey()
        self.save()

    @QtCore.Slot()
    def resetSetStartFrame(self):
        self.cutInfoLsit[self.currentVideoIndex].setStart(1)
        self.displayInfo(1)

    @QtCore.Slot()
    def setEndFrame(self):
        for i in range(self.currentVideoIndex+1 ,len(self.cutInfoLsit)) :
            # after end frame, ignore Videos.
            self.cutInfoLsit[i].setKey(-1)
            self.cutInfoLsit[i].setStart(-1)
            self.cutInfoLsit[i].setEnd(-1)

        self.cutInfoLsit[self.currentVideoIndex].setEnd(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        self.displayInfo(1)
        self.save()

    @QtCore.Slot()
    def resetSetEndFrame(self):
        self.cutInfoLsit[self.currentVideoIndex].setEnd(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.displayInfo(1)

    @QtCore.Slot()
    def ignoreVideo(self):
        self.cutInfoLsit[self.currentVideoIndex].setKey(-1)
        self.cutInfoLsit[self.currentVideoIndex].setStart(-1)
        self.cutInfoLsit[self.currentVideoIndex].setEnd(-1)
        self.displayInfo(1)

    @QtCore.Slot()
    def resetIgnoreVideo(self):
        self.cutInfoLsit[self.currentVideoIndex].setStart(0)
        self.cutInfoLsit[self.currentVideoIndex].setEnd(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.displayInfo(1)

    @QtCore.Slot()
    def save(self):
        if self.cuttingWarning() == False :
            f = open(self.cutinfo_txt, 'w')
            
            for i in range(0,self.videoLen) :
                out = ''
                out = out + str(self.cutInfoLsit[i].getKey()) + '\t'
                out = out + str(self.cutInfoLsit[i].getStart()) + '\t'
                out = out + str(self.cutInfoLsit[i].getEnd()) + '\n'
                f.write(out)

            f.close()
            logger.info("[Step 0] ->> Cuttting Set file Save :" + self.cutinfo_txt)
            # self._window.cutinfo.setText("coutinfo save as\n" + self.cutinfo_txt)

    @QtCore.Slot()
    def show(self):


        if self.show:
            self.show = False
            self._window.show_btn.setText('BackGround')

        else :
            self.show = True
            self._window.show_btn.setText('Show')

    @QtCore.Slot()
    def DisplayType(self) :

        if self.displayType:
            self.displayType = False
            self._window.DisplayType_btn.setText('Hide ID information')

        else :
            self.displayType = True
            self._window.DisplayType_btn.setText('Display ID information')

    @QtCore.Slot()
    def ScheduleMode(self):
        if self.scheduleType  :
            self.scheduleType = False
            self._window.ScheduleMode_btn.setText('Schedule Mode <OFF>')


        else:
            self.scheduleType = True
            self._window.ScheduleMode_btn.setText('Schedule Mode <ON>')

    @QtCore.Slot()
    def StartSchedule(self):

        self.scheduleType = False 
        self._window.ScheduleMode_btn.setText('Schedule Mode <OFF>')
        cuurentTIVT = TrackIntegrityVerificationTool.TIVT()
        ScheduTIVList = []
        ScheduTIVList.append(cuurentTIVT.retTitle())

        for i in range(self.currentScheduleIndex ,len(self.ScheduleList)):
            self.currentScheduleIndex = i
            self.displayInfo(3)
            sch = '=====================================\n[Schedule ' + str(i+1) +' / ' + str(len(self.ScheduleList))+' ]'
            self.displayType = self.ScheduleList[i].DisplayID
            self.show = self.ScheduleList[i].Show
            
            self.actionName = self.ScheduleList[i].actionName
            self.resultPath = self.ScheduleList[i].resultPath
            self.originDataList = self.ScheduleList[i].originDataList
            self.flashActionName()

            if self.ScheduleList[i].step == 0:
                print(sch + " - [STEP 0]")
                self.set_video(1)
                self.play()
            elif self.ScheduleList[i].step == 1:
                print(sch + " - [STEP 1]")
                controller.con_step1(self.stab_input, self.stab_output, self.show, self.cutinfo_txt, self.stabMode)
            elif self.ScheduleList[i].step == 2:
                print(sch + " - [STEP 2]")
                controller.con_step2(self.stab_video, self.yolo_txt, self.yoloModel)
            elif self.ScheduleList[i].step == 3:
                print(sch + " - [STEP 3]")
                controller.con_step3(self.stab_video,self.yolo_txt,self.tracking_csv,self.show, conf.getTrk1_Set(), conf.getTrk2_Set())                
            elif self.ScheduleList[i].step == 4:
                print(sch + " - [STEP 4]")
                tempName = self.resultPath + str(random.random()) +'.jpg'
                controller.con_step4(self.stab_video,tempName)
                os.rename(tempName, self.background_img)
            elif self.ScheduleList[i].step == 5:
                print(sch + " - [STEP 5]")
                controller.con_step5(self.gateLineIO_txt,self.background_img)
            elif self.ScheduleList[i].step == 6:
                print(sch + " - [STEP 6]")
                controller.con_step6(self.gateLineIO_txt, self.tracking_csv, self.gate_tracking_csv) 
            elif self.ScheduleList[i].step == 7:
                print(sch + " - [STEP 7]")
                controller.con_step7(self.stab_video, self.result_video, self.gate_tracking_csv, self.gateLineIO_txt, self.displayType, self.show)        
            elif self.ScheduleList[i].step == 8:
                print(sch + " - [STEP 8 - TIV]")
                ScheduTIVList.append(controller.con_TIVT(self.gate_tracking_csv, self.singelTIVpath))
            elif self.ScheduleList[i].step == 9:
                print(sch + " - [STEP 9 - TIVP]")
                controller.con_TIVP(self.singelTIVpath, self.gateLineIO_txt, self.stab_video, self.resultPath, self.actionName, self.gate_tracking_csv, self.background_img )  

        
        if self.scheduleTIVpath == "" :
            self.scheduleTIVFile = "./result/" + "/" + self.scheduleName + "_TIV.csv"
        else :
            self.scheduleTIVFile = self.scheduleTIVpath + "/" + self.scheduleName + "_TIV.csv"

        base, extension = os.path.splitext(self.scheduleTIVFile)
        k = 0
        while os.path.exists(self.scheduleTIVFile):
            k += 1
            self.scheduleTIVFile = f"{base}_{k}{extension}"

        fp = open( self.scheduleTIVFile, "w")

        for i in range (0,len(ScheduTIVList)):
            fp.write(ScheduTIVList[i])
            fp.write("\n")
        fp.close()

        print ("ALL Schedule Done.")

        self.scheduleType = False
        self._window.ScheduleMode_btn.setText('Schedule Mode <OFF>')

    @QtCore.Slot()
    def AddScheudle(self):
        tempItem = ScheduleItem()
        tempItem.DisplayID = self.displayType 
        tempItem.Show = self.show         
        tempItem.actionName = self.actionName
        tempItem.resultPath = self.resultPath
        tempItem.originDataList = self.originDataList
        tempItem.step = self.currentStep
        self.ScheduleList.insert(self.currentScheduleIndex +1, tempItem)
        if len(self.ScheduleList) == 1 :
            self.currentScheduleIndex = 0
        else :
            self.currentScheduleIndex = self.currentScheduleIndex +1

        self.displayInfo(3)
        
        
        print("AddSchedule "+ str(self.currentScheduleIndex+1) +" : [Step "+str(tempItem.step) + "] - [" + tempItem.actionName +"]")
    
    @QtCore.Slot()
    def GetSchedule(self):
        self.loadCurrentScheduleItem()

    @QtCore.Slot()
    def SetSchedule(self):
        tempItem = ScheduleItem()
        tempItem.DisplayID = self.displayType 
        tempItem.Show = self.show 
        
        tempItem.actionName = self.actionName
        tempItem.resultPath = self.resultPath
        tempItem.originDataList = self.originDataList
        tempItem.step = self.currentStep
        self.ScheduleList[self.currentScheduleIndex] = tempItem
        self.displayInfo(3)
        
    @QtCore.Slot()
    def DeleteSchedule(self):
        if len(self.ScheduleList) > 0 :

            self.ScheduleList.pop(self.currentScheduleIndex)
            if self.currentScheduleIndex > 0:
                self.currentScheduleIndex = self.currentScheduleIndex -1
        self.displayInfo(3)

    @QtCore.Slot()
    def loadSchedule(self):
        self.scheduleLoadPath, filetype = QFileDialog.getOpenFileName(self._window,"Select Schedule File.", self.resultPath ,options=QFileDialog.DontUseNativeDialog)
        if not self.scheduleLoadPath :
            print ("[Cancel] Schedule Load Cancel.")
        else:
            print ("Load Schedule File : " + self.scheduleLoadPath)
            self.scheduleName = self.scheduleLoadPath.split("/")[-1][:-13]
            self.scheduleTIVpath = os.path.dirname(self.scheduleLoadPath)

            self.readScheduleFile()
            self.scheduleType = True
            self._window.ScheduleMode_btn.setText('Schedule Mode <ON>')
            self.loadCurrentScheduleItem()
            self.displayInfo(3)

    def loadCurrentScheduleItem(self):
        self.actionName = self.ScheduleList[self.currentScheduleIndex].actionName
        self.resultPath = self.ScheduleList[self.currentScheduleIndex].resultPath
        self.originDataList = self.ScheduleList[self.currentScheduleIndex].originDataList
        self.show = self.ScheduleList[self.currentScheduleIndex].Show
        self.displayType = self.ScheduleList[self.currentScheduleIndex].DisplayID

        if self.show:
            self._window.show_btn.setText('Show')
        else :
            self._window.show_btn.setText('BackGround')
        if self.displayType:
            self._window.DisplayType_btn.setText('Display ID information')
        else :
            self._window.DisplayType_btn.setText('Hide ID information')

        self.flashActionName()

    @QtCore.Slot()
    def saveSchedule(self):
        filetype = ("_Schedule.txt")
        temp = QFileDialog.getSaveFileName(self._window,"Save Schedule File.", "", filetype, options=QFileDialog.DontUseNativeDialog,)
        self.scheduleSavePath = temp[0] + temp[1]
        self.scheduleName = temp[0].split("/")[-1]
        self.writeScheduleFile()
        print ("Save Schedule File : " + self.scheduleSavePath)
        self.scheduleTIVpath = os.path.dirname(self.scheduleSavePath)
        self.displayInfo(3)

    def readScheduleFile(self):
        f = open(self.scheduleLoadPath, 'r')
        lineData = f.readlines()
        self.ScheduleList = []

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
                    elif counter == 5 : # originDataList
                        tempSchedule.originDataList = tempIndex
                             
                    counter = counter + 1
                    tempIndex = ""
                else:
                    tempIndex = tempIndex + char

            self.ScheduleList.append(tempSchedule)

        f.close()
        
    def writeScheduleFile(self):
        for i in range(0, len(self.ScheduleList)):
            f = open(self.scheduleSavePath, 'w')

            for i in range(0,len(self.ScheduleList)) :
                if self.ScheduleList[i].DisplayID:
                    display = 1
                else:
                    display = 0

                if self.ScheduleList[i].Show:
                    show = 1
                else :
                    show = 0

                out = ''
                out = out + str(self.ScheduleList[i].step) + '\t'
                out = out + str(display) + '\t'
                out = out + str(show) + '\t'
                out = out + self.ScheduleList[i].actionName + '\t'
                out = out + self.ScheduleList[i].resultPath + '\t'
                out = out + self.ScheduleList[i].originDataList + '\n'
                
                f.write(out)
            f.close()

    @QtCore.Slot()
    def droneFolder(self):

        folderpath = QFileDialog.getExistingDirectory(self._window, 'Select Folder to Staibilization', options=QFileDialog.DontUseNativeDialog)
        if folderpath == "" :
            print("[CANCEL] Set Drone Folder Cancel.")
        else :
            flist = os.listdir(folderpath)
            if len(flist) == 0:
                print("<< Warinig : Your Drone Folder Has NO VIDEOS.")
            else:
                self.actionName = flist[0]
                self._window.ActionName_edit.setText(self.actionName)

            self.originDataList = folderpath
            self.setDroneFolderBtnText()
            logger.info("[Set droneFolder] ->> stable originDataList change to :" + self.originDataList)
            self.changeActionName()

    def setDroneFolderBtnText(self):
        out = ""
        counter = 0
        for i in range(0,len(self.originDataList)):
            out = out + self.originDataList[i]
            counter = counter + 1
            if counter == 23 :
                out = out + '\n'
                counter = 0

        self._window.DroneFolder_btn.setText('Set Drone Folder\n['+ out +']')

    @QtCore.Slot()
    def setResultFolder(self):
        temp = QFileDialog.getExistingDirectory(self._window, 'Select Folder to Result.', self.resultPath,options=QFileDialog.DontUseNativeDialog) + '/' # Warning : the path setting maybe can not runnung on Lunix OS
        
        if temp == "/" :
            print("[CANCEL] Set Result Folder Cancel.")
            
        else :
            self.resultPath = temp
            self.setResultFolderBtnText()
            self.changeActionName()

    def setResultFolderBtnText(self):
        out = ""
        counter = 0
        for i in range(0,len(self.resultPath)):
            out = out + self.resultPath[i]
            counter = counter + 1
            if counter == 23 :
                out = out + '\n'
                counter = 0

        self._window.setResultFolder_btn.setText('Set Result Folder\n['+ out +']')

    @QtCore.Slot()
    def step0(self):
        self.currentStep = 0
        if self.scheduleType :
            print("Current Schedule Item Step >> 0 ")            
            self.AddScheudle()
        else :
            print("[STEP 0]")
            self.set_video(1)
            self.play()
        
    @QtCore.Slot()
    def step1(self):
        self.currentStep = 1
        if self.scheduleType :
            print("Current Schedule Item Step >> 1 ")            
            self.AddScheudle()
        else :
            print("[STEP 1]")
            controller.con_step1(self.stab_input, self.stab_output, self.show, self.cutinfo_txt, self.stabMode)
               
    @QtCore.Slot()
    def step2(self): # Yolo
        self.currentStep = 2
        if self.scheduleType :
            print("Current Schedule Item Step >> 2 ")            
            self.AddScheudle()
        else :
            print("[STEP 2]")
            controller.con_step2(self.stab_video, self.yolo_txt, self.yoloModel )

    @QtCore.Slot()
    def step3(self): # Tracking
        self.currentStep = 3
        if self.scheduleType :
            print("Current Schedule Item Step >> 3 ")
            self.AddScheudle()
        else :
            print("[STEP 3]")
            controller.con_step3(self.stab_video,self.yolo_txt,self.tracking_csv,self.show, conf.getTrk1_Set(), conf.getTrk2_Set())

    @QtCore.Slot()
    def step4(self): # BackGround
        self.currentStep = 4
        if self.scheduleType :
            print("Current Schedule Item Step >> 4 ")            
            self.AddScheudle()
        else :
            print("[STEP 4]")
            tempName = self.resultPath + str(random.random()) +'.jpg'
            controller.con_step4(self.stab_video,tempName)
            os.rename(tempName, self.background_img)

    @QtCore.Slot()
    def step5(self): # DrawIO
        self.currentStep = 5
        if self.scheduleType :
            print("Current Schedule Item Step >> 5 ")            
            self.AddScheudle()
        else :  
            print("[STEP 5]")
            controller.con_step5(self.gateLineIO_txt,self.background_img)

    @QtCore.Slot()
    def step6(self): # IO added
        self.currentStep = 6
        if self.scheduleType :
            print("Current Schedule Item Step >> 6 ")            
            self.AddScheudle()
        else :
            print("[STEP 6]")
            controller.con_step6(self.gateLineIO_txt, self.tracking_csv, self.gate_tracking_csv)

    @QtCore.Slot()
    def step7(self): # Replay
        self.currentStep = 7
        if self.scheduleType :
            print("Current Schedule Item Step >> 7 ")            
            self.AddScheudle()
        else :
            print("[STEP 7]")
            controller.con_step7(self.stab_video, self.result_video, self.gate_tracking_csv, self.gateLineIO_txt, self.displayType, self.show)

    @QtCore.Slot()
    def step8_singleTIV(self):
        self.currentStep = 8
        if self.scheduleType :
            print("Current Schedule Item Step >> TIV ")            
            self.AddScheudle()
        else :
            print("[STEP TIV]")
            return controller.con_TIVT(self.gate_tracking_csv, self.singelTIVpath)

    @QtCore.Slot()  
    def step9_TVIPrinter(self):
        self.currentStep = 9
        if self.scheduleType :
            print("Current Schedule Item Step >> TIVPrinter ")
            self.AddScheudle()
        else :
            print("[STEP TIV Printer]")
            if self.TIVPmode == 3 :
                self.set_video(2)
                self.currentIssueIndex = 0
                f = open(self.singelTIVpath, 'r')
                TIV = f.readlines()
                f.close()

                self.TIVIsampleList = []
                index = 0 
                while index < len(TIV) and TIV[index] != "SameIOCar\n" :
                    index += 1

                index += 1
                while index < len(TIV) and TIV[index] != "SameIOMotor\n" :
                    self.TIVIsampleList.append(TIV[index])
                    index += 1

                index += 1
                while index < len(TIV) :
                    self.TIVIsampleList.append(TIV[index])
                    index += 1

                fio = open(self.gateLineIO_txt, 'r')
                self.TIVioLines = fio.readlines()
                fio.close()

                fp = open(self.gate_tracking_csv, "r") 
                
                lines = fp.readlines()
                fp.close()
                self.V = []
                for j in range(0, len(lines)):
                    self.V.append([])
                    T = lines[j].split(",")
                    for k in range(0, len(T)):
                        self.V[j].append(T[k])

                self.displayInfo(4)
            else :
                controller.con_TIVP(self.singelTIVpath, self.gateLineIO_txt, self.stab_video, self.resultPath, self.actionName, self.gate_tracking_csv, self.background_img )  

    @QtCore.Slot()
    def runPedestrian(self):

        print("PedestrianDataMaker")
        controller.con_DO1(self.originDataList, self.resultPath, self.cutinfo_txt, self.actionName)

    @QtCore.Slot()
    def changeStabMode(self):
        if self.stabMode == 'CPU':
            self.stabMode = 'GPU'
            conf.setStabMode('GPU')
            self._window.bar_2.setText("Change Stabilazation Mode | [ GPU ]")
            self._window.step1_btn.setText('[STEP 1] (G)\nStable')
        elif self.stabMode == 'GPU':
            self.stabMode = 'CPU'
            conf.setStabMode('CPU')
            self._window.bar_2.setText("Change Stabilazation Mode | [ CPU ]")
            self._window.step1_btn.setText('[STEP 1] (C)\nStable')
        self._window.title.setText(str(conf.RTVersion()) + " | " + self.stabMode + " | " + self.yoloModel)
    
    @QtCore.Slot()
    def changeYoloModel(self):
        actName = QFileDialog.getOpenFileName(self._window, 'Select file to set Yolo Model.', "./Model/YOLOv4/weights")

        tempName = actName[0].split('/')

        if tempName[-1] != '':
        
            print(tempName[-1])
            self.yoloModel = tempName[-1]
            self._window.title.setText(str(conf.RTVersion()) + " | " + self.stabMode + " | " + self.yoloModel)
            conf.setYoloModel(self.yoloModel)
        else :
            print("[CANCEL] YoloModel change cancel.")

    @QtCore.Slot()
    def changeTIVPbMode(self):
        if self.TIVPmode == 1:
            self.TIVPmode = 2
            conf.setTIVPMode(2)
            self._window.bar_4.setText("Change TIVP Mode | [ Image ]")
            self._window.TVIPrinter_btn.setText('<TIV Printer> (I)')
        elif self.TIVPmode == 2:
            self.TIVPmode = 3
            conf.setTIVPMode(3)
            self._window.bar_4.setText("Change TIVP Mode | [ Real Time Display ]")
            self._window.TVIPrinter_btn.setText('<TIV Printer> (R)')
        elif self.TIVPmode == 3:
            self.TIVPmode = 1
            conf.setTIVPMode(1)
            self._window.bar_4.setText("Change TIVP Mode | [ Video ]")
            self._window.TVIPrinter_btn.setText('<TIV Printer> (V)')

    def changeTrackingSet(self):
        self.CTS_dialog = QDialog()
        ui_file_name = './View/CTS_dialog.ui'
        file = QFile(ui_file_name)
        loader = QUiLoader()
        self.CTS_dialog = loader.load(file)
        file.close()
        self.CTS_dialog.setWindowTitle('change Tracking Setting')
        self.CTS_dialog.CTS_trackingSetText.setText('Enter tracking setting : max_age, min_hits, iou_threshold')
        self.CTS_dialog.CTS_label_Trk1.setText('trackers 1 Set : Default `10,2,0.01`')
        self.CTS_dialog.CTS_label_Trk2.setText('trackers 2 Set : Default `10,2,0.1`')
        self.CTS_dialog.CTS_trackingSetText2.setText('Ex : max_age=10, min_hits=2, iou_threshold=0.01, type `10,2,0.01`. No space.')
        self.CTS_dialog.CTS_submitButton.setText('Submit')
        self.CTS_dialog.CTS_submitButton.clicked.connect(self.submitTrackingSet)

        self.CTS_dialog.show()

    def submitTrackingSet(self):
        if self.CTS_dialog.CTS_Edit_1.text() != '':
            trk1 = self.CTS_dialog.CTS_Edit_1.text()
            print("Trackers1 Set Changed : ",trk1)
            conf.setTrk1_Set(trk1)

        if self.CTS_dialog.CTS_Edit_2.text() != '':
            trk2 = self.CTS_dialog.CTS_Edit_2.text()        
            conf.setTrk2_Set(trk2)
            print("Trackers2 Set Changed : ",trk2)

        self.CTS_dialog.close()

    def setActionNameBtnText(self):
        out = ""
        counter = 0
        for i in range(0,len(self.actionName)):
            out = out + self.actionName[i]
            counter = counter + 1
            if counter == 23 :
                out = out + '\n'
                counter = 0

        self._window.ActionName_btn.setText("Edit ActionName\n[" + out + ']')

    @QtCore.Slot()
    def changeActionName(self) :

        self.actionName = self._window.ActionName_edit.text()

        self.cutinfo_txt = self.resultPath + self.actionName + "_cutInfo.txt"
        self.stab_input = self.originDataList
        self.stab_output = self.resultPath + self.actionName + "_stab.avi"
        self.stab_video = self.stab_output
        self.yolo_txt = self.resultPath+ self.actionName +"_stab_8cls.txt"
        self.tracking_csv = self.resultPath + self.actionName + ".csv"
        self.gateLineIO_txt = self.resultPath + self.actionName + "_IO.txt"
        self.gate_tracking_csv = self.resultPath + self.actionName + "_gate.csv"
        self.result_video = self.resultPath + self.actionName + "_result.avi"
        self.background_img = self.resultPath+ self.actionName +"_background.jpg"
        self.singelTIVpath = self.resultPath + self.actionName + "_TIV.csv"

        self.setActionNameBtnText()

        logger.info("[ChangeActionName] ->> actionName edit to :" + self.actionName)

    def flashActionName(self) :
        self.cutinfo_txt = self.resultPath + self.actionName + "_cutInfo.txt"
        self.stab_input = self.originDataList
        self.stab_output = self.resultPath + self.actionName + "_stab.avi"
        self.stab_video = self.stab_output
        self.yolo_txt = self.resultPath+ self.actionName +"_stab_8cls.txt"
        self.tracking_csv = self.resultPath + self.actionName + ".csv"
        self.gateLineIO_txt = self.resultPath + self.actionName + "_IO.txt"
        self.gate_tracking_csv = self.resultPath + self.actionName + "_gate.csv"
        self.result_video = self.resultPath + self.actionName + "_result.avi"
        self.background_img = self.resultPath+ self.actionName +"_background.jpg"
        self.singelTIVpath = self.resultPath + self.actionName + "_TIV.csv"
        
        self.setActionNameBtnText()
        self.setDroneFolderBtnText()
        self.setResultFolderBtnText()
        
    def cuttingWarning(self):
        err = False
        keyCount = 0 
        for i in range(0,len(self.cutInfoLsit)) :
            if self.cutInfoLsit[i].getKey() != -1 :
                keyCount = keyCount + 1
            if self.cutInfoLsit[i].getStart() >= self.cutInfoLsit[i].getEnd() and self.cutInfoLsit[i].getEnd() != -1 and self.cutInfoLsit[i].getStart() != -1:
                msgBox = QMessageBox()
                msgBox.setWindowTitle("Warning : Video Number : [" + str(i+1) + "]")
                msgBox.setText("Fream cutting fail.\nStart Frame must be early then End Frame.")
                msgBox.exec()
                err = True          
            
        if keyCount > 1 :
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Warning")
            msgBox.setText("KeyFream only can set one.\n" + "You have set" + str(keyCount) + 'KeyFream.')            
            msgBox.exec()
            err = True

        if keyCount < 1 :
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Warning")
            msgBox.setText("No KeyFream Setting. You must set one KeyFream.")
            msgBox.exec()
            err = True

        return err

    def issueFramePrint(self, frame):
        def RTcenter(points):
            ans = []
            
            x = (int(points[0]) + int(points[4]) ) / 2
            y = (int(points[1]) + int(points[5]) ) / 2
            ans.append(int(x))
            ans.append(int(y))
            return ans


        ### Add IO lines ###
        V2 = self.TIVioLines[0].split(",")
        V3 = self.TIVioLines[1].split(",")
        typecode = "XABCDEFGHIJKLMNOPQRSTUVW" 

        pts = []
        bordertype = []
        for i in range(0, len(V2)-1):
            bordertype.append(int(V2[i]))
            pts.append((int(V3[2*i]), int(V3[2*i+1])))

        for j in range(-1, len(bordertype)-1):
            if bordertype[j] > 0:
                cv2.line(frame, pts[j], pts[j+1], (0, 255, 0), 3)
                cv2.putText(frame, f"{typecode[abs(int(bordertype[j]))]}I", ((pts[j][0]+pts[j+1][0])//2, (pts[j][1]+pts[j+1][1])//2), cv2.FONT_HERSHEY_SIMPLEX,  0.5, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.putText(frame, f"{typecode[abs(int(bordertype[j]))]}I", ((pts[j][0]+pts[j+1][0])//2, (pts[j][1]+pts[j+1][1])//2), cv2.FONT_HERSHEY_SIMPLEX,  0.5, (0, 255, 0), 1, cv2.LINE_AA)

            elif bordertype[j] < 0:
                cv2.line(frame, pts[j], pts[j+1], (0, 0, 255), 3)    
                cv2.putText(frame, f"{typecode[abs(int(bordertype[j]))]}O", ((pts[j][0]+pts[j+1][0])//2, (pts[j][1]+pts[j+1][1])//2), cv2.FONT_HERSHEY_SIMPLEX,  0.5, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.putText(frame, f"{typecode[abs(int(bordertype[j]))]}O", ((pts[j][0]+pts[j+1][0])//2, (pts[j][1]+pts[j+1][1])//2), cv2.FONT_HERSHEY_SIMPLEX,  0.5, (0, 0, 255), 1, cv2.LINE_AA)

        for j in range(2, len(self.TIVioLines)):
            V4 = self.TIVioLines[j].split(",")
            k = 0
            for k in range(0, len(V4)-3, 2):
                cv2.line(frame, (int(V4[k]), int(V4[k+1])), (int(V4[k+2]), int(V4[k+3])), (255, 0, 0), 2)

        ### Add Issue Tracking ###

        findex = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        j = 0
        if len(self.TIVIsampleList) != 0 :
            while int(self.V[j][0] != self.TIVIsampleList[self.currentIssueIndex].split(',')[0])  :
                j += 1


        linePoints = self.V[j]
        centers = []
        temp = []
        for count in range (6,len(linePoints)):
            if len(temp) < 8 :
                temp.append(linePoints[count])
            else :
                centers.append(RTcenter(temp))            
                temp = []
                temp.append(linePoints[count])
        
        centerIndex = int(linePoints[1])
        k = 0
        while centerIndex <= findex and centerIndex <= int(linePoints[2]) :
 
            if k == len(centers) - 1 :
                cv2.circle(frame, (centers[k][0],centers[k][1]), 7, (0, 255, 255), -1)
                cv2.circle(frame, (centers[k][0],centers[k][1]), 11, (0, 255, 255), 2)
            elif k < len(centers) - 1 :
                cv2.circle(frame, (centers[k][0],centers[k][1]), 3, (127, 255, 0), 2)
            k += 1
            centerIndex += 1

        ### Add Tracling lines ###
        colors = [(0,0,255), (0,128,255), (0,255,255), (255,255,255), (0,255,0), (255,255,0), (255,0,255), (255,0,0)]        
        pos = np.zeros(8, np.int)
        typecode = "pumctbhg"

        for j in range(0, len(self.V) ):
            if findex >= int(self.V[j][1]) and findex <= int(self.V[j][2]):           
                idx = 6+8*(findex-int(self.V[j][1]))   
                k = 0
                for k in range(0, 8):
                    pos[k] = int(self.V[j][idx+k])
                    
                if pos[0] > 0:    

                    cv2.line(frame, (pos[0], pos[1]), (pos[2], pos[3]), (0, 0, 255), 4)
                    cv2.line(frame, (pos[2], pos[3]), (pos[4], pos[5]), (255, 0, 0), 4)
                    # cv2.line(frame, (pos[2], pos[3]), (pos[4], pos[5]), colors[typecode.find(str(self.V[j][5]))], 4)
                    cv2.line(frame, (pos[4], pos[5]), (pos[6], pos[7]), colors[typecode.find(str(self.V[j][5]))], 4)
                    cv2.line(frame, (pos[6], pos[7]), (pos[0], pos[1]), colors[typecode.find(str(self.V[j][5]))], 4)       

                    if self.displayType :
                        cv2.putText(frame, str(self.V[j][0])+self.V[j][3]+">"+self.V[j][4], (int((pos[0]+pos[4])/2)-50, int((pos[1]+pos[5])/2)+10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 3)
                        cv2.putText(frame, str(self.V[j][0])+self.V[j][3]+">"+self.V[j][4], (int((pos[0]+pos[4])/2)-50, int((pos[1]+pos[5])/2)+10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

                    elif int(self.V[j][0] == self.TIVIsampleList[self.currentIssueIndex].split(',')[0]) :
                        cv2.putText(frame, str(self.V[j][0])+self.V[j][3]+">"+self.V[j][4], (int((pos[0]+pos[4])/2)-50, int((pos[1]+pos[5])/2)+10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 3)
                        cv2.putText(frame, str(self.V[j][0])+self.V[j][3]+">"+self.V[j][4], (int((pos[0]+pos[4])/2)-50, int((pos[1]+pos[5])/2)+10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)


        return frame


class CutInfo() :
    def __init__(self):
        self.key = -1
        self.start = -1
        self.end = -1

    def setKey(self, key) :        
        self.key = int(key)
    
    def setStart(self, start) :
        self.start = int(start)
    
    def setEnd(self,end):
        self.end = int(end)

    def getKey(self):
        return self.key
    
    def getStart(self):
        return self.start

    def getEnd(self):
        return self.end

class ScheduleItem():
    def __init__(self):
        self.step = -1
        self.DisplayID = False
        self.Show = False
        
        self.actionName = ""
        self.resultPath = ""
        self.originDataList = ""


    def setActionName(self, newName):
        self.actionName = newName
    
    def setResultPath(self, newPath):
        self.resultPath = newPath
    
    def setOriginDataList(self, newOrgin):
        self.originDataList = newOrgin
    
    def getShortActionName(self):
        out = ""
        if len(self.actionName) > 12:
            out =self.actionName[0:12]+'...'+self.actionName[-4:]
        else:
            out = self.actionName
        return out


