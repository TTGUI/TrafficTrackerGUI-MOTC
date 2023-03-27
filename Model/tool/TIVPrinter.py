import os
import pathlib
import cv2
import numpy as np

class TIVP:
    def __init__(self):
        self.fileType = '.jpg' 
        self.color = (127, 255, 0)

    def RTcenter(self, points):
        ans = []
        
        x = (int(points[0]) + int(points[4]) ) / 2
        y = (int(points[1]) + int(points[5]) ) / 2
        ans.append(int(x))
        ans.append(int(y))
        return ans

    def printer(self, TIV_path = "", IO_path = "", bkg_path = "", result_path = ""):
         

        result_path = result_path + "TIV_IssuePrint/"
        #### Make IO line base on bkg ####

        baseFrame = cv2.imdecode(np.fromfile(bkg_path, dtype=np.uint8), -1)

        fio = open(IO_path, 'r')
        io = fio.readlines()
        fio.close()

        V2 = io[0].split(",")
        V3 = io[1].split(",")

        pts = []
        bordertype = []
        for i in range(0, len(V2)-1):
            bordertype.append(int(V2[i]))
            pts.append((int(V3[2*i]), int(V3[2*i+1])))

        for j in range(-1, len(bordertype)-1):
            if bordertype[j] > 0:
                cv2.line(baseFrame, pts[j], pts[j+1], (0, 255, 0), 3)
            elif bordertype[j] < 0:
                cv2.line(baseFrame, pts[j], pts[j+1], (0, 0, 255), 3)    

        for j in range(2, len(io)):
            V4 = io[j].split(",")
            k = 0
            for k in range(0, len(V4)-3, 2):
                cv2.line(baseFrame, (int(V4[k]), int(V4[k+1])), (int(V4[k+2]), int(V4[k+3])), (255, 0, 0), 2)

        # cv2.imshow("baseFrame", baseFrame)
        # cv2.waitKey()

        #### Add Tracking line ####

        if not os.path.isdir(result_path):
            os.mkdir(result_path)
        
        cv2.imencode(ext=self.fileType,img=baseFrame)[1].tofile( result_path + "IO" + self.fileType)

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


        for i in range(0, len(sameIOList)) :
            linePoints = sameIOList[i].split(",")
            centers = []
            temp = []
            for count in range (6,len(linePoints)):
                if len(temp) < 8 :
                    temp.append(linePoints[count])
                else :
                    centers.append(self.RTcenter(temp))            
                    temp = []
                    temp.append(linePoints[count])
            # eachFrame = np.zeros((baseFrame.shape[0], baseFrame.shape[1], 3), np.uint8)
            eachFrame = cv2.imdecode(np.fromfile(result_path + "IO" + self.fileType,dtype=np.uint8),-1)
            for k in range(0,len(centers)):
                # eachFrame[centers[k][1],centers[k][0]] = self.color
                if k == len(centers) - 1 :
                    cv2.circle(eachFrame, (centers[k][0],centers[k][1]), 7, (0, 255, 255), -1)
                    cv2.circle(eachFrame, (centers[k][0],centers[k][1]), 11, (0, 255, 255), 2)
                else :
                    cv2.circle(eachFrame, (centers[k][0],centers[k][1]), 3, self.color, 2)

            
            fileName = linePoints[0] + "_" + linePoints[5] + "_" + linePoints[3] + linePoints[4] + "_(" + linePoints[1] + "~" + linePoints[2] + ")"
            cv2.putText(eachFrame, fileName, (10, 40), cv2.FONT_HERSHEY_SIMPLEX,  1, (0,0,0), 6, cv2.LINE_AA)
            cv2.putText(eachFrame, fileName, (10, 40), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 2, cv2.LINE_AA)

            cv2.imencode(ext=self.fileType,img=eachFrame)[1].tofile( result_path + fileName + self.fileType)

            
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
    
    currentTIVP = TIVP()
    currentTIVP.printer(TIV_path, IO_path, bkg_path, curPath)