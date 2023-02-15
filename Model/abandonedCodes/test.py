
from itertools import count
import random
import multiprocessing
import time
import os
import cv2
import numpy as np


class do():
    def __init__(self):
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = []
        self.fuck = "FUCK"
        self.inputpath = "./data/BUG/getFrames.mp4"

        self.warp_mode = cv2.MOTION_HOMOGRAPHY
        self.warp_matrix = np.eye(3, 3, dtype=np.float32)

        self.number_of_iterations = 500
        self.termination_eps = 1e-5    
        self.criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, self.number_of_iterations,  self.termination_eps)
    
    def f2(self,d, l):
        d[1] = '9'
        d['2'] = 7
        d[0.85] = None
        l.reverse()
        print(os.getpid())

    def thedo1(self):
        with multiprocessing.Manager() as manager:
            d = manager.dict()
            l = manager.list(range(10))
            print(d)
            
            p = multiprocessing.Process(target=self.f2, args=(d, l))
            p.start()
            p.join()

            print(d)
            print(l)

    def f(self, x):
        # print(str(os.getpid()) + "\t" +str(x) )
        # x.append(os.getpid())
        sleeptime = random.randint(1,2)
        time.sleep(sleeptime)
        print("%d : %d : %s" % (x,sleeptime,self.fuck))
        # return os.getpid()
        return x 

    def thedo2(self):
        with multiprocessing.Pool(multiprocessing.cpu_count()) as pool :
            
            output = []
            base = multiprocessing.cpu_count()
            i = 0
            self.x = [*range(base*i, base*(i+1))]

            i=i+1

            while i < 5 :
              
                
                print (self.x)
                result = pool.map_async(self.f, self.x)
                print(result.get())



                print("with end")
                output = output + result.get()

                self.x = [*range(base*i, base*(i+1))]
                i=i+1

            pool.close()
            pool.join()
            print(output)

    def f3(self,x):
        # print(">>>"+str(os.getpid())+ str(x))
        time.sleep(1)
        print(self.fuck)
        return x[0]

    def thedo3(self):
        with multiprocessing.Pool(multiprocessing.cpu_count()) as pool :
            self.fuck = "FUUUCKKK"
            output = []
            
            i = 0
            self.x = []
            self.id = 0
            
            for k in range (30):
                temp = []
                temp.append(self.id)
                for j in range(7):                    
                    temp.append(random.randint(1,100))
                self.id = self.id +1
                self.x.append(temp)


            while i < 3 :
                print (self.x)
                result = []
                result = pool.map_async(self.f3, self.x)
                print(result.get())
                print(type(result))
                print("with end")
                output = output + result.get()

                for k in range (30):
                    print(self.id)
                    temp = []
                    temp.append(self.id)
                    for j in range(7):                    
                        temp.append(random.randint(1,100))
                    self.id = self.id +1
                    self.x.append(temp)

                i=i+1

            pool.close()
            pool.join()
            print(output)        
    
    def f4(self, x) :
        cap = cv2.VideoCapture(self.inputpath)
        print ("\t" + str(x) + "\t" + str(os.getpid()))
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_POS_FRAMES, x)
            ret, frame = cap.read()
            frame = cv2.putText(frame, str(x), (50,150), cv2.FONT_HERSHEY_COMPLEX, 5, (0,0,255), 2)
            cap.release()
            return frame
        # cv2.waitKey(1)
        cap.release()
        
        return frame

    def thedo4(self):
        multi = multiprocessing.cpu_count()
        multi = 8
        output = []
        frame = 0
        cap = cv2.VideoCapture(self.inputpath)
        allframe = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))        
        cap.release()
        bigWhile = int(allframe / multi)
        less = int(allframe % multi)
        start = time.time()
        print("All frame : " + str(allframe))
        print("less : " + str(less))

        
        with multiprocessing.Pool(multi) as pool :
            with multiprocessing.Manager() as manager : 

                while bigWhile > 0 :
                    print ("/////"+ str(bigWhile) + "/////")
                    waitinput = [*range(frame,frame+multi)]
                    frame = frame + multi
                    result = pool.map_async(self.f4, waitinput)
                    output = output + result.get()                

                    bigWhile = bigWhile - 1

                print ("///// less /////")
                waitinput = [*range(frame,frame+less)]
                result = pool.map_async(self.f4, waitinput)
                output = output + result.get()       
            
        pool.close()
        pool.join()

        out = cv2.VideoWriter("./data/output.avi",self.fourcc, 29.97,(width,height))
        print(len(output))
        end = time.time() - start
        p2 = time.time()
        print(end)
        for i in range(0,len(output)):
            out.write(output[i])
        out.release()
        end = time.time() - p2
        print(end)               

    def f5(self, x) :
        cap = cv2.VideoCapture(self.inputpath)
        # print ("\t" + str(x) + "\t" + str(os.getpid()))
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_POS_FRAMES, x)
            ret, frame = cap.read()
            # frame = cv2.putText(frame, str(x), (50,150), cv2.FONT_HERSHEY_COMPLEX, 5, (0,0,255), 2)
            frame = cv2.resize(frame, (self.width, self.height), interpolation=cv2.INTER_CUBIC)
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            temp_warp = self.shrList[0]
            try:
                (cc, temp_warp) = cv2.findTransformECC(self.target_frame, frame_gray, temp_warp, self.warp_mode, self.criteria)
            except:
                (cc, temp_warp) = cv2.findTransformECC(self.target_frame, frame_gray, temp_warp, self.warp_mode, self.criteria, inputMask=None, gaussFiltSize=1)

            frame_aligned = cv2.warpPerspective (frame, temp_warp, (self.stabilization_sz[1], self.stabilization_sz[0]), flags=cv2.INTER_CUBIC + cv2.WARP_INVERSE_MAP)                
            
            self.shrList[0] = temp_warp
            cap.release()
            return frame_aligned
        
        cap.release()        
        return
        
    def thedo5(self):
        # multi = multiprocessing.cpu_count()
        multi = 7
        output = []
        frame = 0
        cap = cv2.VideoCapture(self.inputpath)
        allframe = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)/2)
        self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)/2)        
        
        bigWhile = int(allframe / multi)
        less = int(allframe % multi)
        
        ret, frameT = cap.read() 
        frameT = cv2.resize(frameT, (self.width, self.height), interpolation=cv2.INTER_CUBIC)
        self.target_frame = cv2.cvtColor(frameT, cv2.COLOR_BGR2GRAY)
        self.stabilization_sz = frameT.shape
        cap.release()
        li = self.warp_matrix
        shr = multiprocessing.Manager()
        self.shrList = shr.list()
        self.shrList.append(li)

        start = time.time()
        with multiprocessing.Pool(multi) as pool :
                        
            while bigWhile > 0 :
                print ("/////"+ str(bigWhile) + "/////")
                waitinput = [*range(frame,frame+multi)]
                frame = frame + multi
                result = pool.map_async(self.f5, waitinput)
                output = output + result.get()                

                bigWhile = bigWhile - 1
                
                print(self.shrList[0])
            print ("///// less /////")
            waitinput = [*range(frame,frame+less)]
            result = pool.map_async(self.f5, waitinput)
            output = output + result.get()       
            
        pool.close()
        pool.join()

        out = cv2.VideoWriter("./data/output.avi",self.fourcc, 29,(self.width,self.height))
        print(len(output))
        end = time.time() - start
        p2 = time.time()
        print(end)
        for i in range(0,len(output)):
            out.write(output[i])
        out.release()
        end = time.time() - p2
        print(end)               
        
    def f6(self, x) :
        cap = cv2.VideoCapture(self.inputpath)
        print ("\t" + str(x) + "\t" + str(os.getpid()))
        ecc_s = time.time()
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_POS_FRAMES, x)
            ret, frame = cap.read()
            # frame = cv2.putText(frame, str(x), (50,150), cv2.FONT_HERSHEY_COMPLEX, 5, (0,0,255), 2)
            frame = cv2.resize(frame, (self.width, self.height), interpolation=cv2.INTER_CUBIC)
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            temp_warp = self.shrList[0]
            try:
                (cc, temp_warp) = cv2.findTransformECC(self.target_frame, frame_gray, temp_warp, self.warp_mode, self.criteria)
            except:
                (cc, temp_warp) = cv2.findTransformECC(self.target_frame, frame_gray, temp_warp, self.warp_mode, self.criteria, inputMask=None, gaussFiltSize=1)

            frame_aligned = cv2.warpPerspective (frame, temp_warp, (self.stabilization_sz[1], self.stabilization_sz[0]), flags=cv2.INTER_CUBIC + cv2.WARP_INVERSE_MAP)                
            
            self.shrList[0] = temp_warp

            ecc_e = time.time()
            print ("\t\t" + str(x) + "\t" + str(ecc_e - ecc_s))
            cap.release()
            return frame_aligned
        
        cap.release()
        
        return frame
        
    def thedo6(self):
        multi = int(multiprocessing.cpu_count() / 2)
        # multi = 8
        print(multi)
        print(type(multi))
        output = []
        frame = 0
        cap = cv2.VideoCapture(self.inputpath)
        allframe = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)/2)
        self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)/2)

        waitWorkPa3 = self.pa3(0,allframe)

        bigWhile = int(len(waitWorkPa3) / multi)
        less = int(len(waitWorkPa3) % multi)       
        
        ret, frameT = cap.read() 
        frameT = cv2.resize(frameT, (self.width, self.height), interpolation=cv2.INTER_CUBIC)
        self.target_frame = cv2.cvtColor(frameT, cv2.COLOR_BGR2GRAY)
        self.stabilization_sz = frameT.shape
        cap.release()

        li = self.warp_matrix
        shr = multiprocessing.Manager()
        self.shrList = shr.list()
        self.shrList.append(li)

        start = time.time()
        with multiprocessing.Pool(multi) as pool :
                        
            while bigWhile > 0 :
                print ("/////"+ str(bigWhile) + "/////")                

                waitinput = waitWorkPa3[frame: (frame+multi)]
                frame = frame + multi
                result = pool.map_async(self.f6, waitinput)
                output = output + result.get()                

                bigWhile = bigWhile - 1
                
                print(self.shrList[0])
            print ("///// less /////")
            waitinput = waitWorkPa3[frame: frame+less]
            result = pool.map_async(self.f6, waitinput)
            output = output + result.get()       
            
        pool.close()
        pool.join()
        end = time.time() - start
        outputName = "./data/output_6_" + str(end) + ".avi"
        out = cv2.VideoWriter(outputName,self.fourcc, 29,(self.width,self.height))
        print(len(output))
        
        p2 = time.time()
        print(end)
        for i in range(0,len(output)):
            out.write(output[i])
        out.release()
        end = time.time() - p2
        print(end)               

    def theT(self):
        a =5
        b =30
        li = [*range(0,108)]
        li = self.pa3(0,len(li))
        print(type(li))
        print(li)
        print(li[1:5])
        li = li[1:5]
        print(li)

    def pa3(self, start, end) :
        list = []
        k = 0

        for i in range(int(start), int(end)) :
            if k % 1 == 0 :
                list.append(i)
            k = k + 1

        return list

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

    def f7(self, x):
        print ("\t" + str(os.getpid()))
        start = time.time()
        frame = x
        frame = cv2.resize(frame, (self.width, self.height), interpolation=cv2.INTER_CUBIC)
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        temp_warp = self.shr_Warp_matrix[0]
        try:
            (cc, temp_warp) = cv2.findTransformECC(self.target_frame, frame_gray, temp_warp, self.warp_mode, self.criteria)
        except:
            (cc, temp_warp) = cv2.findTransformECC(self.target_frame, frame_gray, temp_warp, self.warp_mode, self.criteria, inputMask=None, gaussFiltSize=1)

        frame_aligned = cv2.warpPerspective (frame, temp_warp, (self.stabilization_sz[1], self.stabilization_sz[0]), flags=cv2.INTER_CUBIC + cv2.WARP_INVERSE_MAP)
        self.shr_Warp_matrix[0] = temp_warp
        # self.IOBuffer[x] = frame_aligned
        end = time.time()
        print ( "\t\t" + str(os.getpid())+ "\t" + str(end - start) + "\tECC done." )

        return frame_aligned

    def thedo7(self):
        cap = cv2.VideoCapture(self.inputpath)
        self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)/2)
        self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)/2)
        ret, frameT = cap.read() 
        frameT = cv2.resize(frameT, (self.width, self.height), interpolation=cv2.INTER_CUBIC)
        self.target_frame = cv2.cvtColor(frameT, cv2.COLOR_BGR2GRAY)
        self.stabilization_sz = frameT.shape
        cap.release()


        cap = cv2.VideoCapture(self.inputpath)
        inputFrames = []
        x = 0  
        while cap.isOpened() :
            ret, frame = cap.read()
            if not ret :
                break
            if x % 3 == 0 :
                inputFrames.append(frame)
            x=x+1
            print (x)
        cap.release()
        allFrames = len(inputFrames)
        print("Frame : " + str(allFrames))
             

        multi = 11
        ECC_s  = 0 
        ECC_e = 0
        out = cv2.VideoWriter("./data/output_7.avi" ,self.fourcc, 29,(self.width,self.height))
        with multiprocessing.Pool(multi) as pool :
            shr = multiprocessing.Manager()
            self.shr_Warp_matrix = shr.list()
            self.shr_Warp_matrix.append(self.warp_matrix)
            self.IOBuffer = shr.list()

            allCount = 0
            less = 0  
            ECC_s = time.time()
            output = []
            
            while allCount < allFrames :
                IOBuffer = []
                if allCount + multi >= allFrames:
                    less = allCount + multi - allFrames 
                    IOBuffer =  inputFrames[allCount: (allCount+less)]
                else:
                    IOBuffer =  inputFrames[allCount: (allCount+multi)]

                print (allCount)
                
                allCount = allCount + multi
                # trigger = [*range(0,len(self.IOBuffer))]

                # result = pool.map_async(self.f7, IOBuffer)                
                # output = result.get()
                output = pool.map(self.f7, IOBuffer)
                for i in range(0,len(output)):
                    frame = cv2.resize(output[i], (self.width, self.height), interpolation=cv2.INTER_CUBIC)
                    out.write(frame) 
                print(self.shr_Warp_matrix[0])

                # for i in range(0,len(self.IOBuffer)):

                #     frame = cv2.resize(self.IOBuffer[i], (self.width, self.height), interpolation=cv2.INTER_CUBIC)
                #     # cv2.imshow("OUT",frame)
                #     # cv2.waitKey(1)
                #     out.write(frame)
            
            ECC_e = time.time()
            print(str(ECC_e - ECC_s))
            print("ALL ECC cost :" + str(ECC_e - ECC_s))
            # name = "./data/output_7_" + str(int(ECC_e - ECC_s)) + ".avi"
            # out = cv2.VideoWriter(name,self.fourcc, 29,(self.width,self.height))
            
            # for i in range(0,len(output)):

            #     frame = cv2.resize(output[i], (self.width, self.height), interpolation=cv2.INTER_CUBIC)
            #     # cv2.imshow("OUT",frame)
            #     # cv2.waitKey(1)
            #     out.write(frame)
            #        
            

        print("ALL ECC cost :" + str(ECC_e - ECC_s))
        out.release()
        out = cv2.VideoWriter("./data/"+str(int(ECC_e - ECC_s)) ,self.fourcc, 29,(self.width,self.height))

    def f6_2(self, x) :
        cap = cv2.VideoCapture(self.inputpath)
        print ("\t" + str(x) + "\t" + str(os.getpid()))
        ecc_s = time.time()
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_POS_FRAMES, x)
            ret, frame = cap.read()
            # frame = cv2.putText(frame, str(x), (50,150), cv2.FONT_HERSHEY_COMPLEX, 5, (0,0,255), 2)
            frame = cv2.resize(frame, (self.width, self.height), interpolation=cv2.INTER_CUBIC)
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            temp_warp = self.shrList[0]
            try:
                (cc, temp_warp) = cv2.findTransformECC(self.target_frame, frame_gray, temp_warp, self.warp_mode, self.criteria)
            except:
                (cc, temp_warp) = cv2.findTransformECC(self.target_frame, frame_gray, temp_warp, self.warp_mode, self.criteria, inputMask=None, gaussFiltSize=1)

            frame_aligned = cv2.warpPerspective (frame, temp_warp, (self.stabilization_sz[1], self.stabilization_sz[0]), flags=cv2.INTER_CUBIC + cv2.WARP_INVERSE_MAP)                
            
            self.shrList[0] = temp_warp

            ecc_e = time.time()
            print ("\t\t" + str(x) + "\t" + str(ecc_e - ecc_s))
            cap.release()
            return frame_aligned
        
        cap.release()
        
        return frame
        
    def thedo6_2(self):
        multi = int(multiprocessing.cpu_count() / 2)
        # multi = 8
        print(multi)
        print(type(multi))
        output = []
        frame = 0
        cap = cv2.VideoCapture(self.inputpath)
        allframe = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)/2)
        self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)/2)

        waitWorkPa3 = self.pa3(0,allframe)

        bigWhile = int(len(waitWorkPa3) / multi)
        less = int(len(waitWorkPa3) % multi)       
        
        ret, frameT = cap.read() 
        frameT = cv2.resize(frameT, (self.width, self.height), interpolation=cv2.INTER_CUBIC)
        self.target_frame = cv2.cvtColor(frameT, cv2.COLOR_BGR2GRAY)
        self.stabilization_sz = frameT.shape
        cap.release()

        li = self.warp_matrix
        shr = multiprocessing.Manager()
        self.shrList = shr.list()
        self.shrList.append(li)

        start = time.time()
        with multiprocessing.Pool(multi) as pool :
                        
            while bigWhile > 0 :
                print ("/////"+ str(bigWhile) + "/////")

                

                waitinput = waitWorkPa3[frame: (frame+multi)]
                frame = frame + multi
                result = pool.map_async(self.f6_2, waitinput)
                                

                output = output + result.get()
                bigWhile = bigWhile - 1
                
                print(self.shrList[0])
            print ("///// less /////")
            waitinput = waitWorkPa3[frame: frame+less]
            result = pool.map_async(self.f6_2, waitinput)
            output = output + result.get()       

        out = cv2.VideoWriter("./data/output.avi",self.fourcc, 29,(self.width,self.height))
        print(len(output))
        end = time.time() - start
        p2 = time.time()
        print(end)
        for i in range(0,len(output)):
            out.write(output[i])
        out.release()
        end = time.time() - p2
        print(end)               

    def makeFrames(self):
        cap = cv2.VideoCapture(self.inputpath)

        frameList = [ 1620, 1728, 2931, 3163, 3603, 3731 ]

        for i in range(0,len(frameList)) :
            cap.set(cv2.CAP_PROP_POS_FRAMES, frameList[i])
            ret, frame = cap.read()
            cv2.imwrite("./data/"+str(i)+".jpg", frame)

    def RNECC(self, targetF, currentF, iterations, eps):
  
        criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, iterations, eps)

        frameT = cv2.resize(targetF, (1920, 1080), interpolation=cv2.INTER_CUBIC)
        target_frame = cv2.cvtColor(frameT, cv2.COLOR_BGR2GRAY)

        frame = currentF
        frame = cv2.resize(frame, (1920, 1080), interpolation=cv2.INTER_CUBIC)
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        temp_warp = np.eye(3, 3, dtype=np.float32)
        print(temp_warp)

        start = time.time()
        try:
            (cc, temp_warp) = cv2.findTransformECC(target_frame, frame_gray, temp_warp, self.warp_mode, criteria)
        except:
            (cc, temp_warp) = cv2.findTransformECC(target_frame, frame_gray, temp_warp, self.warp_mode, criteria, inputMask=None, gaussFiltSize=1)
        end = time.time()

        frame_aligned = cv2.warpPerspective (frame, temp_warp, (1920, 1080), flags=cv2.INTER_CUBIC + cv2.WARP_INVERSE_MAP)
        output = ""
        output = self.level +"\t"+ str(iterations) + "\t" + str(eps) + "\t" + str(cc) + "\t" + str(end-start)
        temp = "./data/BUG/output/" + self.level+"_" +str(iterations)+"_"+ str(eps) +"_"+ str(round(cc,3)) +".jpg"
        print(output)
        cv2.destroyAllWindows()
        cv2.imshow(temp,frame_aligned)
        cv2.waitKey(1)
        
        cv2.imwrite(temp, frame_aligned)
 
        return output


    def criteriaTest(self) :

        self.path = "./data/BUG/"
        Tjpg = "1.jpg"
        Cjpg = "2.jpg"
        targetList = []
        currentList = []
        outputstr = []

        temp = "level\titerations\teps\tcc\tcost time"
        outputstr.append(temp +"\n")
        for i in range(1,4):
            targetList.append( str( self.path + str(i) + Tjpg ) )
            currentList.append( str( self.path + str(i) + Cjpg ))
        
        for i in range(0, len(targetList)):
            self.targetF = cv2.imread(targetList[i])
            self.currentF = cv2.imread(currentList[i])
      
            self.level = str(i+1)
            # eps = 1e-5
            # for iter in range(30, 500, 10) :
            #     print(self.level + "\t" +str(iter) + "\t" + str(eps))
            #     temp = self.RNECC(self.targetF, self.currentF, iter, eps)
            #     outputstr.append(temp +"\n")

            iter = 300
            for i in range(1, 1000, 20) :
                eps = (5*1e-4)*i
                print(self.level + "\t" +str(iter) + "\t" + str(eps))
                temp = self.RNECC(self.targetF, self.currentF, iter, eps)
                outputstr.append(temp +"\n")

        outputFile = open("./data/BUG/criteriaData.txt", 'w')
            
        for i in range(0,len(outputstr)) :    
            outputFile.write(outputstr[i])
        outputFile.close()

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
                    + "\t End :" + str(self.cutInfoList[i].getEnd()))
                    

