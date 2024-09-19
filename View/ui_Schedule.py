from Model.tool import TrackIntegrityVerificationTool
from logs import logger
import os
from PySide2.QtWidgets import QFileDialog
from PySide2.QtGui import QColor, QPalette


def ScheduleMode(mainWindow):
    if mainWindow.scheduleType == 'edit' :
        mainWindow.scheduleType = 'off'
        mainWindow._window.ScheduleMode_btn.setText('Schedule Mode <OFF>')
        mainWindow.set_button_text_color(mainWindow._window.ScheduleMode_btn, "block")

    else:
        mainWindow.scheduleType = 'edit'
        mainWindow._window.ScheduleMode_btn.setText('Schedule Mode <EDIT>')
        mainWindow.set_button_text_color(mainWindow._window.ScheduleMode_btn, "blue")
    mainWindow.renewScheduleBoard()


def StartSchedule(mainWindow):

    mainWindow.scheduleType = 'run'
    mainWindow._window.ScheduleMode_btn.setText('Schedule Mode <RUN>')
    cuurentTIVT = TrackIntegrityVerificationTool.TIVT()
    ScheduTIVList = []
    ScheduTIVList.append(cuurentTIVT.retTitle())
    logger.info(f"[Start Schedule][{mainWindow.scheduleName}]")

    for i in range(mainWindow.currentScheduleIndex ,len(mainWindow.ScheduleList)):
        mainWindow.currentScheduleIndex = i
        mainWindow.displayInfo(3)
        sch = '=====================================\n[Schedule ' + str(i+1) +' / ' + str(len(mainWindow.ScheduleList))+' ]'
        mainWindow.displayType = mainWindow.ScheduleList[i].DisplayID
        mainWindow.show = mainWindow.ScheduleList[i].Show
        
        mainWindow.actionName = mainWindow.ScheduleList[i].actionName
        mainWindow.resultPath = mainWindow.ScheduleList[i].resultPath
        mainWindow.droneFolderPath = mainWindow.ScheduleList[i].droneFolderPath
        mainWindow.flashActionName()

        if mainWindow.ScheduleList[i].step == 0:
            logger.info(sch + " - [STEP 0]")
            mainWindow.step0()
            return
        elif mainWindow.ScheduleList[i].step == 1:
            logger.info(sch + " - [STEP 1]")
            mainWindow.step1()
        elif mainWindow.ScheduleList[i].step == 2:
            logger.info(sch + " - [STEP 2]")
            mainWindow.step2()
        elif mainWindow.ScheduleList[i].step == 3:
            logger.info(sch + " - [STEP 3]")
            mainWindow.step3()                
        elif mainWindow.ScheduleList[i].step == 4:
            logger.info(sch + " - [STEP 4]")
            mainWindow.step4()                
        elif mainWindow.ScheduleList[i].step == 5:
            logger.info(sch + " - [STEP 5]")
            mainWindow.step5()
        elif mainWindow.ScheduleList[i].step == 6:
            logger.info(sch + " - [STEP 6]")
            mainWindow.step6()
        elif mainWindow.ScheduleList[i].step == 7:
            logger.info(sch + " - [STEP 7]")
            mainWindow.step7()
        elif mainWindow.ScheduleList[i].step == 8:
            logger.info(sch + " - [STEP 8 - TIV]")
            mainWindow.step8_singleTIV()
        elif mainWindow.ScheduleList[i].step == 9:
            logger.info(sch + " - [STEP 9 - TIVP]")
            mainWindow.step9_TIVPrinter()
    
    if mainWindow.scheduleTIVFolderPath == "" :
        mainWindow.scheduleTIVFile = "./result/" + "/" + mainWindow.scheduleName + "_TIV.csv"
    else :
        mainWindow.scheduleTIVFile = mainWindow.scheduleTIVFolderPath + "/" + mainWindow.scheduleName + "_TIV.csv"

    base, extension = os.path.splitext(mainWindow.scheduleTIVFile)
    k = 0
    while os.path.exists(mainWindow.scheduleTIVFile):
        k += 1
        mainWindow.scheduleTIVFile = f"{base}_{k}{extension}"

    fp = open( mainWindow.scheduleTIVFile, "w")

    for i in range (0,len(ScheduTIVList)):
        fp.write(ScheduTIVList[i])
        fp.write("\n")
    fp.close()

    print ("ALL Schedule Done.")

    mainWindow.scheduleType = 'off'
    mainWindow._window.ScheduleMode_btn.setText('Schedule Mode <OFF>')


def AddScheudle(mainWindow):
    tempItem = ScheduleItem()
    tempItem.DisplayID = mainWindow.displayType 
    tempItem.Show = mainWindow.show         
    tempItem.actionName = mainWindow.actionName
    tempItem.resultPath = mainWindow.resultPath
    tempItem.droneFolderPath = mainWindow.droneFolderPath
    tempItem.step = mainWindow.currentStep
    mainWindow.ScheduleList.insert(mainWindow.currentScheduleIndex +1, tempItem)
    if len(mainWindow.ScheduleList) == 1 :
        mainWindow.currentScheduleIndex = 0
    else :
        mainWindow.currentScheduleIndex = mainWindow.currentScheduleIndex +1

    mainWindow.displayInfo(3)
    
    
    print("AddSchedule "+ str(mainWindow.currentScheduleIndex+1) +" : [Step "+str(tempItem.step) + "] - [" + tempItem.actionName +"]")


