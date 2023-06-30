

from asyncore import write
import os
import time
import cv2
import numpy as np
from config import conf
from logs import logger

class StableVideo:
    # Type 0
    def __init__(self, inputVideoPath, cut_txt):
        logger.info("[Step 1] ->> Type 0. " ) 
        self.cuttingData(cut_txt)
        self.inputVideoPath = inputVideoPath
        self.videolist = os.listdir(inputVideoPath)

        self.videolist.sort()

        ''' cv2 read video  setting ''' 
        self.cap = cv2.VideoCapture(os.path.join( os.path.abspath(inputVideoPath), self.videolist[0]))
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.targrt_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))   # get width from origin video
        self.target_hight = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # get hight from origin video


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


    def ending( self, index, frame ) :
        if index == conf.enddingIndex and frame >= conf.enddingFrame :
            return True
        else :
            return False

    def ECC(self):
        pass

    def stableVideoWithOutputpath(self, outputpath, is_Show=False):

        startTime = 0 
        out = cv2.VideoWriter(outputpath, self.fourcc, 9.99, (self.output_width, self.output_hight))        
        count = 0
        
        index = 0
        while index < len(self.videolist) :
            while self.cutInfoList[index].getKey() == -1 and self.cutInfoList[index].getStart() == -1 and self.cutInfoList[index].getEnd() == -1 and index < len(self.videolist):
                logger.info("[Step 1] ->> PASS : " +  self.videolist[index] )
                index = index + 1
                if index >= len(self.videolist) :
                    logger.info("[Step 1] ->> Complete stable video : " +  self.videolist[index-1])
                    self.cap.release()
                    out.release()
                    cv2.destroyAllWindows()

                    workingTime = time.process_time() - startTime
                    
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

            self.ECC_cost = 0 
            self.read_cost = 0 
            self.write_cost = 0
            
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
            startTime = time.process_time()  
            while self.cap.isOpened():
                read_S = time.process_time()
                ret, frame = self.cap.read()            

                if not ret :
                    logger.info("[Step 1] ->> Complete stable video : " +  self.videolist[index])
                    break
                
                if self.cap.get(cv2.CAP_PROP_POS_FRAMES) > ( now * tenP ) :
                    print("[ " + str(now*10) + "% ]")
                    now = now + 1

                read_E = time.process_time()
                self.read_cost = self.read_cost + (read_E - read_S)
                if count % 3 == 0 :

                    frame = cv2.resize(frame, (self.output_width, self.output_hight), interpolation=cv2.INTER_CUBIC)
                    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                    ECC_S = time.process_time()
                    try:
                        (cc, warp_matrix) = cv2.findTransformECC(self.target_frame, frame_gray, self.warp_matrix, self.warp_mode, self.criteria)
                        
                    except:
                        (cc, warp_matrix) = cv2.findTransformECC(self.target_frame, frame_gray, self.warp_matrix, self.warp_mode, self.criteria, inputMask=None, gaussFiltSize=1)
                    ECC_E = time.process_time()
                    # print(str(ECC_E - ECC_S)+ "\tcc : " +str(cc)) 
                    print(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
                    self.ECC_cost = self.ECC_cost + (ECC_E - ECC_S)

                    write_S = time.process_time()
                    frame_aligned = cv2.warpPerspective (frame, warp_matrix, (self.stabilization_sz[1], self.stabilization_sz[0]), flags=cv2.INTER_CUBIC + cv2.WARP_INVERSE_MAP)                
                    # frame_resized = frame_aligned[0:self.target_hight, 0:self.targrt_width]
                    # frame_resized = frame_aligned # for original size                                            
                    # frame_resized = cv2.resize(frame_resized, (self.output_width, self.output_hight))

                    out.write(frame_aligned)
                    write_E = time.process_time()
                    self.write_cost = self.write_cost + (write_E - write_S)
                    if self.cap.get(cv2.CAP_PROP_POS_FRAMES) >= self.cutInfoList[index].getEnd() :
                    # if self.ending(index, self.cap.get(cv2.CAP_PROP_POS_FRAMES)):
                        logger.info( "[Step 1] ->> <" + self.videolist[index] + "> Cut Frame End in : [" + str(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) +"]" )
                        logger.info("[Step 1] ->> Complete stable video : " +  self.videolist[index])
                        break


                    if is_Show :
                        cv2.imshow('frame', frame_aligned)
                        if cv2.waitKey(1) == ord('q'):
                            logger.info( "[Step 1] ->> <" + self.videolist[index] + "> Cut Frame End in : [" + str(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) +"]" )
                            break
                
                count = count + 1

            index = index +1

        logger.info("[Step 1] ->> ECC_costTime :" + str(self.ECC_cost))
        logger.info("[Step 1] ->> Read_costTime :" + str(self.read_cost))
        logger.info("[Step 1] ->> Write_costTime :" + str(self.write_cost))

        self.cap.release()
        out.release()
        cv2.destroyAllWindows()

        workingTime = time.process_time() - startTime
        
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