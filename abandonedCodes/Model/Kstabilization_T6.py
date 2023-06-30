import os
import sys
from pickle import FALSE, TRUE
import time
import cv2
import numpy as np
import multiprocessing
from config import conf
from logs import logger

class StableVideo:
    # Type 6
    def __init__(self, inputVideoPath, cut_txt):
        logger.info("[Step 1] ->> Type 6. START.")
        self.cuttingData(cut_txt) # create cutting dataset
        self.inputVideoPath = inputVideoPath # folder path
        self.videolist = os.listdir(inputVideoPath) # files list in folder

        self.videolist.sort()

        ''' cv2 read video  setting ''' 
        cap = cv2.VideoCapture(os.path.join( os.path.abspath(inputVideoPath), self.videolist[0]))
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.targrt_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))   # get width from origin video
        self.target_hight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # get hight from origin video
        cap.release()

        # if self.target_hight > 1080 :
        #     self.output_width = int(self.targrt_width / 2)
        #     self.output_hight = int(self.target_hight / 2)
        # else:
        #     self.output_width = self.targrt_width
        #     self.output_hight = self.target_hight

        self.output_width = 1920
        self.output_hight = 1080
        
        ''' stablize setting '''

        self.warp_mode = cv2.MOTION_HOMOGRAPHY
        self.warp_matrix = np.eye(3, 3, dtype=np.float32)

        # self.roi = [ [0, 0], [self.targrt_width, self.target_hight] ]        
        # self.roi_x = self.roi[0][0]
        # self.roi_y = self.roi[0][1]
        # self.roi_width = self.roi[1][0] - self.roi[0][0]
        # self.roi_height = self.roi[1][1] - self.roi[0][1]
        self.number_of_iterations = 300
        self.termination_eps = 5*1e-4
        self.criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, self.number_of_iterations,  self.termination_eps)

    def ECC(self, x):
        print ("\t" + str(os.getpid()))
        
        frame = x
        frame = cv2.resize(frame, (1920, 1080), interpolation=cv2.INTER_CUBIC)
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        temp_warp = self.shr_Warp_matrix[0]
        # print(self.shr_Warp_matrix[0])
        start = time.time()

        try:
            (cc, temp_warp) = cv2.findTransformECC(self.target_frame, frame_gray, temp_warp, self.warp_mode, self.criteria)
            print("cc : " + str(round(cc,2)))
        except:
            (cc, temp_warp) = cv2.findTransformECC(self.target_frame, frame_gray, temp_warp, self.warp_mode, self.criteria, inputMask=None, gaussFiltSize=1)

        end = time.time()

        frame_aligned = cv2.warpPerspective (frame, temp_warp, (self.stabilization_sz[1], self.stabilization_sz[0]), flags=cv2.INTER_CUBIC + cv2.WARP_INVERSE_MAP)
        self.shr_Warp_matrix[0] = temp_warp
        # self.IOBuffer[x] = frame_aligned        
        print ( "\t\t" + str(os.getpid())+ "\t" + str(end - start) + "\tECC done." )
        
        return frame_aligned  
      
    def stableVideoWithOutputpath(self, outputpath, is_Show=False):
        # get target frame
        index = 0
        while index < len(self.videolist) :
            if self.cutInfoList[index].getKey() != -1 :
                cap = cv2.VideoCapture(os.path.join( os.path.abspath(self.inputVideoPath), self.videolist[index]))
                cap.set(cv2.CAP_PROP_POS_FRAMES, self.cutInfoList[index].getKey()-1)
                ret, frame = cap.read()
                
                frameT = cv2.resize(frame, (self.output_width, self.output_hight), interpolation=cv2.INTER_CUBIC)
                self.target_frame = cv2.cvtColor(frameT, cv2.COLOR_BGR2GRAY)
                self.stabilization_sz = frameT.shape
                cap.release()
                break              
            index = index +1
        
        # prepare
        startTime = time.time() 
        out = cv2.VideoWriter(outputpath, self.fourcc, 9.99, (1920, 1080)) 
        self.currentVideoIndex = 0 # video list index
        self.currentFrameIndex = 0 # video frame index
        self.KbufferSize = 100 # Frame number in Kbuffer
        self.Kbuffer = []
        self.pa = 0 # Counting ever paNumber Frame for ECC
        self.paNumber = 3 # % 3
        # self.multi = int(multiprocessing.cpu_count() / 2)
        self.multi = 8
        self.poolSize = 8

        
        self.ECC_costTime = 0
        self.Read_costTime = 0 
        self.Write_costTime = 0

        # start stabilization
        with multiprocessing.Pool(self.multi) as pool :
            # make share list to store warp_matrix for multiprocessing
            warp = self.warp_matrix
            shr = multiprocessing.Manager()
            self.shr_Warp_matrix = shr.list()
            self.shr_Warp_matrix.append(warp)

            while self.currentVideoIndex < len(self.videolist) :
                while self.cutInfoList[self.currentVideoIndex].getKey() == -1 and self.cutInfoList[self.currentVideoIndex].getStart() == -1 and self.cutInfoList[self.currentVideoIndex].getEnd() == -1 :
                    # detect ignore video
                    self.currentVideoIndex = self.currentVideoIndex + 1
                    if self.currentVideoIndex >= len(self.videolist):
                        out.release()
                        workingTime = time.time() - startTime
                        logger.info("[Step 1] ->> Complete stable video : " +  self.videolist[self.currentVideoIndex-1])
                        logger.info("[Step 1] ->> cost time :" + str(workingTime))
                        logger.info("[Step 1] ->> Output file :" + outputpath)
                        return
                    else :
                        logger.info("[Step 1] ->> PASS : " +  self.videolist[self.currentVideoIndex-1] )

                self.currentFrameIndex = self.cutInfoList[self.currentVideoIndex].getStart()-1
                cap = cv2.VideoCapture(os.path.join( os.path.abspath(self.inputVideoPath), self.videolist[self.currentVideoIndex]))
                cap.set(cv2.CAP_PROP_POS_FRAMES, self.cutInfoList[self.currentVideoIndex].getKey()-1)

                logger.info("[Step 1] ->> Stabilize video :" + str(self.videolist[self.currentVideoIndex]))
                unit = []
                self.IO_S = time.time()
                self.IO_E = 0
                while self.currentFrameIndex < self.cutInfoList[self.currentVideoIndex].getEnd() :
                    # print ("get Frame:" + str(  cap.get(cv2.CAP_PROP_POS_FRAMES )) + "\t" + str( self.currentFrameIndex))
                    ret, frame = cap.read()

                    if self.pa % self.paNumber == 0 :
                        unit.append(frame)
                        print("\t[Buffering frame : " + str(self.currentFrameIndex) + "]", end='\r')
                        
                    if len(unit) == self.poolSize or self.currentFrameIndex == self.cutInfoList[self.currentVideoIndex].getEnd()-1: 
                        # print(self.shr_Warp_matrix[0])
                        self.IO_E = time.time()
                        print("IO : " + str(self.IO_E - self.IO_S))
                        self.Read_costTime = self.Read_costTime + (self.IO_E - self.IO_S)
                        delta = time.time()                   
                        result = pool.map_async(self.ECC, unit)
                        result_S = time.time()
                        self.ECC_costTime = self.ECC_costTime + ( result_S - delta )
                        output = result.get()
                        result_E = time.time()
                        print ("Result (Start in pool.map): " + str(result_E - delta))
                        print ("Result : " + str(result_E - result_S))

                        for j in range(0,len(output)):
                            frame = cv2.resize(output[j], (1920, 1080), interpolation=cv2.INTER_CUBIC)
                            out.write(frame) 
                        write = time.time()
                        print("Write : " + str(write - result_E))
                        
                        
                        self.Write_costTime = self.Write_costTime + (write - result_E)
                        unit = []
                        self.IO_S = time.time()


                    self.pa = self.pa + 1
                    self.currentFrameIndex = self.currentFrameIndex + 1

                self.currentVideoIndex = self.currentVideoIndex +1
        out.release()
        workingTime = time.time() - startTime
        logger.info("[Step 1] ->> Type 6.")
        logger.info("[Step 1] ->> multiprocess :" + str(self.multi))
        logger.info("[Step 1] ->> poolSize :" + str(self.poolSize))
        logger.info("[Step 1] ->> ECC_costTime :" + str(self.ECC_costTime))
        logger.info("[Step 1] ->> Read_costTime :" + str(self.Read_costTime))
        logger.info("[Step 1] ->> Write_costTime :" + str(self.Write_costTime))
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
                    + "\t End :" + str(self.cutInfoList[i].getEnd()) )


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

