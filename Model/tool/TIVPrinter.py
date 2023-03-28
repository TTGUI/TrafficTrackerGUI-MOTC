import os
import pathlib
import cv2
import numpy as np
from config import conf

class TIVP:
    def __init__(self):
        self.fileType = '.jpg' 
        self.color = (127, 255, 0)
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        if __name__ != '__main__':
            self.windowSize = conf.getTIVP_windoSize()
        else:
            self.windowSize = 200

    def RTcenter(self, points):
        ans = []
        
        x = (int(points[0]) + int(points[4]) ) / 2
        y = (int(points[1]) + int(points[5]) ) / 2
        ans.append(int(x))
        ans.append(int(y))
        return ans
    
    def dwarIO(self, io, frame):
        V2 = io[0].split(",")
        V3 = io[1].split(",")

        pts = []
        bordertype = []
        for i in range(0, len(V2)-1):
            bordertype.append(int(V2[i]))
            pts.append((int(V3[2*i]), int(V3[2*i+1])))

        for j in range(-1, len(bordertype)-1):
            if bordertype[j] > 0:
                cv2.line(frame, pts[j], pts[j+1], (0, 255, 0), 3)
            elif bordertype[j] < 0:
                cv2.line(frame, pts[j], pts[j+1], (0, 0, 255), 3)    

        for j in range(2, len(io)):
            V4 = io[j].split(",")
            k = 0
            for k in range(0, len(V4)-3, 2):
                cv2.line(frame, (int(V4[k]), int(V4[k+1])), (int(V4[k+2]), int(V4[k+3])), (255, 0, 0), 2)

        return frame

    def printer(self, TIV_path, IO_path, stab_video , result_path , actionName ):
        
        result_path = result_path + actionName + "_TIV_IssuePrint/"
        #### Read IO line ####

        fio = open(IO_path, 'r')
        io = fio.readlines()
        fio.close()

        #### Add Tracking line ####

        if not os.path.isdir(result_path):
            os.mkdir(result_path)

        f = open(TIV_path, 'r')
        TIV = f.readlines()
        f.close()

        sameIOList = []

        index = 0 
        while index < len(TIV) and TIV[index] != "SameIOCar\n" :
            index += 1

        index += 1
        while index < len(TIV) and TIV[index] != "SameIOMotor\n" :
            sameIOList.append(TIV[index])
            index += 1

        index += 1
        while index < len(TIV) :
            sameIOList.append(TIV[index])
            index += 1


        cap = cv2.VideoCapture(stab_video)
        for i in range(0, len(sameIOList)) :
            linePoints = sameIOList[i].split(",")
            startFrame = linePoints[1]
            endFrame = linePoints[2]
            fileName = linePoints[0] + "_" + linePoints[5] + "_" + linePoints[3] + linePoints[4] + "_(" + startFrame + "~" + endFrame + ")"
            
            centers = []
            temp = []
            print("[" + str(i+1) + "/" + str(len(sameIOList)) + "] " + fileName)
            # get tracking points center
            for count in range (6,len(linePoints)):
                if len(temp) < 8 :
                    temp.append(linePoints[count])
                else :
                    centers.append(self.RTcenter(temp))            
                    temp = []
                    temp.append(linePoints[count])

            effectiveWindow = 0
            if int(startFrame) > self.windowSize :
                cap.set(cv2.CAP_PROP_POS_FRAMES, int(startFrame) - self.windowSize)
                effectiveWindow += self.windowSize
            else :
                effectiveWindow += int(startFrame)
                cap.set(cv2.CAP_PROP_POS_FRAMES, 1)
            if int(endFrame) + self.windowSize > cap.get(cv2.CAP_PROP_FRAME_COUNT) :
                effectiveWindow += cap.get(cv2.CAP_PROP_FRAME_COUNT) - int(endFrame)
            else :
                effectiveWindow += self.windowSize

            k = 0
            index = 0
            frameID =  cap.get(cv2.CAP_PROP_POS_FRAMES)
            out = cv2.VideoWriter(result_path + fileName+".avi", self.fourcc, 30, (1920, 1080)) 

            while frameID < int(endFrame) + self.windowSize :
                print(str(index+1) + "/" + str(int(endFrame)-int(startFrame)+ effectiveWindow) +"          ", end='\r')
                ret, frame = cap.read()
                if not ret :
                    break
                frame = self.dwarIO(io,frame)
                if frameID + k >= int(startFrame) :
                    if frameID < int(endFrame) : 
                        k += 1
                    for p in range(0,k) :
                        if p == len(centers) - 1 :
                            cv2.circle(frame, (centers[p][0],centers[p][1]), 7, (0, 255, 255), -1)
                            cv2.circle(frame, (centers[p][0],centers[p][1]), 11, (0, 255, 255), 2)
                        else :
                            cv2.circle(frame, (centers[p][0],centers[p][1]), 3, self.color, -1)

                displayStr = fileName + "  [ " +str(cap.get(cv2.CAP_PROP_POS_FRAMES)) + " ]"
                cv2.putText(frame, displayStr, (10, 40), cv2.FONT_HERSHEY_SIMPLEX,  1, (0,0,0), 6, cv2.LINE_AA)
                cv2.putText(frame, displayStr, (10, 40), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 2, cv2.LINE_AA)
                out.write(frame)
                frameID =  cap.get(cv2.CAP_PROP_POS_FRAMES)
                index +=1

                cv2.imshow("frame",frame)
                cv2.waitKey(1)
            

            out.release()
        
        cv2.destroyAllWindows()
        cap.release()
        print("[TIVPrinter Done.]")

if __name__ == '__main__':
    curPath = str(pathlib.Path(__file__).parent.resolve())
    curPath = curPath + '\\'
    print("[Folder paht default codefile current folder.]")

    TIV_path = input("[Enter TIV_path ] >> ")
    if TIV_path == "" :
        TIV_path = "TEST_TIV.csv"
    TIV_path = curPath + TIV_path

    IO_path = input("[Enter IO_path ] >> ")
    if IO_path == "" :
        IO_path = "TEST_IO.txt"
    IO_path = curPath + IO_path
    
    bkg_path = input("[Enter bkg_path ] >> ")
    if bkg_path == "" :
        bkg_path = "TEST_background.jpg"
    bkg_path = curPath + bkg_path
    
    actionName = "default"
    stab_video = "stab_video"

    currentTIVP = TIVP()
    currentTIVP.printer(TIV_path, IO_path, stab_video, curPath, actionName, stab_video)