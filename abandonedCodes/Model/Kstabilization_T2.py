import os
import time
import cv2
import numpy as np
import multiprocessing
from config import conf
from logs import logger

class StableVideo:
    # Type 2.3
    def __init__(self, inputVideoPath, cut_txt):
        self.cuttingData(cut_txt)
        self.inputVideoPath = inputVideoPath
        self.videolist = os.listdir(inputVideoPath)

        self.videolist.sort()

        ''' cv2 read video  setting ''' 
        cap = cv2.VideoCapture(os.path.join( os.path.abspath(inputVideoPath), self.videolist[0]))
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.targrt_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))   # get width from origin video
        self.target_hight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # get hight from origin video
        cap.release()

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

    def ECC(self, x) :
        ecc_cap_s = time.time()
        print("\t" + str(os.getpid()) )
        
        frame = x
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)        
        temp_warp = self.shrList[0]
        ecc_ecc_s = time.time()
        print("ECC_LOAD : " + str(ecc_ecc_s - ecc_cap_s))

        try:
            (cc, temp_warp) = cv2.findTransformECC(self.target_frame, frame_gray, temp_warp, self.warp_mode, self.criteria)
        except:
            (cc, temp_warp) = cv2.findTransformECC(self.target_frame, frame_gray, temp_warp, self.warp_mode, self.criteria, inputMask=None, gaussFiltSize=1)

        frame_aligned = cv2.warpPerspective (frame, temp_warp, (self.stabilization_sz[1], self.stabilization_sz[0]), flags=cv2.INTER_CUBIC + cv2.WARP_INVERSE_MAP)                
            
        self.shrList[0] = temp_warp
        print("\t" + "\t" + str(os.getpid()) + "\tECC_ECC : " + str(time.time() - ecc_ecc_s))

        return frame_aligned     
      

    def stableVideoWithOutputpath(self, outputpath, is_Show=False):
     
        # get target frame
        index = 0
        while index < len(self.videolist) :
            if self.cutInfoList[index].getKey() != -1 :
                cap = cv2.VideoCapture(os.path.join( os.path.abspath(self.inputVideoPath), self.videolist[index]))
                cap.set(cv2.CAP_PROP_POS_FRAMES, self.cutInfoList[index].getKey())
                ret, frame = cap.read()

                
                frameT = cv2.resize(frame, (self.output_width, self.output_hight), interpolation=cv2.INTER_CUBIC)
                self.target_frame = cv2.cvtColor(frameT, cv2.COLOR_BGR2GRAY)
                self.stabilization_sz = frameT.shape
                cap.release()
                break              
            index = index +1

        
        # start stabilization
        startTime = time.time()  
        out = cv2.VideoWriter(outputpath, self.fourcc, 9.99, (self.output_width, self.output_hight)) 
        self.currentIndex = 0 # video list index
        # multi = int(multiprocessing.cpu_count() / 2)
        multi = 7
        print("CPU : " + str(multi))
        output = []
        while self.currentIndex < len(self.videolist):
            if self.cutInfoList[self.currentIndex].getKey() == -1 and self.cutInfoList[self.currentIndex].getStart() == -1 and self.cutInfoList[self.currentIndex].getEnd() == -1 :
            
                # pass ignore video
                self.currentIndex = self.currentIndex + 1
            else :
                
                bigWhile = int(len(self.cutInfoList[self.currentIndex].pa3) / multi)
                less = int(len(self.cutInfoList[self.currentIndex].pa3) % multi)
                print("BIG WHILE : " + str(bigWhile))
                print("LESS : " + str(less))

                with multiprocessing.Pool(multi) as pool :
                    # make share list to store warp_matrix for multiprocessing
                    li = self.warp_matrix
                    shr = multiprocessing.Manager()
                    self.shrList = shr.list()
                    self.shrList.append(li)


                    frame_id = 0
                    cap = cv2.VideoCapture(os.path.join( os.path.abspath(self.inputVideoPath), self.videolist[index]))            
                    while bigWhile > 0 :
                        print ("/////"+ str(bigWhile) + "/////")                        
                        self.waitFrameList = shr.list()
                        
                        waitinput = self.cutInfoList[self.currentIndex].pa3[frame_id: (frame_id+multi)]
                        print(waitinput)
                        cap_s = time.time()
                        for i in range(0,len(waitinput)) :

                            cap.set(cv2.CAP_PROP_POS_FRAMES, waitinput[i]-1)
                            ret, frame = cap.read()
                            frame = cv2.resize(frame, (self.output_width, self.output_hight), interpolation=cv2.INTER_CUBIC)                            
                            self.waitFrameList.append(frame)
                        cap_e = time.time()
                        print("CAP : " +str(cap_e - cap_s))                        
                        frame_id = frame_id + multi                    
                        result = pool.map_async(self.ECC, self.waitFrameList )

                        store = time.time()                       
                        output = result.get()                          
                        WRI_S = time.time()
                        print("STORE : " + str( WRI_S - store ))            
                        for i in range(0,len(output)):
                            out.write(output[i])
                        bigWhile = bigWhile - 1      
                        WRI_E = time.time()
                        print("WRI : " + str(WRI_E - WRI_S))                  
                        print(self.shrList[0])

                    print ("///// less /////")
                    waitinput = self.cutInfoList[self.currentIndex].pa3[frame_id: frame_id+less]
                    self.waitFrameList = []
                    for i in range(0,len(waitinput)) :

                        cap.set(cv2.CAP_PROP_POS_FRAMES, waitinput[i]-1)
                        ret, frame = cap.read()
                        frame = cv2.resize(frame, (self.output_width, self.output_hight), interpolation=cv2.INTER_CUBIC)                        
                        self.waitFrameList.append(frame)

                    result = pool.map_async(self.ECC, self.waitFrameList)
                    pool.close()
                    pool.join()
                    output = result.get()
                    for i in range(0,len(output)):
                        out.write(output[i])                    
                pool.close()
                pool.join()

                self.currentIndex = self.currentIndex + 1
                cap.release()
                out.release()
        workingTime = time.time() - startTime
        # WRI_S = time.time()
        # for i in range(0,len(output)):
        #     out.write(output[i])
        # WRI_E = time.time()  
        print("WRI : " + str(WRI_E - WRI_S))
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

        pa3 = 0
        for i in range(0,len(self.cutInfoList)):
            if self.cutInfoList[i].getStart() != -1 :
                for k in range(self.cutInfoList[i].getStart(), self.cutInfoList[i].getEnd()) :
                    if pa3 % 3 == 0 :
                        self.cutInfoList[i].pa3.append(k)
                    pa3 = pa3 + 1

        for i in range(0,len(self.cutInfoList)):
            print ("Key :" + str(self.cutInfoList[i].getKey()) + "\t Start :"+ str(self.cutInfoList[i].getStart())
                    + "\t End :" + str(self.cutInfoList[i].getEnd()) + "\tpa3 :" + str(len(self.cutInfoList[i].pa3)))
                    
class CutInfo() :
    def __init__(self):
        self.key = -1
        self.start = -1
        self.end = -1
        self.pa3 = []

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