if __name__ == '__main__':
    mydo = do()
    mydo.criteriaTest()



    # with multiprocessing.Manager() as manager:
    #     d = manager.dict()
    #     l = manager.list(range(10))
        
    #     p = multiprocessing.Process(target=f, args=(d, l))
    #     p.start()
    #     p.join()

    #     print(d)
    #     print(l)

# class ResultMaker:
#     def __init__(self, outCV):
#         self.out = outCV
#         self.outputFrameID = 0
#         self.waitList = []

#     def addNewFrame(self, frameData ):
#         self.waitList.append(frameData)
    
#     def checkWaitList(self):
#         self.waitList.sort()
#         while len(self.waitList) > 0 and self.outputFrameID == self.waitList[0][0] :
#             self.out.write(self.waitList[0][1])
#             self.waitList.pop(0)
#             self.outputFrameID = self.outputFrameID + 1


# ston = [1,2,3,4,5]
# mylist = []
# print(len(mylist))
# print(len(ston))
# for i in range(0,7):
#     temp = [random.randint(1,100),ston]
#     mylist.append(temp)

# print(mylist)

# print("====")

# mylist.sort()

# print(mylist)

# print(mylist[0][0])

# print("====")

# i = 1 

# while len(ston) != 0 and i == ston[0]: 
#     print("POP : " + str(ston[0]))
#     ston.pop(0)
#     print(len(ston))
#     i = i + 1









