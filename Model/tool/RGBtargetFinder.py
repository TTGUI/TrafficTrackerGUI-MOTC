
import cv2
import os
import pathlib
import numpy as np

# 工具功能 :
# 於A資料夾下含有資料夾群，根據各資料夾與檔名格式"aaa_幀數.jpg"，並將該畫面轉化為B通道
# 在B資料夾群中搜尋"aaa_幀數正負一.jpg"，並將該兩畫面轉化為R通道與G通道
# 最後將前面3幀提取的RGB合併為一幀後輸出至C資料夾

# fileName format : ABCfolder + subFolderFileList[i] + 路口名稱 + roadCode + frameNumber + .jpg

curPath = str(pathlib.Path(__file__).parent.resolve())  # code file path.
Afolder = curPath + '/A/'      # A資料夾
Bfolder = curPath + '/B_不需標註_其為前後frame影像可用來確認是否是行人用/'      # B資料夾
CFolder = curPath + '/C/' # C資料夾


AfolderList = os.listdir(Afolder)
BfolderList = os.listdir(Bfolder)

if not os.path.isdir(CFolder):
    os.mkdir(CFolder)



for i in range(0,len(AfolderList)):
    subFolderFileList = os.listdir(Afolder+AfolderList[i])  
    BsubFolderFileList = os.listdir(Bfolder+BfolderList[i])

    if not os.path.isdir(CFolder+AfolderList[i]):
        os.mkdir(CFolder+AfolderList[i])
    for j in range(0, len(subFolderFileList)):

        if subFolderFileList[j][-4:] == ".jpg" : # fileType is ".jpg"
            roadCode = subFolderFileList[j][-11:-9]   # road number
            frameNumber = subFolderFileList[j][-8:-4] # frame number
            Apath = Afolder + AfolderList[i] + "\\"+subFolderFileList[j]
            print(Apath)
            # print(roadCode)
            frame1 = cv2.imdecode(np.fromfile(Apath,dtype=np.uint8), -1)
            b, x, rx = cv2.split(frame1)                # b channel

            
            Bpath = Bfolder + BfolderList[i] + "\\"
            frame2 = np.zeros(frame1.shape,np.uint8)    # init
            frame3 = np.zeros(frame1.shape,np.uint8)    # init 
            for k in range(0, len(BsubFolderFileList)) :
                if BsubFolderFileList[k][-8:-4] == str(int(frameNumber) -1) and BsubFolderFileList[k][-11:-9] == roadCode :
                    frame2 = cv2.imdecode(np.fromfile(Bpath+BsubFolderFileList[k],dtype=np.uint8), -1)
                    print ("-1 : " + str(BsubFolderFileList[k]))
                if BsubFolderFileList[k][-8:-4] == str(int(frameNumber) +1) and BsubFolderFileList[k][-11:-9] == roadCode :
                    frame3 = cv2.imdecode(np.fromfile(Bpath+BsubFolderFileList[k],dtype=np.uint8), -1)
                    print ("+1 : " + str(BsubFolderFileList[k]))

            x, g, rx = cv2.split(frame2)    # g channel
            bx, gx, r = cv2.split(frame3)   # r channel

            frameans = np.zeros(frame1.shape,np.uint8)  # init
            frameans = cv2.merge([b,g,r])   # merge rgb channel

            resultPath = CFolder+AfolderList[i] +"\\"
            outputName = subFolderFileList[j][:-4]
            cv2.imencode(ext='.jpg',img=frameans)[1].tofile(resultPath + outputName + '_spRGB_.jpg' )


print("Finish")







    
    


