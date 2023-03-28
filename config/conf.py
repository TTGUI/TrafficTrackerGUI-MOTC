# logger setting
# loggerLevel : degug, info, warning, error, critical 
loggerLevel = 'debug'
version = 'TrafficTrackerGUI - 3.2.1'

###### Config format #####
# [ 0 ] - Stable Mode <CPU/GPU>
# [ 1 ] - Yolo Model Name <last_100.pt / 20211109172733_last_200_1920.pt / ect.>

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

def setStabMode(Mode):
    setConfigData(0, Mode)

def getYoloModel():
    return getConfData(1)

def setYoloModel(Mode):
    setConfigData(1, Mode)

def getTIVP_windoSize():
    return int(getConfData(2))

def setTIVP_windoSize(Mode):
    setConfigData(2, Mode)