# import os
# import time
# import cv2
# import numpy as np
# from config import conf
# from logs import logger

# class StableVideo:

#     def __init__(self, inputVideoPath, cut_txt):
#         self.cuttingData(cut_txt)
#         self.inputVideoPath = inputVideoPath
#         self.videolist = os.listdir(inputVideoPath)

#         self.videolist.sort()

#         ''' cv2 read video  setting ''' 
#         self.cap = cv2.VideoCapture(os.path.join( os.path.abspath(inputVideoPath), self.videolist[0]))
#         self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
#         self.targrt_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))   # get width from origin video
#         self.target_hight = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # get hight from origin video

#         if self.target_hight > 1080 :
#             self.output_width = int(self.targrt_width / 2)
#             self.output_hight = int(self.target_hight / 2)
#         else:
#             self.output_width = self.targrt_width
#             self.output_hight = self.target_hight
        
#         ''' stablize setting '''

#         self.warp_mode = cv2.MOTION_HOMOGRAPHY
#         self.warp_matrix = np.eye(3, 3, dtype=np.float32)

#         # self.roi = [ [0, 0], [self.targrt_width, self.target_hight] ]        
#         # self.roi_x = self.roi[0][0]
#         # self.roi_y = self.roi[0][1]
#         # self.roi_width = self.roi[1][0] - self.roi[0][0]
#         # self.roi_height = self.roi[1][1] - self.roi[0][1]
#         self.number_of_iterations = 500
#         self.termination_eps = 1e-5    
#         self.criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, self.number_of_iterations,  self.termination_eps)


