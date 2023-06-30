import numpy as np
import cv2
import sys
import math
from config import conf

def P2L(Lp1,Lp2,p):
    # c=((a·b)/(b·b))·b
    a = np.array([p[0]-Lp1[0], p[1]-Lp1[1]])
    b = np.array([Lp2[0]-Lp1[0], Lp2[1]-Lp1[1]])
    if sum(a*b) <= 0:
        dist = np.sqrt((p[0]-Lp1[0])*(p[0]-Lp1[0])+(p[1]-Lp1[1])*(p[1]-Lp1[1]))
        return dist
    elif sum(a*b) >= (Lp2[0]-Lp1[0])*(Lp2[0]-Lp1[0])+(Lp2[1]-Lp1[1])*(Lp2[1]-Lp1[1]):
        dist = np.sqrt((p[0]-Lp2[0])*(p[0]-Lp2[0])+(p[1]-Lp2[1])*(p[1]-Lp2[1]))
        return dist
    else:        
        c = b.dot((float(a.dot(b))/b.dot(b)))
        dist = np.sqrt((a-c).dot(a-c))    
        return dist
    
fio = open(conf.gateLineIO_txt, 'r')
# fio = open('C_高雄市鼓山區裕誠路 & 博愛二路_IO.txt', 'r')
lines = fio.readlines()
fio.close()

V = lines[0].split(",")
V2 = lines[1].split(",")
pts = np.zeros((len(V)-1, 2), np.int)
bordertype = np.zeros(len(V)-1, np.int)

i = 0
for i in range(0, len(V)-1):
    bordertype[i] = int(V[i])  
    pts[i][0] = int(V2[2*i])
    pts[i][1] = int(V2[2*i+1])
    
contour = pts.reshape((-1,1,2))    
    
#frame = cv2.imread('bk.jpg')
#cv2.drawContours(frame, [contour], -1, (0, 255, 0), 5)   
#frame = cv2.resize(frame, (1024, 540))
#cv2.imshow('scene', frame) 
#cv2.waitKey(100)

# fp = open('C_高雄市鼓山區裕誠路 & 博愛二路.csv', 'r')
fp = open(conf.tracking_csv, 'r')
lines = fp.readlines()

# fout = open('C_高雄市鼓山區裕誠路 & 博愛二路_gate.csv', 'w')
fout = open(conf.gate_tracking_csv, 'w')

i = 0
for i in range(0, len(lines)):
    V = lines[i].split(",")
    firstenter = False
    lastenter = False    

    j = 6
    for j in range(6, len(V), 8):
        Cx = int((int(V[j])+int(V[j+2])+int(V[j+4])+int(V[j+6]))/4)
        Cy = int((int(V[j+1])+int(V[j+3])+int(V[j+5])+int(V[j+7]))/4)
        
        if cv2.pointPolygonTest(contour, (Cx, Cy), False) >= 0:
            if not firstenter:
                firstenter = True
                
                minidx = len(bordertype)-2
                if bordertype[minidx] > 0:
                    mindist = P2L(pts[minidx], pts[0], (Cx,Cy))
                else:
                    mindist = 9999

                k = 0                    
                for k in range(0, len(bordertype)-2):
                    if bordertype[k] > 0:
                        dist = P2L(pts[k], pts[k+1], (Cx,Cy))
                        if dist < mindist:
                            mindist = dist
                            minidx = int(k)     
                if (mindist > 100):
                    V[3] = 'X'
                else:
                    V[3] = chr(int(64+bordertype[minidx]))+'I'

            lastenter = True    
            
        elif lastenter:
            minidx = len(bordertype)-2
            if bordertype[minidx] < 0:
                mindist = P2L(pts[minidx], pts[0], (Cx,Cy))
            else:
                mindist = 9999

            k = 0                    
            for k in range(0, len(bordertype)-2):
                if bordertype[k] < 0:
                    dist = P2L(pts[k], pts[k+1], (Cx,Cy))
                    if dist < mindist:
                        mindist = dist
                        minidx = int(k)     
            if (mindist > 100):
                V[4] = 'X'
            else:
                V[4] = chr(int(64-bordertype[minidx]))+'O'

            lastenter = False
    V = ",".join(V)
    fout.writelines(V)

fp.close()    
fout.close()
