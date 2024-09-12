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
    # Type 0 NEW
    def __init__(self, inputVideoPath, cut_txt):
        logger.info("[Step 1] ->> Type 0_NEW. START.")
        self.cuttingData(cut_txt) # create cutting dataset
        self.inputVideoPath = inputVideoPath # folder path
        self.videolist = os.listdir(inputVideoPath) # files list in folder

        self.videolist.sort()

        ''' cv2 read video  setting '''
        cap = cv2.VideoCapture(os.path.join( os.path.abspath(inputVideoPath), self.videolist[0]))
        if cap.isOpened():
            self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.targrt_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))   # get width from origin video
            self.target_hight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # get hight from origin video
            self.target_fps = cap.get(cv2.CAP_PROP_FPS)                  # get FPS from origin video
        else :
            logger.warning(f"[Step 1(C)] Video read failed : {os.path.join( os.path.abspath(inputVideoPath), self.videolist[0])}")
            return
        cap.release()

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
        # self.termination_eps = 1e-5
        self.criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, self.number_of_iterations,  self.termination_eps)


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
        self.output_fps = 9.99
        out = cv2.VideoWriter(outputpath, self.fourcc, self.output_fps, (1920, 1080))
        self.currentVideoIndex = 0 # video list index
        self.currentFrameIndex = 0 # video frame index

        self.pa = 0 # Counting ever paNumber Frame for ECC
        # self.paNumber = 3 # % 3
        self.paNumber = round(self.target_fps / self.output_fps)  # % 3

        self.ECC_costTime = 0
        self.Read_costTime = 0
        self.Write_costTime = 0

        # start stabilization
        while self.currentVideoIndex < len(self.videolist) :
                while self.cutInfoList[self.currentVideoIndex].getKey() == -1 and self.cutInfoList[self.currentVideoIndex].getStart() == -1 and self.cutInfoList[self.currentVideoIndex].getEnd() == -1 :
                    # detect ignore video
                    self.currentVideoIndex = self.currentVideoIndex + 1
                    if self.currentVideoIndex >= len(self.videolist):
                        out.release()
                        workingTime = time.time() - startTime
                        logger.info("[Step 1] ->> Complete stable video : " +  self.videolist[self.currentVideoIndex-1])
                        logger.info(f"[Step 1] ->> [In % Out] FPS = paNumber : [ {self.target_fps} % {self.output_fps} ] = {self.paNumber}.")
                        logger.info("[Step 1] ->> ECC_costTime :" + str(self.ECC_costTime))
                        logger.info("[Step 1] ->> Read_costTime :" + str(self.Read_costTime))
                        logger.info("[Step 1] ->> Write_costTime :" + str(self.Write_costTime))
                        logger.info("[Step 1] ->> cost time :" + str(workingTime))
                        logger.info("[Step 1] ->> Output file :" + outputpath)
                        return
                    else :
                        logger.info("[Step 1] ->> PASS : " +  self.videolist[self.currentVideoIndex-1] )

                self.currentFrameIndex = self.cutInfoList[self.currentVideoIndex].getStart()
                cap = cv2.VideoCapture(os.path.join( os.path.abspath(self.inputVideoPath), self.videolist[self.currentVideoIndex]))
                cap.set(cv2.CAP_PROP_POS_FRAMES, self.cutInfoList[self.currentVideoIndex].getStart())

                logger.info("[Step 1] ->> Stabilize video :" + str(self.videolist[self.currentVideoIndex]))



                while cap.get(cv2.CAP_PROP_POS_FRAMES) < self.cutInfoList[self.currentVideoIndex].getEnd():
                    # print ("get Frame:" + str(  cap.get(cv2.CAP_PROP_POS_FRAMES )) + "\t" + str( self.currentFrameIndex))
                    self.IO_S = time.time()
                    ret, frame = cap.read()
                    self.IO_E = time.time()
                    self.Read_costTime = self.Read_costTime + (self.IO_E - self.IO_S)

                    if self.pa % self.paNumber == 0 :
                        frame = cv2.resize(frame, (1920, 1080), interpolation=cv2.INTER_CUBIC)
                        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


                        self.ECC_S = time.time()
                        try:
                            (cc, self.warp_matrix) = cv2.findTransformECC(self.target_frame, frame_gray, self.warp_matrix, self.warp_mode, self.criteria)
                            # print("cc : " + str(round(cc,5)))
                            # print(self.warp_matrix)
                        except:
                            (cc, self.warp_matrix) = cv2.findTransformECC(self.target_frame, frame_gray, self.warp_matrix, self.warp_mode, self.criteria, inputMask=None, gaussFiltSize=1)
                        self.ECC_E = time.time()
                        self.ECC_costTime = self.ECC_costTime + ( self.ECC_E - self.ECC_S)
                        frame_aligned = cv2.warpPerspective (frame, self.warp_matrix, (self.stabilization_sz[1], self.stabilization_sz[0]), flags=cv2.INTER_CUBIC + cv2.WARP_INVERSE_MAP)
                        self.write_S = time.time()
                        out.write(frame_aligned)
                        self.write_E = time.time()

                        self.Write_costTime =self.Write_costTime + (self.write_E - self.write_S)

                        print(str(int(cap.get(cv2.CAP_PROP_POS_FRAMES))) ,end='\r')
                        if is_Show :
                            cv2.imshow('frame', frame)
                            if cv2.waitKey(1) == ord('q'):
                                print("Step1 break for keyboard >q< .")
                                break

                    self.pa = self.pa + 1
                    self.currentFrameIndex = self.currentFrameIndex + 1

                self.currentVideoIndex = self.currentVideoIndex +1


        out.release()
        workingTime = time.time() - startTime
        if is_Show:
            cv2.destroyAllWindows() 
        logger.info("[Step 1] ->> Type 0 NEW.")
        logger.info(f"[Step 1] ->> [In % Out] FPS = paNumber : [ {self.target_fps} % {self.output_fps} ] = {self.paNumber}.")
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
        print("=======================================================")
        for i in range(0,len(self.cutInfoList)):
            print ("Key :" + str(self.cutInfoList[i].getKey()) + "\t Start :"+ str(self.cutInfoList[i].getStart())
                    + "\t End :" + str(self.cutInfoList[i].getEnd()) )
        print("=======================================================")


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