#     def ending( self, index, frame ) :
#         if index == conf.enddingIndex and frame >= conf.enddingFrame :
#             return True
#         else :
#             return False

#     def stableVideoWithOutputpath(self, outputpath, is_Show=False):

#         startTime = time.time()  
#         out = cv2.VideoWriter(outputpath, self.fourcc, 9.99, (self.output_width, self.output_hight))        
#         count = 0
        
#         index = 0
#         while index < len(self.videolist) :
#             while self.cutInfoList[index].getKey() == -1 and self.cutInfoList[index].getStart() == -1 and self.cutInfoList[index].getEnd() == -1 and index < len(self.videolist):
#                 logger.info("[Step 1] ->> PASS : " +  self.videolist[index] )
#                 index = index + 1
#                 if index >= len(self.videolist) :
#                     logger.info("[Step 1] ->> Complete stable video : " +  self.videolist[index-1])
#                     self.cap.release()
#                     out.release()
#                     cv2.destroyAllWindows()

#                     workingTime = time.time() - startTime
                    
#                     logger.info("[Step 1] ->> cost time :" + str(workingTime))
#                     logger.info("[Step 1] ->> Output file :" + outputpath)
                    
#                     # Break
#                     return

#             self.cap = cv2.VideoCapture(os.path.join( os.path.abspath(self.inputVideoPath), self.videolist[index]))    
#             if self.cutInfoList[index].getKey() != -1 :

