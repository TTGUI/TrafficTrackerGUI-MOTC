import os
import pathlib
import cv2
import numpy as np

# 繪製CSV軌跡
# 並將軌跡結果另存於\csvPrintResult\

curPath = str(pathlib.Path(__file__).parent.resolve())
csvName = '苗栗縣至公路_文發路_民族路路口120米_B_new20230110_gate.csv'
inName = curPath + '\\' + csvName
csvResultPath = curPath + '\\' + 'csvPrintResult\\'
fileType = '.jpg'                                       # result Image file type(jpa. png. bmp.) 


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
if not os.path.isdir(csvResultPath):
    os.mkdir(csvResultPath)
print (">>>  " + inName)

f = open(inName, 'r')
lines = f.readlines()

f.close()

        
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

outputTitel = csvResultPath + csvName[0:7]  + csvName[-11:-8]


text = 'All   Type:All' + "   (" +  str(countAll) + ")"
cv2.putText(img, text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 1, cv2.LINE_AA)
cv2.imshow('ALL',img)
cv2.imencode(ext=fileType,img=img)[1].tofile( outputTitel + 'All_Type_All' + "(" +  str(countAll) + ")" + fileType)

countTemp = getCountABCD(countA)
text = 'AI   Type:All' + "   (" +  str(countTemp) + ")"
cv2.putText(AI, text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 1, cv2.LINE_AA)
cv2.imshow('AI',AI)
cv2.imencode(ext=fileType,img=AI)[1].tofile( outputTitel + 'AI_Type_All' + "(" +  str(countTemp) + ")" + fileType)

for i in range (0, len(Aout)):
    A = 'A'
    fileName = 'AI' + chr(ord(A) + i ) + 'O_Type_All' + "(" +  str(countA[i]) + ")"  + fileType
    text = 'AI'+ chr(ord(A) + i ) + 'O' + '   Type:All' + "   (" +  str(countA[i]) + ")"
    cv2.putText(Aout[i], text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 1, cv2.LINE_AA)
    cv2.imencode(ext=fileType,img=Aout[i])[1].tofile( outputTitel + fileName )

countTemp = getCountABCD(countB)
text = 'BI   Type:All' + "   (" +  str(countTemp) + ")"
cv2.putText(BI, text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 1, cv2.LINE_AA)
cv2.imshow('BI',BI)
cv2.imencode(ext=fileType,img=BI)[1].tofile( outputTitel + 'BI_Type_All' + "(" +  str(countTemp) + ")" + fileType)
for i in range (0, len(Bout)):
    A = 'A'
    fileName = 'BI' + chr(ord(A) + i ) + 'O_Type_All' + "(" +  str(countB[i]) + ")"  + fileType
    text = 'BI'+ chr(ord(A) + i ) + 'O' + '   Type:All' + "   (" +  str(countB[i]) + ")"
    cv2.putText(Bout[i], text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 1, cv2.LINE_AA)
    cv2.imencode(ext=fileType,img=Bout[i])[1].tofile( outputTitel + fileName )

countTemp = getCountABCD(countC)
text = 'CI   Type:All' + "   (" +  str(countTemp) + ")"
cv2.putText(CI, text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 1, cv2.LINE_AA)
cv2.imshow('CI',CI)
cv2.imencode(ext=fileType,img=CI)[1].tofile( outputTitel + 'CI_Type_All' + "(" +  str(countTemp) + ")" + fileType)
for i in range (0, len(Cout)):
    A = 'A'
    fileName = 'CI' + chr(ord(A) + i ) + 'O_Type_All' + "(" +  str(countC[i]) + ")"  + fileType
    text = 'CI'+ chr(ord(A) + i ) + 'O' + '   Type:All' + "   (" +  str(countC[i]) + ")"
    cv2.putText(Cout[i], text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 1, cv2.LINE_AA)
    cv2.imencode(ext=fileType,img=Cout[i])[1].tofile( outputTitel + fileName )

countTemp = getCountABCD(countD)
text = 'DI   Type:All' + "   (" +  str(countTemp) + ")"
cv2.putText(DI, text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 1, cv2.LINE_AA)
cv2.imshow('DI',DI)
cv2.imencode(ext=fileType,img=DI)[1].tofile( outputTitel + 'DI_Type_All' + "(" +  str(countTemp) + ")" + fileType)
for i in range (0, len(Dout)):
    A = 'A'
    fileName = 'DI' + chr(ord(A) + i ) + 'O_Type_All' + "(" +  str(countD[i]) + ")"  + fileType
    text = 'DI'+ chr(ord(A) + i ) + 'O' + '   Type:All' + "   (" +  str(countD[i]) + ")"
    cv2.putText(Dout[i], text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), 1, cv2.LINE_AA)
    cv2.imencode(ext=fileType,img=Dout[i])[1].tofile( outputTitel + fileName )
cv2.waitKey(0)   
