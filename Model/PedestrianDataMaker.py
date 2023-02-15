

from asyncore import write
import os
import time
import cv2
import numpy as np
from config import conf
from logs import logger
"""
class Pedestrian:
    def __init__(self, inputVideoPath, cut_txt):
        logger.info("[Step 1] ->> Type 0. " ) 
        self.cuttingData(cut_txt)
        self.inputVideoPath = inputVideoPath
        self.videolist = os.listdir(inputVideoPath)
        self.videolist.sort()

        ''' cv2 read video  setting ''' 
        self.cap = cv2.VideoCapture(os.path.join( os.path.abspath(inputVideoPath), self.videolist[0]))
        self.targrt_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))   # get width from origin video
        self.target_hight = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # get hight from origin video
        self.frameCount = 1
        

    def process(self, resultPath, actionName):
        index = 0
        while index < len(self.videolist):
            while self.cutInfoList[index].getKey() == -1 and self.cutInfoList[index].getStart() == -1 and  self.cutInfoList[index].getEnd() == -1 :
                index = index + 1
                if index >= len(self.videolist):
                    print("\n")
                    return
            
            currentFrame = self.cutInfoList[index].getKey()-1
            cap = cv2.VideoCapture(os.path.join( os.path.abspath(self.inputVideoPath), self.videolist[index]))
            cap.set(cv2.CAP_PROP_POS_FRAMES, self.cutInfoList[index].getKey()-1)

            while cap.get(cv2.CAP_PROP_POS_FRAMES) < self.cutInfoList[index].getEnd():
                ret, frame = cap.read()
                if not ret :
                    break
                fileName = resultPath + actionName + "_"+ str(self.frameCount) + "_v" + str(index+1) + "_f" + str(int(cap.get(cv2.CAP_PROP_POS_FRAMES))) + ".jpg"

                cv2.imwrite(resultPath+"temp.jpg", frame)

                os.rename(resultPath+"temp.jpg", fileName)

                self.frameCount = self.frameCount + 1
                print(">>>>>[PedestrianDataMaker] => " + "Video( " + str(index+1) + " / " + str(len(self.videolist)) + " ) : Frame( " + str(cap.get(cv2.CAP_PROP_POS_FRAMES)) 
                        + " / " + str(self.cutInfoList[index].getEnd()) + " )" , end='\r')

                cap.set(cv2.CAP_PROP_POS_FRAMES, cap.get(cv2.CAP_PROP_POS_FRAMES) + 300 )

            index = index + 1
        print("\n")

    def cuttingData(self, cut_txt):
        f = open( cut_txt, 'r' )
        self.cutInfo = f.readlines()
        self.cutInfoList = []

        for i in range(0, len(self.cutInfo)) :
            string = ''
            count = 0
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
 
        for i in range(0,len(self.cutInfoList)):
            print ("Key :" + str(self.cutInfoList[i].getKey()) + "\t Start :"+ str(self.cutInfoList[i].getStart())
                    + "\t End :" + str(self.cutInfoList[i].getEnd()))
"""
class Pedestrian:
    def __init__(self, inputVideoPath):
        self.inputVideoPath = inputVideoPath
        self.videolist = os.listdir(inputVideoPath)
        self.videolist.sort()

        ''' cv2 read video  setting ''' 
        self.cap = cv2.VideoCapture(os.path.join( os.path.abspath(inputVideoPath), self.videolist[0]))
        self.targrt_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))   # get width from origin video
        self.target_hight = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # get hight from origin video
        self.frameCount = 1
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')


    def process(self):
        index = 0

        while index < len(self.videolist):

            
            cap = cv2.VideoCapture(os.path.join( os.path.abspath(self.inputVideoPath), self.videolist[index]))
            center = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) /2 , int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) /2)
            trans = cv2.getRotationMatrix2D(center, 180, 1)
            out = cv2.VideoWriter(os.path.join( os.path.abspath(self.inputVideoPath), str(index)+".avi"), self.fourcc, cap.get(cv2.CAP_PROP_FPS), (1920,1080))  
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret :
                    break

                
                frame = cv2.warpAffine(frame, trans, (1920,1080))
                out.write(frame)
                cv2.imshow("frame",frame)
                cv2.waitKey(1)

            cap.release()
            out.release()


            index = index + 1


    def cuttingData(self, cut_txt):
        f = open( cut_txt, 'r' )
        self.cutInfo = f.readlines()
        self.cutInfoList = []

        for i in range(0, len(self.cutInfo)) :
            string = ''
            count = 0
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
 
        for i in range(0,len(self.cutInfoList)):
            print ("Key :" + str(self.cutInfoList[i].getKey()) + "\t Start :"+ str(self.cutInfoList[i].getStart())
                    + "\t End :" + str(self.cutInfoList[i].getEnd()))

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


# def pedestrian_main(originDataList, resultPath, cutinfo_txt, actionName):
    
#     current_Pede = Pedestrian(originDataList, cutinfo_txt)
#     current_Pede.process(resultPath, actionName)
def pedestrian_main(originDataList, resultPath, cutinfo_txt, actionName):
    
    current_Pede = Pedestrian(originDataList)
    current_Pede.process()