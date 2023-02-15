# logger setting
# loggerLevel : degug, info, warning, error, critical 
loggerLevel = 'debug'
version = 'TrafficTrackerGUI - 3.0.1'

def getStabMode():
    f = open('./config/config.txt', 'r')
    lines = f.readlines()
    f.close()
    
    return lines[0]

def setStabMode(Mode):

    f = open('./config/config.txt', 'w')
    f.write(Mode)
    f.close()

getStabMode()