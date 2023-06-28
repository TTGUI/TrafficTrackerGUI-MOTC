import os
from pathlib import Path
import cv2
import numpy as np
import argparse
import os
from pathlib import Path

import cv2
import numpy as np

class csvParse():
    """
    csvParse 提供編輯csv檔案的功能.
    -c [csv file path] input csv file name.
    -s [store_true] save csv file. default output will be overwrite save to input csv file.
    -o [csv file name] output file save as new name, ex `output.csv`.
    -a [csv file path] append csv file will be append to input csv file.
    -rcl [class type] Remove class type from csv.移除的class,可以是連續class字元組成的字串
    -rid [id] remove tracking id from csv
    -rin [frame] remove tracking id starts earlier then this frame number.
    -rout [frame] remove tracking id ends later then this frame number.
    -p [store_true] print csv display image, result folder will be same as input csv file.
    -pt [file type] print csv display image file type(jpa. png. bmp.)
    -h [store_true] 詳細說明
    """
    def __init__(self) -> None:
        
        self.inputCsvLine =[]
    
    def printCsvImg(self, lines, csv,fileType = '.jpg' ):
            if fileType[0] != '.':
                fileType = '.' + fileType

            def RTcenter(points):
                ans = []
                
                x = (int(points[0]) + int(points[4]) ) / 2
                y = (int(points[1]) + int(points[5]) ) / 2
                ans.append(int(x))
                ans.append(int(y))
                return ans

            def RTIO(data):
                ans = []
                ans.append(data[3])
                ans.append(data[4])
                return ans
            csvResultFolder = Path(csv).parent.resolve() / str(os.path.splitext(csv)[0][:-5] + '_CsvPrint')

            if not os.path.isdir(csvResultFolder):
                os.mkdir(csvResultFolder)
                    
            print(len(lines))    
            countAll = len(lines)
            countA = []
            countB = []
            countC = []
            countD = []

            axis_X = 1080
            axis_Y = 2048
            img = np.zeros((axis_X, axis_Y, 3), np.uint8)
            AI = np.zeros((axis_X, axis_Y, 3), np.uint8)
            BI = np.zeros((axis_X, axis_Y, 3), np.uint8)
            CI = np.zeros((axis_X, axis_Y, 3), np.uint8)
            DI = np.zeros((axis_X, axis_Y, 3), np.uint8)
            Aout = []
            Bout = []
            Cout = []
            Dout = []

            for i in range(0,4):
                Aout.append(np.zeros((axis_X, axis_Y, 3), np.uint8))
                Bout.append(np.zeros((axis_X, axis_Y, 3), np.uint8)) 
                Cout.append(np.zeros((axis_X, axis_Y, 3), np.uint8))
                Dout.append(np.zeros((axis_X, axis_Y, 3), np.uint8))
                countA.append(0)
                countB.append(0)
                countC.append(0)
                countD.append(0)

            for i in range(0,len(lines)):
                print(str(i+1) + " / " + str(len(lines)), end='\r' )
                linePoints = lines[i].split(",")

                centers = []
                temp = []
                IO = RTIO(linePoints)
                I = IO[0]
                O = IO[1]
                for count in range (6,len(linePoints)):
                    if len(temp) < 8 :
                        temp.append(linePoints[count])
                    else :
                        centers.append(RTcenter(temp))            
                        temp = []
                        temp.append(linePoints[count])
                
                if I != 'X' and O != 'X':
                    index = -1
                    color = [255, 255, 255]
                    color2 = [255, 255, 255]
                    if O == 'AO':
                        color2 = [255, 0, 0]
                        index = 0
                    elif O == 'BO':
                        color2 = [0, 255, 0]
                        index = 1
                    elif O == 'CO':
                        color2 = [0, 0, 255]
                        index = 2
                    elif O == 'DO':
                        color2 = [255, 255, 255]
                        index = 3
                    if I == 'AI': countA[index] = countA[index] + 1
                    elif I == 'BI': countB[index] = countB[index] + 1 
                    elif I == 'CI': countC[index] = countC[index] + 1 
                    elif I == 'DI': countD[index] = countD[index] + 1 
                    for k in range(0,len(centers)):

                        if I == 'AI':
                            color = [255, 0, 0]
                            AI[centers[k][1],centers[k][0]] = color2                
                            Aout[index][centers[k][1],centers[k][0]] = color2

                        elif I == 'BI':
                            color = [0, 255, 0]
                            BI[centers[k][1],centers[k][0]] = color2
                            Bout[index][centers[k][1],centers[k][0]] = color2

                        elif I == 'CI':
                            color = [0, 0, 255]
                            CI[centers[k][1],centers[k][0]] = color2
                            Cout[index][centers[k][1],centers[k][0]] = color2

                        elif I == 'DI':
                            color = [255, 255, 255]
                            DI[centers[k][1],centers[k][0]] = color2
                            Dout[index][centers[k][1],centers[k][0]] = color2

                        img[centers[k][1],centers[k][0]] = color


            print ("\nDONE.")

            def getCountABCD(data):
                countTemp = 0
                for i in range(0,len(data)):
                    countTemp = countTemp + int(data[i])

                return countTemp
            


            text = 'All   Type:All' + "   (" +  str(countAll) + ")"
            cv2.putText(img, text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 1, cv2.LINE_AA)
            cv2.imshow('ALL',img)
            cv2.imencode(ext=fileType,img=img)[1].tofile( str(csvResultFolder / f"All_Type_All({countAll}){fileType}"))

            countTemp = getCountABCD(countA)
            text = 'AI   Type:All' + "   (" +  str(countTemp) + ")"
            cv2.putText(AI, text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 1, cv2.LINE_AA)
            cv2.imshow('AI',AI)
            cv2.imencode(ext=fileType,img=AI)[1].tofile( str(csvResultFolder / f"AI_Type_All({countTemp}){fileType}"))

            for i in range (0, len(Aout)):
                A = 'A'
                fileName = 'AI' + chr(ord(A) + i ) + 'O_Type_All' + "(" +  str(countA[i]) + ")"  + fileType
                text = 'AI'+ chr(ord(A) + i ) + 'O' + '   Type:All' + "   (" +  str(countA[i]) + ")"
                cv2.putText(Aout[i], text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 1, cv2.LINE_AA)
                cv2.imencode(ext=fileType,img=Aout[i])[1].tofile( str(csvResultFolder / fileName ))

            countTemp = getCountABCD(countB)
            text = 'BI   Type:All' + "   (" +  str(countTemp) + ")"
            cv2.putText(BI, text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 1, cv2.LINE_AA)
            cv2.imshow('BI',BI)
            cv2.imencode(ext=fileType,img=BI)[1].tofile( str(csvResultFolder / f"BI_Type_All({countTemp}){fileType}"))
            for i in range (0, len(Bout)):
                A = 'A'
                fileName = 'BI' + chr(ord(A) + i ) + 'O_Type_All' + "(" +  str(countB[i]) + ")"  + fileType
                text = 'BI'+ chr(ord(A) + i ) + 'O' + '   Type:All' + "   (" +  str(countB[i]) + ")"
                cv2.putText(Bout[i], text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 1, cv2.LINE_AA)
                cv2.imencode(ext=fileType,img=Bout[i])[1].tofile( str(csvResultFolder / fileName))

            countTemp = getCountABCD(countC)
            text = 'CI   Type:All' + "   (" +  str(countTemp) + ")"
            cv2.putText(CI, text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 1, cv2.LINE_AA)
            cv2.imshow('CI',CI)
            cv2.imencode(ext=fileType,img=CI)[1].tofile( str(csvResultFolder / f"CI_Type_All({countTemp}){fileType}"))
            for i in range (0, len(Cout)):
                A = 'A'
                fileName = 'CI' + chr(ord(A) + i ) + 'O_Type_All' + "(" +  str(countC[i]) + ")"  + fileType
                text = 'CI'+ chr(ord(A) + i ) + 'O' + '   Type:All' + "   (" +  str(countC[i]) + ")"
                cv2.putText(Cout[i], text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 1, cv2.LINE_AA)
                cv2.imencode(ext=fileType,img=Cout[i])[1].tofile( str(csvResultFolder / fileName ))

            countTemp = getCountABCD(countD)
            text = 'DI   Type:All' + "   (" +  str(countTemp) + ")"
            cv2.putText(DI, text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 1, cv2.LINE_AA)
            cv2.imshow('DI',DI)
            cv2.imencode(ext=fileType,img=DI)[1].tofile( str(csvResultFolder / f"DI_Type_All({countTemp}){fileType}"))
            for i in range (0, len(Dout)):
                A = 'A'
                fileName = 'DI' + chr(ord(A) + i ) + 'O_Type_All' + "(" +  str(countD[i]) + ")"  + fileType
                text = 'DI'+ chr(ord(A) + i ) + 'O' + '   Type:All' + "   (" +  str(countD[i]) + ")"
                cv2.putText(Dout[i], text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 1, cv2.LINE_AA)
                cv2.imencode(ext=fileType,img=Dout[i])[1].tofile( str(csvResultFolder / fileName) )
            cv2.waitKey(0)   


    def getLineData(self, line, id):
        temp = line.split(',')
        return temp[id]
    def getID(self, line):
        return self.getLineData(line, 0)
    def getINframe(self, line):
        return self.getLineData(line, 1)
    def getOUTframe(self, line):
        return self.getLineData(line, 2)
    def getIOin(self, line):
        return self.getLineData(line, 3)
    def getIOout(self, line):
        return self.getLineData(line, 4)
    def getClass(self, line):
        return self.getLineData(line, 5)
    
    def main(self) :

        parser = argparse.ArgumentParser()
        parser.add_argument("-c", "--csv",
                            help="[csv file path] input csv file name.",
                            type=str)
        parser.add_argument("-s", "--save",
                            help="[store_true] save csv file. default output will be overwrite save to input csv file.",
                            action="store_true")
        parser.add_argument("-o","--outputCsv",
                            help="[csv file name] output file save as new name, ex `output.csv`",
                            type=str)
        parser.add_argument("-rcl", "--removeClass",
                            help="[class type] Remove class type from csv. ex: `-r c` will remove all class type `car` from csv.\
                            `-r cpm` will remove all class type `car`,`pedestran` and `motor` from csv.\
                            All class type : 'p'行人 'u'自行車 'm'機車 'c'小客車 't'貨車 'b'大客車 'h'聯結車(頭) 'g'聯結車(尾).",
                            type=str)
        parser.add_argument("-a", "--appendCsv",
                            help="[csv file path] append csv file will be append to input csv file.\
                            tracking id will be follow input csv.\
                            You CAN NOT operate on append csv file.If you want to operate on append csv file, please operate this file first before marge.",
                            type=str)
        parser.add_argument("-rid", "--removeId",
                            help="[id] remove tracking id from csv",
                            type=int)
        parser.add_argument("-rin", "--removeInFrameTime",
                            help="[frame] remove tracking id starts earlier then this frame number.",
                            type=int)
        parser.add_argument("-rout", "--removeOutFrameTime",    
                            help="[frame] remove tracking id ends later then this frame number.",
                            type=int)
        parser.add_argument("-p", "--printCsvImg",
                            help="print csv display image, result folder will be same as input csv file.",
                            action="store_true")
        parser.add_argument("-pt", "--printCsvImgFileType",
                            help="print csv display image file type(jpa. png. bmp.). default is jpg.",
                            type=str)
         
        
        args = parser.parse_args()

        if not args.csv:

            print(">> No input csv file. type `python csvParser.py -h` for help.")
            print(self.__doc__)
            return

        if args.csv:
            self.curPath = str(Path(args.csv).parent.resolve())
            f = open(args.csv, 'r')
            self.inputCsvLine = f.readlines()
            f.close()
            print("Input Csv >> " + f"{args.csv}")
        else:
            print("No input csv file")

        if args.removeClass:
            self.inputCsvLine = [line for i, line in enumerate(self.inputCsvLine) if self.getClass(line) not in args.removeClass]

        if args.removeId:
            self.inputCsvLine = [line for i, line in enumerate(self.inputCsvLine) if self.getID(line) != args.removeId]
        
        if args.removeInFrameTime:
            self.inputCsvLine = [line for i, line in enumerate(self.inputCsvLine) if int(self.getINframe(line)) >= args.removeInFrameTime]
        
        if args.removeOutFrameTime:
            self.inputCsvLine = [line for i, line in enumerate(self.inputCsvLine) if int(self.getOUTframe(line)) <= args.removeOutFrameTime]

        if args.appendCsv:
            f = open(args.appendCsv, 'r')
            appendCsvLine = f.readlines()
            f.close()
            lastID = int(self.getID(self.inputCsvLine[-1]))
            for i in range(0, len(appendCsvLine)):
                temp = appendCsvLine[i].split(',')
                temp[0] = str(int(temp[0]) + lastID)
                appendCsvLine[i] = ','.join(temp)
            self.inputCsvLine.extend(appendCsvLine)
            print("Append Csv >> " + f"{args.appendCsv}")

        if args.printCsvImg:
            if args.printCsvImgFileType:
                self.printCsvImg(self.inputCsvLine, args.csv, fileType = args.printCsvImgFileType)
            else:
                self.printCsvImg(self.inputCsvLine, args.csv)

        if args.save:
            if args.outputCsv:
                outputCsvName =  Path(self.curPath) / args.outputCsv
                f = open(outputCsvName, 'w')
                for i in range(0, len(self.inputCsvLine)):
                    f.write(self.inputCsvLine[i])
                f.close()
                print("Output Csv Save >> " + f"{outputCsvName}")
            else:
                f = open(args.csv, 'w')
                for i in range(0, len(self.inputCsvLine)):
                    f.write(self.inputCsvLine[i])
                f.close()
                print("Output Csv Save >> " + f"{args.csv}")


if __name__ == '__main__':
    currentClass = csvParse()
    currentClass.main()