#                 # keyTenP = int(conf.key_frame / 10)
#                 keyTenP = int(self.cutInfoList[index].getKey() / 10)
#                 now = 0
#                 print("[Load Key Frame] : <" + self.videolist[index] +'>')
#                 while self.cap.isOpened():  # capture key frame

#                     ret, frame = self.cap.read()
#                     if not ret :
#                         break

#                     if is_Show :
#                         cv2.imshow('frame', frame)
#                         if cv2.waitKey(1) == ord('q'): 
#                             break
                    
#                     if self.cap.get(cv2.CAP_PROP_POS_FRAMES) > ( now * keyTenP ) :
#                         print("[ " + str(now*10) + "% ]")
#                         now = now + 1 

#                     if self.cap.get(cv2.CAP_PROP_POS_FRAMES) == self.cutInfoList[index].getKey():
                        
#                         print ("GET TARGET\tframe: " + str(self.cap.get(cv2.CAP_PROP_POS_FRAMES)))
#                         frame = cv2.resize(frame, (self.output_width, self.output_hight), interpolation=cv2.INTER_CUBIC)
#                         self.target_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#                         self.stabilization_sz = frame.shape
#                         logger.info( "[Step 1] ->> <" + self.videolist[index] + "> Key Frame : [" + str(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) +"]" )
#                         break

