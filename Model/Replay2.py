import numpy as np
import cv2
import sys
import math
import re
from logs import logger

def Replay_main(stab_video, result_video, gate_tracking_csv, gateLineIO_txt, displayType, show) :
    # video = cv2.VideoCapture("台北市信義區松仁路_信義路五段路口80米_A_stab.avi")
    video = cv2.VideoCapture(stab_video)
    
    now = 0

    if not video.isOpened():
        sys.exit()
    tenP = int(video.get(cv2.CAP_PROP_FRAME_COUNT) / 10)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    
    # out = cv2.VideoWriter("台北市信義區松仁路_信義路五段路口80米_A_result.avi",fourcc, 9.99, (1920,1080))
    out = cv2.VideoWriter(result_video,fourcc, video.get(cv2.CAP_PROP_FPS), (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))))

    # 0:行人(紅) 1:自行車(橘) 2:機車(黃) 3:小客車(白) 4:貨車(綠) 5:大客車(水藍) 6:聯結車頭(粉紅) 7:聯結車身(藍) 
    typecode = "pumctbhg"
    colors = [(0,0,255), (0,128,255), (0,255,255), (255,255,255), (0,255,0), (255,255,0), (255,0,255), (255,0,0)]
    # fp = open("台北市信義區松仁路_信義路五段路口80米_A_gate.csv", "r") 
    fp = open(gate_tracking_csv, "r") 

    lines = fp.readlines()
    fp.close()

    V = []
    V.append([])
    for j in range(0, len(lines)):
        V.append([])
        T = lines[j].split(",")
        for k in range(0, len(T)):
            V[j].append(T[k])


    # fio = open('台北市信義區松仁路_信義路五段路口80米_A_IO.txt', 'r')
    fio = open(gateLineIO_txt, 'r')
    lines2 = fio.readlines()
    fio.close()

    V2 = lines2[0].split(",")
    V3 = lines2[1].split(",")
    pts = []
    bordertype = []
    for i in range(0, len(V2)-1):
        bordertype.append(int(V2[i]))
        pts.append((int(V3[2*i]), int(V3[2*i+1])))

    pos = np.zeros(8, np.int)
    framecount = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    i = 1
    for i in range(1, framecount):   
        
        ok, frame = video.read()
        j = -1
        for j in range(-1, len(bordertype)-1):
            if bordertype[j] > 0:
                cv2.line(frame, pts[j], pts[j+1], (0, 255, 0), 3)
            elif bordertype[j] < 0:
                cv2.line(frame, pts[j], pts[j+1], (0, 0, 255), 3)    
        
        j = 2
        for j in range(2, len(lines2)):
            V4 = lines2[j].split(",")
            k = 0
            for k in range(0, len(V4)-3, 2):
                cv2.line(frame, (int(V4[k]), int(V4[k+1])), (int(V4[k+2]), int(V4[k+3])), (255, 0, 0), 2)
        
        if i > ( now * tenP ) :
            print("[ " + str(now*10) + "% ]", end='\r')
            now = now + 1
            
        # print(i)
        j = 0    
        for j in range(0, len(lines)):
        
            if i >= int(V[j][1]) and i <= int(V[j][2]):           
                idx = 6+8*(i-int(V[j][1]))   
                k = 0
                for k in range(0, 8):
                    pos[k] = int(V[j][idx+k])
                    
                if pos[0] > 0:    
                    
                    if displayType :
                        cv2.putText(frame, str(V[j][0]), (int((pos[0]+pos[4])/2)-30, int((pos[1]+pos[5])/2)+10), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,0), 6)
                        cv2.putText(frame, str(V[j][0]), (int((pos[0]+pos[4])/2)-30, int((pos[1]+pos[5])/2)+10), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,0), 2)
                        cv2.putText(frame, str(V[j][0])+V[j][3]+">"+V[j][4], (int((pos[0]+pos[4])/2)-50, int((pos[1]+pos[5])/2)+10), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,0), 6)
                        cv2.putText(frame, str(V[j][0])+V[j][3]+">"+V[j][4], (int((pos[0]+pos[4])/2)-50, int((pos[1]+pos[5])/2)+10), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,0), 2)

                    cv2.line(frame, (pos[0], pos[1]), (pos[2], pos[3]), (0, 0, 255), 4)
                    cv2.line(frame, (pos[2], pos[3]), (pos[4], pos[5]), colors[typecode.find(str(V[j][5]))], 4)
                    cv2.line(frame, (pos[4], pos[5]), (pos[6], pos[7]), colors[typecode.find(str(V[j][5]))], 4)
                    cv2.line(frame, (pos[6], pos[7]), (pos[0], pos[1]), colors[typecode.find(str(V[j][5]))], 4)


        # frame2_resized = cv2.resize(frame, (1024, 540), cv2.INTER_AREA)
        
        frame = cv2.resize(frame, (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))), cv2.INTER_AREA)
        if show:
            cv2.imshow('frame',frame)
        out.write(frame)

        cv2.waitKey(1)
    ###############################################################################
    #    if(i>=2):
    #        cv2.imwrite(str(i+10000)+".jpg", frame)
    ###############################################################################
    out.release()
    video.release()  
    cv2.destroyAllWindows()
    logger.info("[Replay2.py] ->> Output file :" + result_video)