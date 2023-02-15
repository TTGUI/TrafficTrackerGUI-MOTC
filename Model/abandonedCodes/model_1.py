from logs import logger
from config import conf
import os

path = './data/'
if not os.path.isdir(path):
    os.mkdir(path)

path = './result/'
if not os.path.isdir(path):
    os.mkdir(path)


print("model 1 : TEST TEST \n")

def M1F1():
    print("M1F1")
    Curremt = Test()
    Curremt.cuttingData()
    Curremt.play()

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


class Test() :

    def __init__(self):
        pass

    def play(self):
        for i in range(0,len(self.cutInfoList)):
            print ("Key :" + str(self.cutInfoList[i].getKey()) + "\t Start :"+ str(self.cutInfoList[i].getStart())
            + "\t End :" + str(self.cutInfoList[i].getEnd()))


    def cuttingData(self):
        f = open( conf.cutinfo_txt, 'r' )
        self.cutInfo = f.readlines()
        self.cutInfoList = []


        for i in range(0, len(self.cutInfo)) :
            string = ''
            count = 0
            ln = 0
            tempCut = CutInfo()
            for j in range(0, len(self.cutInfo[i])) :                

                if self.cutInfo[i][j] == '\t' or self.cutInfo[i][j] == '\n':
                    count = count + 1
                    
                    tempInt = int(string)
                    string = ''

                    if count == 1 :
                        tempCut.setKey(tempInt)
                    if count == 2 :
                        tempCut.setStart(tempInt)
                    if count == 3 :
                        tempCut.setEnd(tempInt)

                string = string + self.cutInfo[i][j]
            self.cutInfoList.append(tempCut)

        f.close()