#             self.cap.set(cv2.CAP_PROP_POS_FRAMES,cv2.CAP_PROP_POS_FRAMES)

#             if self.cutInfoList[index].getStart() > 1 :
#                 cutTenP = int(self.cutInfoList[index].getStart() / 10)
#                 now = 0
#                 print("[Run Cut Frame] : <"+ self.videolist[index] + '>')
#                 while self.cap.isOpened() :

#                     ret, frame = self.cap.read()
#                     if not ret :
#                         break
                    
#                     if is_Show :
#                         cv2.imshow('frame', frame)
#                         if cv2.waitKey(1) == ord('q'):                            
#                             logger.info( "<" + self.videolist[index] + "> Cut Frame start in : [" + str(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) +"]" )
#                             break
                    
#                     if self.cap.get(cv2.CAP_PROP_POS_FRAMES) > ( now * cutTenP ) :
#                         print("[ " + str(now*10) + "% ]")
#                         now = now + 1                     

#                     if self.cap.get(cv2.CAP_PROP_POS_FRAMES) == self.cutInfoList[index].getStart():
#                         logger.info( "[Step 1] ->> <" + self.videolist[index] + "> Cut Frame start in : [" + str(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) +"]" )
#                         break
#             else :
#                 logger.info( "[Step 1] ->> <" + self.videolist[index] + "> Cut Frame start in : [1]" )
                