def GetSchedule(mainWindow):
    mainWindow.loadCurrentScheduleItem()


def SetSchedule(mainWindow):
    tempItem = ScheduleItem()
    tempItem.DisplayID = mainWindow.displayType 
    tempItem.Show = mainWindow.show 
    
    tempItem.actionName = mainWindow.actionName
    tempItem.resultPath = mainWindow.resultPath
    tempItem.droneFolderPath = mainWindow.droneFolderPath
    tempItem.step = mainWindow.currentStep
    mainWindow.ScheduleList[mainWindow.currentScheduleIndex] = tempItem
    mainWindow.displayInfo(3)
    

def DeleteSchedule(mainWindow):
    if mainWindow.scheduleType == 'off' and mainWindow.TIVPmode == 3 : # TIVP real time mode edit by user.
        if len(mainWindow.TIVIsampleList) > 0 :
            mainWindow.TIVIsampleList.pop(mainWindow.currentIssueIndex)
            if mainWindow.currentIssueIndex > 0:
                mainWindow.currentIssueIndex = mainWindow.currentIssueIndex -1
            mainWindow.displayInfo(4)
    else :                                                 # Schedule edit mode.
        if len(mainWindow.ScheduleList) > 0 :
            mainWindow.ScheduleList.pop(mainWindow.currentScheduleIndex)
            if mainWindow.currentScheduleIndex > 0:
                mainWindow.currentScheduleIndex = mainWindow.currentScheduleIndex -1
            mainWindow.displayInfo(3)


def loadSchedule(mainWindow):
    if mainWindow.scheduleType == 'off' and mainWindow.TIVPmode == 3 and mainWindow.currentStep == 9:     # Load TIVP Issue
        mainWindow.loadTIVIssue()
    else:                                                                               # Normal Schedule Load
        mainWindow.scheduleLoadPath, filetype = QFileDialog.getOpenFileName(mainWindow._window,"Select Schedule File.", mainWindow.resultPath)
        
        if not mainWindow.scheduleLoadPath :
            print ("[Cancel] Schedule Load Cancel.")
        else:
            print ("Load Schedule File : " + mainWindow.scheduleLoadPath)
            mainWindow.scheduleName = mainWindow.scheduleLoadPath.split("/")[-1][:-13]
            mainWindow.scheduleTIVFolderPath = os.path.dirname(mainWindow.scheduleLoadPath)

            mainWindow.readScheduleFile()
            mainWindow.scheduleType = 'edit'
            mainWindow.set_button_text_color(mainWindow._window.ScheduleMode_btn, "blue")
            mainWindow._window.ScheduleMode_btn.setText('Schedule Mode <EDIT>')
            mainWindow.loadCurrentScheduleItem()
            mainWindow.displayInfo(3)
            mainWindow.renewScheduleBoard()

def loadCurrentScheduleItem(mainWindow):
    mainWindow.actionName = mainWindow.ScheduleList[mainWindow.currentScheduleIndex].actionName
    mainWindow.resultPath = mainWindow.ScheduleList[mainWindow.currentScheduleIndex].resultPath
    mainWindow.droneFolderPath = mainWindow.ScheduleList[mainWindow.currentScheduleIndex].droneFolderPath
    mainWindow.show = mainWindow.ScheduleList[mainWindow.currentScheduleIndex].Show
    mainWindow.displayType = mainWindow.ScheduleList[mainWindow.currentScheduleIndex].DisplayID

    if mainWindow.show:
        mainWindow._window.show_btn.setText('Show')
    else :
        mainWindow._window.show_btn.setText('BackGround')
    if mainWindow.displayType:
        mainWindow._window.DisplayType_btn.setText('Display ID')
    else :
        mainWindow._window.DisplayType_btn.setText('Hide ID')

    mainWindow.flashActionName()


def saveSchedule(mainWindow):
    if mainWindow.scheduleType == 'off' and mainWindow.TIVPmode == 3 and mainWindow.currentStep == 9:     # Save TIVP Issue
        mainWindow.saveTIVIssue()
    else:                                                                               # Normal Schedule Save
        filetype = ("_Schedule.txt")
        temp = QFileDialog.getSaveFileName(mainWindow._window,"Save Schedule File.", "", filetype)
        if temp[0] != "":
            mainWindow.scheduleSavePath = temp[0] + temp[1]
            mainWindow.scheduleName = temp[0].split("/")[-1]
            mainWindow.writeScheduleFile()
            print ("Save Schedule File : " + mainWindow.scheduleSavePath)
            mainWindow.scheduleTIVFolderPath = os.path.dirname(mainWindow.scheduleSavePath)
            mainWindow.displayInfo(3)
        else :
            print ("[Cancel] Schedule Save Cancel.")

