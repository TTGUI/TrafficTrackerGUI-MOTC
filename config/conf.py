# logger setting
# loggerLevel : degug, info, warning, error, critical 
loggerLevel = 'debug'

###### Config format #####
# [ 0 ] - Version Number : <3.2.1>
# [ 1 ] - Stable Mode : <CPU> | <GPU>
# [ 2 ] - Yolo Model Name : <last_100.pt> | <20211109172733_last_200_1920.pt> | <ect.>
# [ 3 ] - TIV ignore frame, ignore top and end frames to calculate TIV : <900>
# [ 4 ] - Extend Print Frame, When generating issue track vidoe, this number will be the extra length at the beginning and end of the video : <100>
# [ 5 ] - TIVPrint mode : <1> Video output mode | <2> background output mode | <3> Real Time Display.

ID_Version = 0
ID_StabMode = 1
ID_YoloModel = 2
ID_TIVingore = 3
ID_TIVextend = 4
ID_TIVPmode = 5

def __init__():
    getStabMode() 

def setConfigData(index, mode):
    mode = str(mode)
    f = open('./config/config.txt', 'r')
    lines = f.readlines()
    f.close()

    f = open('./config/config.txt', 'w')
    for i in range(0, len(lines)):
        if i == index :
            f.write(mode+'\n')
        else:
            f.write(lines[i])

    f.close()

def getConfData(lineNumber):
    f = open('./config/config.txt', 'r')
    data = f.readlines()
    f.close()

    return data[lineNumber].split('\n')[0]

def getVersion():
    return getConfData(ID_Version)

def getStabMode():
    return getConfData(ID_StabMode)

def setStabMode(mode):
    setConfigData(ID_StabMode, mode)

def getYoloModel():
    return getConfData(ID_YoloModel)

def setYoloModel(mode):
    setConfigData(ID_YoloModel, mode)

def getTIV_ignoreFrame():
    return int(getConfData(ID_TIVingore))

def setTIV_ignoreFrame(frames):
    setConfigData(ID_TIVingore, frames)

def getTIVP_ExtendPrintFrame():
    return int(getConfData(ID_TIVextend))

def setTIVP_ExtendPrintFrame(frames):
    setConfigData(ID_TIVextend, frames)

def getTIVPMode():
    return int(getConfData(ID_TIVPmode))

def setTIVPMode(mode):
    setConfigData(ID_TIVPmode, mode)

def RTVersion():
    ver = 'TrafficTrackerGUI - ' + getVersion()
    return ver