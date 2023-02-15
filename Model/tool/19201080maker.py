import cv2
import os

fourcc = cv2.VideoWriter_fourcc(*'XVID')
inputfolder = "./data/BUG/"
videoList = os.listdir(inputfolder)

print(len(videoList))
print(videoList)
print("=========================")

for i in range(0,len(videoList)):
    
    name = ""
    for j in range(0,len(videoList[i]) -4):
        name = name + videoList[i][j]
    outpath = inputfolder + name  + "_pad_stab.avi"
    input = os.path.join( os.path.abspath(inputfolder), videoList[i])
    print( input)
    print (outpath)
    
    cap = cv2.VideoCapture(input)
    out = cv2.VideoWriter(inputfolder+"temp.avi" ,fourcc, cap.get(cv2.CAP_PROP_FPS),(1920, 1080))
    
    allframe = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    i = 1
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret :
            break
        print (str(i)+" / " + str(allframe), end='\r')
        i = i + 1
        frame = cv2.copyMakeBorder(frame, 0, 28*2, 0, 448*2, cv2.BORDER_CONSTANT, value=(0, 0, 0))
        cv2.imshow('frame',frame)
        cv2.waitKey(1)
        out.write(frame)

    cap.release()
    out.release()

    os.rename(inputfolder+"temp.avi", outpath )
    print("###################")

