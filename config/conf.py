# logger setting
# loggerLevel : degug, info, warning, error, critical 
loggerLevel = 'debug'
version = 'TrafficTrackerGUI - 3.1.0'

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

def getStabMode():
    f = open('./config/config.txt', 'r')
    lines = f.readlines()
    f.close()
    
    return lines[0].split('\n')[0]

def setStabMode(Mode):
    setConfigData(0, Mode)

def getYoloModel():
    f = open('./config/config.txt', 'r')
    lines = f.readlines()
    f.close()

    return lines[1].split('\n')[0]

def setYoloModel(Mode):
    setConfigData(1, Mode)