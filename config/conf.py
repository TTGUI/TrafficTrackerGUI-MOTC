# logger setting
# loggerLevel : degug, info, warning, error, critical 
loggerLevel = 'debug'
version = 'TrafficTrackerGUI - 3.2.1'

###### Config format #####
# [ 0 ] - Stable Mode <CPU/GPU>
# [ 1 ] - Yolo Model Name <last_100.pt / 20211109172733_last_200_1920.pt / ect.>
# [ 2 ] - TIV ignore frame <900>, ignore top and end frames to calculate TIV.
# [ 3 ] - Extend Print Frame <100>, When generating issue track vidoe, this number will be the extra length at the beginning and end of the video.

def __init__():
    getStabMode() 

def setConfigData(index, mode):
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

def getStabMode():
    return getConfData(0)

def setStabMode(mode):
    setConfigData(0, mode)

def getYoloModel():
    return getConfData(1)

def setYoloModel(mode):
    setConfigData(1, mode)

def getTIV_ignoreFrame():
    return int(getConfData(2))

def setTIV_ignoreFrame(frames):
    setConfigData(2, frames)

def getTIVP_ExtendPrintFrame():
    return int(getConfData(3))

def setTIVP_ExtendPrintFrame(frames):
    setConfigData(3, frames)