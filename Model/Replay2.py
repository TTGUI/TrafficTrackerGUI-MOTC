import numpy as np
import cv2
import sys
import math
import re
from logs import logger
from tqdm import tqdm

def Replay_main(stab_video, result_video, gate_tracking_csv, gateLineIO_txt, displayType, show) :
    # video = cv2.VideoCapture("台北市信義區松仁路_信義路五段路口80米_A_stab.avi")
    video = cv2.VideoCapture(stab_video)
    
    if not video.isOpened():
        sys.exit()
    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    
    # out = cv2.VideoWriter("台北市信義區松仁路_信義路五段路口80米_A_result.avi",fourcc, 9.99, (1920,1080))
    out = cv2.VideoWriter(result_video, fourcc, video.get(cv2.CAP_PROP_FPS), 
                          (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))))

    # 0`p`:行人(紅) 1`u`:自行車(橘) 2`m`:機車(黃) 3`c`:小客車(白) 4`t`:貨車(綠) 5`b`:大客車(水藍) 6`h`:聯結車頭(粉紅) 7`g`:聯結車身(藍)
    typecode = "pumctbhg"
    colors = [(0,0,255), (0,128,255), (0,255,255), (255,255,255), (0,255,0), (255,255,0), (255,0,255), (255,0,0)]
    
    # fp = open("台北市信義區松仁路_信義路五段路口80米_A_gate.csv", "r")
    fp = open(gate_tracking_csv, "r") 
    lines = fp.readlines()
    fp.close()

    V = [[] for _ in range(len(lines)+1)]
    for j in range(len(lines)):
        T = lines[j].split(",")
        V[j] = T

    # fio = open('台北市信義區松仁路_信義路五段路口80米_A_IO.txt', 'r')
    fio = open(gateLineIO_txt, 'r')
    lines2 = fio.readlines()
    fio.close()

    V2 = lines2[0].split(",")
    V3 = lines2[1].split(",")
    pts = [(int(V3[2*i]), int(V3[2*i+1])) for i in range(len(V2)-1)]
    bordertype = [int(V2[i]) for i in range(len(V2)-1)]
    
    pos = np.zeros(8, np.int)
    framecount = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    # Use tqdm to track the progress of frames processing
    for i in tqdm(range(1, framecount), desc="Processing frames"):
        ok, frame = video.read()
        
        for j in range(len(bordertype)-1):
            if bordertype[j] > 0:
                cv2.line(frame, pts[j], pts[j+1], (0, 255, 0), 3)
            elif bordertype[j] < 0:
                cv2.line(frame, pts[j], pts[j+1], (0, 0, 255), 3)

        for j in range(2, len(lines2)):
            V4 = lines2[j].split(",")
            for k in range(0, len(V4)-3, 2):
                cv2.line(frame, (int(V4[k]), int(V4[k+1])), (int(V4[k+2]), int(V4[k+3])), (255, 0, 0), 2)
        
        for j in range(len(lines)):
            if i >= int(V[j][1]) and i <= int(V[j][2]):           
                idx = 6 + 8 * (i - int(V[j][1]))
                for k in range(8):
                    pos[k] = int(V[j][idx + k])

                if pos[0] > 0:
                    cv2.line(frame, (pos[0], pos[1]), (pos[2], pos[3]), (0, 0, 255), 4)
                    cv2.line(frame, (pos[2], pos[3]), (pos[4], pos[5]), colors[typecode.find(str(V[j][5]))], 4)
                    cv2.line(frame, (pos[4], pos[5]), (pos[6], pos[7]), colors[typecode.find(str(V[j][5]))], 4)
                    cv2.line(frame, (pos[6], pos[7]), (pos[0], pos[1]), colors[typecode.find(str(V[j][5]))], 4)

                    if displayType:
                        cv2.putText(frame, str(V[j][0])+","+V[j][3]+">"+V[j][4], 
                                    (int((pos[0]+pos[4])/2)-50, int((pos[1]+pos[5])/2)+10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 3)
                        cv2.putText(frame, str(V[j][0])+","+V[j][3]+">"+V[j][4], 
                                    (int((pos[0]+pos[4])/2)-50, int((pos[1]+pos[5])/2)+10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

        frame = cv2.resize(frame, (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))), cv2.INTER_AREA)
        if show:
            cv2.imshow('frame', frame)
        out.write(frame)

        cv2.waitKey(1)
        
    out.release()
    video.release()  
    cv2.destroyAllWindows()
    logger.info("[Replay2.py] ->> Output file : " + result_video)
