

import os
import time
import cv2
import numpy as np
import multiprocessing
import threading
import queue
from config import conf
from logs import logger

class Worker(threading.Thread):
    def __init__(self, id, workList, outList, output_width, output_hight, target_frame, warp_matrix, warp_mode, criteria, stabilization_sz ):
        threading.Thread.__init__(self)
        self.threadID = id
        self.queue = workList
        self.out2WaitList = outList

        self.output_width = output_width
        self.output_hight = output_hight
        self.target_frame = target_frame
        self.warp_matrix = warp_matrix
        self.warp_mode = warp_mode
        self.criteria = criteria
        self.stabilization_sz = stabilization_sz
        
        self.flag = True

    def stop(self) :
        self.flag = False

    def run(self):
        while self.flag == True:
            if self.queue.qsize() > 0 :
                data = []
                data = self.queue.get()
                
                frame = data[1]
                frame = cv2.resize(frame, (self.output_width, self.output_hight), interpolation=cv2.INTER_CUBIC)
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                try:
                    print("start /// Worker %d : %d " % (self.threadID, data[0]))


                    (cc, self.warp_matrix) = cv2.findTransformECC(self.target_frame, frame_gray, self.warp_matrix, self.warp_mode, self.criteria)

                    print("END /// Worker %d : %d " % (self.threadID, data[0]) )
                    print(time.time())
                    print("////")
                except:
                    
                    (cc, self.warp_matrix) = cv2.findTransformECC(self.target_frame, frame_gray, self.warp_matrix, self.warp_mode, self.criteria, inputMask=None, gaussFiltSize=1)

                frame_aligned = cv2.warpPerspective (frame, self.warp_matrix, (self.stabilization_sz[1], self.stabilization_sz[0]), flags=cv2.INTER_CUBIC + cv2.WARP_INVERSE_MAP)
                temp = [data[0],frame_aligned]
                self.out2WaitList.append(temp)

  


     
