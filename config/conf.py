# logger setting
# loggerLevel : degug, info, warning, error, critical 
loggerLevel = 'debug'

###### Config format #####
# [ 0 ] - Version Number : <3.2.1>
# [ 1 ] - Stable Mode : <CPU> | <GPU>
# [ 2 ] - Tracking trackers1 Setting max_age=10, min_hits=2, iou_threshold=0.01 : 10,2,0.01
# [ 3 ] - Tracking trackers2 Setting max_age=10, min_hits=2, iou_threshold=0.1 : 10,2,0.1
# [ 4 ] - Yolo Model Name : <last_100.pt> | <20211109172733_last_200_1920.pt> | <ect.>
# [ 5 ] - TIV ignore frame, ignore top and end frames to calculate TIV : <900>
# [ 6 ] - Extend Print Frame, When generating issue track vidoe, this number will be the extra length at the beginning and end of the video : <100>
# [ 7 ] - TIVPrint mode : <1> Video output mode | <2> background output mode | <3> Real Time Display.


# config index
ID_Version = 0
ID_StabMode = 1
ID_Trk1_Set = 2
ID_Trk2_Set = 3
ID_YoloModel = 4
ID_TIVingore = 5
ID_TIVextend = 6
ID_TIVPmode = 7
ID_Output_height = 8
ID_Output_width = 9

# config.txt Titles
configTitle = [
"Version",
"Step1_StabMode",
"Trk1_Set",
"Trk2_Set",
"YoloModel",
"TIVingoreFrames",
"TIVP_ExtendPrintFrame",
"TIVPmode",
"Output_height",
"Output_width"
]

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
            f.write(f"{configTitle[index]}={mode}"+'\n')
        else:
            f.write(lines[i])

    f.close()

def getConfData(lineNumber):
    f = open('./config/config.txt', 'r')
    data = f.readlines()
    f.close()
    lintStr = data[lineNumber].split('\n')[0]
    ans = lintStr.split('=')[1]
    return ans

def getVersion():
    return getConfData(ID_Version)

def getStabMode():
    return getConfData(ID_StabMode)

def setStabMode(mode):
    setConfigData(ID_StabMode, mode)

def getTrk1_Set():
    lineStr = getConfData(ID_Trk1_Set)
    tupleing = lineStr.split(',')
    return (int(tupleing[0]), int(tupleing[1]), float(tupleing[2]))
 
def setTrk1_Set(mode):
    mode = mode.replace(' ', '')
    sp = mode.split(',')
    ans = ""
    for i in range(0, len(sp)):
        ans += str(sp[i])
        if i != len(sp)-1:
            ans += ","
    setConfigData(ID_Trk1_Set, ans)

def getTrk2_Set():
    lineStr = getConfData(ID_Trk2_Set)
    tupleing = lineStr.split(',')
    return (int(tupleing[0]), int(tupleing[1]), float(tupleing[2]))

def setTrk2_Set(mode):
    mode = mode.replace(' ', '')
    sp = mode.split(',')
    ans = ""
    for i in range(0, len(sp)):
        ans += str(sp[i])
        if i != len(sp)-1:
            ans += ","
    setConfigData(ID_Trk2_Set, ans)

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

def getOutput_height():
    return int(getConfData(ID_Output_height))

def setOutput_height(size):
    setConfigData(ID_Output_height, size)

def getOutput_width():
    return int(getConfData(ID_Output_width))

def setOutput_width(size):
    setConfigData(ID_Output_width, size)

def RTVersion():
    ver = 'TrafficTrackerGUI - ' + getVersion()
    return ver

if __name__ == '__main__':
    print(getVersion())
    print(getStabMode())
    print(getTrk1_Set())
    print(getTrk2_Set())
    print(getYoloModel())
    print(getTIV_ignoreFrame())
    print(getTIVP_ExtendPrintFrame())
    print(getTIVPMode())
    print(RTVersion())