def readScheduleFile(mainWindow):
    def encodeFile():
        encodings = ['utf-8', 'cp950']
        for e in encodings:
            try:
                with open(mainWindow.scheduleLoadPath, 'r', encoding=e) as f:
                    return f.readlines()
            except UnicodeDecodeError:
                pass
        print(f'Could not read {mainWindow.scheduleLoadPath} with any encoding.')
        return None
    # f = open(mainWindow.scheduleLoadPath, 'r', encoding='utf-8')
    lineData = encodeFile()
    mainWindow.ScheduleList = []

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

        mainWindow.ScheduleList.append(tempSchedule)

def set_button_text_color(mainWindow, button, color):
    palette = button.palette()
    palette.setColor(QPalette.ButtonText, QColor(color))
    button.setPalette(palette)

    
def writeScheduleFile(mainWindow):
    for i in range(0, len(mainWindow.ScheduleList)):
        f = open(mainWindow.scheduleSavePath, 'w', encoding='utf-8')

        for i in range(0,len(mainWindow.ScheduleList)) :
            if mainWindow.ScheduleList[i].DisplayID:
                display = 1
            else:
                display = 0

            if mainWindow.ScheduleList[i].Show:
                show = 1
            else :
                show = 0

            out = ''
            out = out + str(mainWindow.ScheduleList[i].step) + '\t'
            out = out + str(display) + '\t'
            out = out + str(show) + '\t'
            out = out + mainWindow.ScheduleList[i].actionName + '\t'
            out = out + mainWindow.ScheduleList[i].resultPath + '\t'
            out = out + mainWindow.ScheduleList[i].droneFolderPath + '\n'
            
            f.write(out)
        f.close()

def renewScheduleBoard(mainWindow):
    if mainWindow.scheduleType == 'off' and mainWindow.TIVPmode == 3 and mainWindow.currentStep == 9 : # TIVP real time mode edit by user.
        mainWindow._window.DeleteSchedule_btn.setText('Delete TIV Issue')
        mainWindow._window.LoadScheduleFile_btn.setText('Load TIV File')
        mainWindow._window.SaveScheduleFile_btn.setText('Save TIV File')
        chColor2 = "blue"

    else :
        mainWindow._window.DeleteSchedule_btn.setText('Delete Schedule')
        mainWindow._window.LoadScheduleFile_btn.setText('Load Schedule File')
        mainWindow._window.SaveScheduleFile_btn.setText('Save Schedule File')
        chColor2 = "black"

    mainWindow.set_button_text_color(mainWindow._window.SaveScheduleFile_btn, chColor2)
    mainWindow.set_button_text_color(mainWindow._window.LoadScheduleFile_btn, chColor2)
    mainWindow.set_button_text_color(mainWindow._window.DeleteSchedule_btn, chColor2)
    mainWindow.set_button_text_color(mainWindow._window.show_btn, chColor2)
    mainWindow.set_button_text_color(mainWindow._window.DisplayType_btn, chColor2)
    mainWindow.set_button_text_color(mainWindow._window.showTracking_btn, chColor2)

    if mainWindow.scheduleType == 'edit':
        chColor = "blue"
    else:
        chColor = "black"
    mainWindow.set_button_text_color(mainWindow._window.step0_btn, chColor)
    mainWindow.set_button_text_color(mainWindow._window.step1_btn , chColor)
    mainWindow.set_button_text_color(mainWindow._window.step2_btn , chColor)
    mainWindow.set_button_text_color(mainWindow._window.step3_btn , chColor)
    mainWindow.set_button_text_color(mainWindow._window.step4_btn , chColor)
    mainWindow.set_button_text_color(mainWindow._window.step5_btn , chColor)
    mainWindow.set_button_text_color(mainWindow._window.step6_btn , chColor)
    mainWindow.set_button_text_color(mainWindow._window.step7_btn , chColor)
    mainWindow.set_button_text_color(mainWindow._window.TIV_btn , chColor)
    mainWindow.set_button_text_color(mainWindow._window.TIVPrinter_btn , chColor)

class ScheduleItem():
    def __init__(mainWindow):
        mainWindow.step = -1
        mainWindow.DisplayID = False
        mainWindow.Show = False
        
        mainWindow.actionName = ""
        mainWindow.resultPath = ""
        mainWindow.droneFolderPath = ""


    def setActionName(mainWindow, newName):
        mainWindow.actionName = newName
    
    def setResultPath(mainWindow, newPath):
        mainWindow.resultPath = newPath
    
    def setdroneFolderPath(mainWindow, newOrgin):
        mainWindow.droneFolderPath = newOrgin
    
    def getShortActionName(mainWindow):
        out = ""
        if len(mainWindow.actionName) > 12:
            out =mainWindow.actionName[0:12]+'...'+mainWindow.actionName[-4:]
        else:
            out = mainWindow.actionName
        return out