#             logger.info("[Step 1] ->> Start stable video : " +  self.videolist[index] )            
#             tenP = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT) / 10)
#             now = 0

#             while self.cap.isOpened():
#                 ret, frame = self.cap.read()            

#                 if not ret :
#                     logger.info("[Step 1] ->> Complete stable video : " +  self.videolist[index])
#                     break
                
#                 if self.cap.get(cv2.CAP_PROP_POS_FRAMES) > ( now * tenP ) :
#                     print("[ " + str(now*10) + "% ]")
#                     now = now + 1

#                 if count % 3 == 0 :

#                     frame = cv2.resize(frame, (self.output_width, self.output_hight), interpolation=cv2.INTER_CUBIC)
#                     frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#                     print("ECC")
#                     try:
#                         (cc, warp_matrix) = cv2.findTransformECC(self.target_frame, frame_gray, self.warp_matrix, self.warp_mode, self.criteria)
#                     except:
#                         (cc, warp_matrix) = cv2.findTransformECC(self.target_frame, frame_gray, self.warp_matrix, self.warp_mode, self.criteria, inputMask=None, gaussFiltSize=1)
#                     print("\tECC")
                    
#                     frame_aligned = cv2.warpPerspective (frame, warp_matrix, (self.stabilization_sz[1], self.stabilization_sz[0]), flags=cv2.INTER_CUBIC + cv2.WARP_INVERSE_MAP)                
#                     # frame_resized = frame_aligned[0:self.target_hight, 0:self.targrt_width]
#                     # frame_resized = frame_aligned # for original size                                            
#                     # frame_resized = cv2.resize(frame_resized, (self.output_width, self.output_hight))
#                     print("\t\tEND")
#                     print("//////////////")
#                     print(warp_matrix)
                    