class StableVideo:

    def __init__(self, inputVideoPath, cut_txt):
        self.cuttingData(cut_txt)
        self.inputVideoPath = inputVideoPath
        self.videolist = os.listdir(inputVideoPath)
        self.videolist.sort()

        self.waitWorkList = queue.Queue()
        self.workFrameID = 0
        self.waitOutList = []
        self.outputFrameID = 0
        self.workerList = []

        ''' cv2 read video  setting ''' 
        self.cap = cv2.VideoCapture(os.path.join( os.path.abspath(inputVideoPath), self.videolist[0]))
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.targrt_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))   # get width from origin video
        self.target_hight = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # get hight from origin video

        if self.target_hight > 1080 :
            self.output_width = int(self.targrt_width / 2)
            self.output_hight = int(self.target_hight / 2)
        else:
            self.output_width = self.targrt_width
            self.output_hight = self.target_hight
        
        ''' stablize setting '''

        self.warp_mode = cv2.MOTION_HOMOGRAPHY
        self.warp_matrix = np.eye(3, 3, dtype=np.float32)

        # self.roi = [ [0, 0], [self.targrt_width, self.target_hight] ]        
        # self.roi_x = self.roi[0][0]
        # self.roi_y = self.roi[0][1]
        # self.roi_width = self.roi[1][0] - self.roi[0][0]
        # self.roi_height = self.roi[1][1] - self.roi[0][1]
        self.number_of_iterations = 500
        self.termination_eps = 1e-5    
        self.criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, self.number_of_iterations,  self.termination_eps)


    def ending( self, index, frame ) :
        if index == conf.enddingIndex and frame >= conf.enddingFrame :
            return True
        else :
            return False


    def checkWaitOutList(self):
        self.waitOutList.sort()
        while len(self.waitOutList) > 0 and self.outputFrameID == self.waitOutList[0][0] :
            self.out.write(self.waitOutList[0][1])
            self.waitOutList.pop(0)
            self.outputFrameID = self.outputFrameID + 1

    def stableVideoWithOutputpath(self, outputpath, is_Show=False):

        startTime = time.time()  
        self.out = cv2.VideoWriter(outputpath, self.fourcc, 9.99, (self.output_width, self.output_hight))

        count = 0
        
        index = 0 # input video number
        while index < len(self.videolist) :
            while self.cutInfoList[index].getKey() == -1 and self.cutInfoList[index].getStart() == -1 and self.cutInfoList[index].getEnd() == -1 and index < len(self.videolist):
                logger.info("[Step 1] ->> PASS : " +  self.videolist[index] )
                index = index + 1
                if index >= len(self.videolist) :
                    logger.info("[Step 1] ->> Complete stable video : " +  self.videolist[index-1])
                    self.cap.release()
                    self.out.release()
                    cv2.destroyAllWindows()

                    workingTime = time.time() - startTime
                    
                    logger.info("[Step 1] ->> cost time :" + str(workingTime))
                    logger.info("[Step 1] ->> Output file :" + outputpath)
                    
                    # Break
                    return

            self.cap = cv2.VideoCapture(os.path.join( os.path.abspath(self.inputVideoPath), self.videolist[index]))    
            if self.cutInfoList[index].getKey() != -1 :

                # keyTenP = int(conf.key_frame / 10)
                keyTenP = int(self.cutInfoList[index].getKey() / 10)
                now = 0
                print("[Load Key Frame] : <" + self.videolist[index] +'>')
                while self.cap.isOpened():  # capture key frame

                    ret, frame = self.cap.read()
                    if not ret :
                        break

                    if is_Show :
                        cv2.imshow('frame', frame)
                        if cv2.waitKey(1) == ord('q'): 
                            break
                    
                    if self.cap.get(cv2.CAP_PROP_POS_FRAMES) > ( now * keyTenP ) :
                        print("[ " + str(now*10) + "% ]")
                        now = now + 1 

                    if self.cap.get(cv2.CAP_PROP_POS_FRAMES) == self.cutInfoList[index].getKey():
                        
                        print ("GET TARGET\tframe: " + str(self.cap.get(cv2.CAP_PROP_POS_FRAMES)))
                        frame = cv2.resize(frame, (self.output_width, self.output_hight), interpolation=cv2.INTER_CUBIC)
                        self.target_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        self.stabilization_sz = frame.shape
                        logger.info( "[Step 1] ->> <" + self.videolist[index] + "> Key Frame : [" + str(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) +"]" )
                        break

            self.cap.set(cv2.CAP_PROP_POS_FRAMES,cv2.CAP_PROP_POS_FRAMES)

            if self.cutInfoList[index].getStart() > 1 :
                cutTenP = int(self.cutInfoList[index].getStart() / 10)
                now = 0
                print("[Run Cut Frame] : <"+ self.videolist[index] + '>')
                while self.cap.isOpened() :

                    ret, frame = self.cap.read()
                    if not ret :
                        break
                    
                    if is_Show :
                        cv2.imshow('frame', frame)
                        if cv2.waitKey(1) == ord('q'):                            
                            logger.info( "<" + self.videolist[index] + "> Cut Frame start in : [" + str(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) +"]" )
                            break
                    
                    if self.cap.get(cv2.CAP_PROP_POS_FRAMES) > ( now * cutTenP ) :
                        print("[ " + str(now*10) + "% ]")
                        now = now + 1                     

                    if self.cap.get(cv2.CAP_PROP_POS_FRAMES) == self.cutInfoList[index].getStart():
                        logger.info( "[Step 1] ->> <" + self.videolist[index] + "> Cut Frame start in : [" + str(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) +"]" )
                        break
            else :
                logger.info( "[Step 1] ->> <" + self.videolist[index] + "> Cut Frame start in : [1]" )
                
            logger.info("[Step 1] ->> Start stable video : " +  self.videolist[index] )            
            tenP = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT) / 10)
            now = 0

            for i in range(0, 3) :
                self.workerList.append(Worker(i*3, self.waitWorkList, self.waitOutList, self.output_width, self.output_hight, self.target_frame
                                               , self.warp_matrix, self.warp_mode, self.criteria, self.stabilization_sz))
            for i in range (0, 3):
                self.workerList[i].start()

            while self.cap.isOpened():
                ret, frame = self.cap.read()            

                if not ret :
                    logger.info("[Step 1] ->> Complete stable video : " +  self.videolist[index])
                    break
                
                if self.cap.get(cv2.CAP_PROP_POS_FRAMES) > ( now * tenP ) :
                    print("[ " + str(now*10) + "% ]")
                    now = now + 1

                if count % 3 == 0 :

                    # frame = cv2.resize(frame, (self.output_width, self.output_hight), interpolation=cv2.INTER_CUBIC)
                    # frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    # try:
                    #     (cc, warp_matrix) = cv2.findTransformECC(self.target_frame, frame_gray, self.warp_matrix, self.warp_mode, self.criteria)
                    # except:
                    #     (cc, warp_matrix) = cv2.findTransformECC(self.target_frame, frame_gray, self.warp_matrix, self.warp_mode, self.criteria, inputMask=None, gaussFiltSize=1)

                    
                    # frame_aligned = cv2.warpPerspective (frame, warp_matrix, (self.stabilization_sz[1], self.stabilization_sz[0]), flags=cv2.INTER_CUBIC + cv2.WARP_INVERSE_MAP)                
                    # frame_resized = frame_aligned[0:self.target_hight, 0:self.targrt_width]
                    # frame_resized = frame_aligned # for original size                                            
                    # frame_resized = cv2.resize(frame_resized, (self.output_width, self.output_hight))

                    # self.out.write(frame_aligned)


                    temp = [self.workFrameID, frame]
                    self.waitWorkList.put(temp)


                    self.checkWaitOutList()


                    

                    if self.cap.get(cv2.CAP_PROP_POS_FRAMES) >= self.cutInfoList[index].getEnd() :
                    # if self.ending(index, self.cap.get(cv2.CAP_PROP_POS_FRAMES)):
                        logger.info( "[Step 1] ->> <" + self.videolist[index] + "> Cut Frame End in : [" + str(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) +"]" )
                        logger.info("[Step 1] ->> Complete stable video : " +  self.videolist[index])
                        break

                    self.workFrameID = self.workFrameID + 1
                    print("FrameID : %d" % self.workFrameID )
                    print ("wait in  : %d" % (self.waitWorkList.qsize()))
                    print ("wiat out : %d" % (len(self.waitOutList)))

                    # if is_Show :
                    #     cv2.imshow('frame', frame_aligned)
                    #     if cv2.waitKey(1) == ord('q'):
                    #         logger.info( "[Step 1] ->> <" + self.videolist[index] + "> Cut Frame End in : [" + str(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) +"]" )
                    #         break
                
                count = count + 1

            index = index +1

        # while self.waitWorkList.qsize() > 0 :
        #     print ("wait in  : %d" % (self.waitWorkList.qsize()))
        #     print ("wiat out : %d" % (len(self.waitOutList)))
        #     self.checkWaitOutList()
        #     print()
        
        

        for i in range (0, 3):
            self.workerList[i].join()
        print ("NOOO : %d" % (len(self.waitOutList)))

        self.cap.release()
        self.out.release()
        cv2.destroyAllWindows()

        workingTime = time.time() - startTime


        logger.info("[Step 1] ->> cost time :" + str(workingTime))
        logger.info("[Step 1] ->> Output file :" + outputpath)

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

if __name__ == '__main__':
    print("::::Stabilization.py Example::::")
    print("> Please put the video which need to stabilez in same directrory,")
    print("> and make the file name as '1.mp4'.")
    print("> sand then there were be a file output as '2.avi'.")

    current_STAB = StableVideo('1.mp4')
    current_STAB.stableVideoWithOutputpath(outputpath='2.avi')


def stab_main(stab_input,stab_output,show,cut_txt):
    
    current_STAB = StableVideo(stab_input, cut_txt)
    current_STAB.stableVideoWithOutputpath(stab_output,show)

    





