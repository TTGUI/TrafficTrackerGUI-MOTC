import numpy as np
import cv2
import sys
import math
import re
from config import conf

video = cv2.VideoCapture(conf.stab_video)
if not video.isOpened():
    sys.exit()
    


fourcc = cv2.VideoWriter_fourcc(*'FMP4')
out = cv2.VideoWriter(conf.result_video,fourcc, 9.99, (2048,1080))

# 0`p`:行人(紅) 1`u`:自行車(橘) 2`m`:機車(黃) 3`c`:小客車(白) 4`t`:貨車(綠) 5`b`:大客車(水藍) 6`h`:聯結車頭(粉紅) 7`g`:聯結車身(藍) 
typecode = "pumctbhg"
colors = [(0,0,255), (0,128,255), (0,255,255), (255,255,255), (0,255,0), (255,255,0), (255,0,255), (255,0,0)]
# fp = open("C_高雄市鼓山區裕誠路 & 博愛二路_gate.csv", "r") 
fp = open(conf.gate_tracking_csv, "r") 

lines = fp.readlines()
fp.close()

V = []
V.append([])
for j in range(0, len(lines)):
    V.append([])
    T = lines[j].split(",")
    for k in range(0, len(T)):
        V[j].append(T[k])


#fio = open('C_高雄市鼓山區裕誠路 & 博愛二路_IO.txt', 'r')
fio = open(conf.gateLineIO_txt, 'r')
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
            cv2.line(frame, pts[j], pts[j+1], (0, 255, 0), 5)
        elif bordertype[j] < 0:
            cv2.line(frame, pts[j], pts[j+1], (0, 0, 255), 5)    
    
    
    
    print(i)
    j = 0    
    for j in range(0, len(lines)):
    
        if i >= int(V[j][1]) and i <= int(V[j][2]):           
            idx = 6+8*(i-int(V[j][1]))   
            k = 0
            for k in range(0, 8):
                pos[k] = int(V[j][idx+k])
                
            if pos[0] > 0:    
                cv2.putText(frame, str(V[j][0]), (int((pos[0]+pos[4])/2)-30, int((pos[1]+pos[5])/2)+10), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,0), 6)
                cv2.putText(frame, str(V[j][0]), (int((pos[0]+pos[4])/2)-30, int((pos[1]+pos[5])/2)+10), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,0), 2)
                cv2.putText(frame, str(V[j][0])+V[j][3][0]+V[j][4][0], (int((pos[0]+pos[4])/2)-50, int((pos[1]+pos[5])/2)+10), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,0), 6)
                cv2.putText(frame, str(V[j][0])+V[j][3][0]+V[j][4][0], (int((pos[0]+pos[4])/2)-50, int((pos[1]+pos[5])/2)+10), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,0), 2)
                cv2.line(frame, (pos[0], pos[1]), (pos[2], pos[3]), (0, 0, 255), 4)
                cv2.line(frame, (pos[2], pos[3]), (pos[4], pos[5]), colors[typecode.find(str(V[j][5]))], 4)
                cv2.line(frame, (pos[4], pos[5]), (pos[6], pos[7]), colors[typecode.find(str(V[j][5]))], 4)
                cv2.line(frame, (pos[6], pos[7]), (pos[0], pos[1]), colors[typecode.find(str(V[j][5]))], 4)


    frame2_resized = cv2.resize(frame, (1024, 540), cv2.INTER_AREA)
    cv2.imshow('frame',frame2_resized)

    temp_resize = cv2.resize(frame, (2048,1080), cv2.INTER_AREA)

    out.write(temp_resize)    

    cv2.waitKey(1)
###############################################################################
#    if(i>=2):
#        cv2.imwrite(str(i+10000)+".jpg", frame)
###############################################################################
out.release()
video.release()  
cv2.destroyAllWindows()