#                     print(self.warp_matrix)
#                     print("//////////////")
#                     out.write(frame_aligned)
                    
#                     if self.cap.get(cv2.CAP_PROP_POS_FRAMES) >= self.cutInfoList[index].getEnd() :
#                     # if self.ending(index, self.cap.get(cv2.CAP_PROP_POS_FRAMES)):
#                         logger.info( "[Step 1] ->> <" + self.videolist[index] + "> Cut Frame End in : [" + str(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) +"]" )
#                         logger.info("[Step 1] ->> Complete stable video : " +  self.videolist[index])
#                         break


#                     if is_Show :
#                         cv2.imshow('frame', frame_aligned)
#                         if cv2.waitKey(1) == ord('q'):
#                             logger.info( "[Step 1] ->> <" + self.videolist[index] + "> Cut Frame End in : [" + str(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) +"]" )
#                             break
                
#                 count = count + 1

#             index = index +1


#         self.cap.release()
#         out.release()
#         cv2.destroyAllWindows()

#         workingTime = time.time() - startTime
        
#         logger.info("[Step 1] ->> cost time :" + str(workingTime))
#         logger.info("[Step 1] ->> Output file :" + outputpath)

#     def cuttingData(self, cut_txt):
#         f = open( cut_txt, 'r' )
#         self.cutInfo = f.readlines()
#         self.cutInfoList = []

#         for i in range(0, len(self.cutInfo)) :
#             string = ''
#             count = 0
#             tempCut = CutInfo()
#             for j in range(0, len(self.cutInfo[i])) :                

#                 if self.cutInfo[i][j] == '\t' or self.cutInfo[i][j] == '\n':
#                     count = count + 1
                    
#                     tempInt = int(string)
#                     string = ''

#                     if count == 1 :
#                         tempCut.setKey(tempInt)
#                     if count == 2 :
#                         tempCut.setStart(tempInt)
#                     if count == 3 :
#                         tempCut.setEnd(tempInt)

#                 string = string + self.cutInfo[i][j]
#             self.cutInfoList.append(tempCut)

#         f.close()

 
#         for i in range(0,len(self.cutInfoList)):
#             print ("Key :" + str(self.cutInfoList[i].getKey()) + "\t Start :"+ str(self.cutInfoList[i].getStart())
#             + "\t End :" + str(self.cutInfoList[i].getEnd()))

# class CutInfo() :
#     def __init__(self):
#         self.key = -1
#         self.start = -1
#         self.end = -1

#     def setKey(self, key) :        
#         self.key = int(key)
    
#     def setStart(self, start) :
#         self.start = int(start)
    
#     def setEnd(self,end):
#         self.end = int(end)

#     def getKey(self):
#         return self.key
    
#     def getStart(self):
#         return self.start

#     def getEnd(self):
#         return self.end

# if __name__ == '__main__':
#     print("::::Stabilization.py Example::::")
#     print("> Please put the video which need to stabilez in same directrory,")
#     print("> and make the file name as '1.mp4'.")
#     print("> sand then there were be a file output as '2.avi'.")

#     current_STAB = StableVideo('1.mp4')
#     current_STAB.stableVideoWithOutputpath(outputpath='2.avi')


# def stab_main(stab_input,stab_output,show,cut_txt):
    
    # current_STAB = StableVideo(stab_input, cut_txt)
    # current_STAB.stableVideoWithOutputpath(stab_output,show)





