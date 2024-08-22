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

def IOadded_main(gateLineIO_txt, tracking_csv, gate_tracking_csv) :
    # fio = open('台北市信義區松仁路_信義路五段路口80米_A_IO.txt', 'r')
    fio = open(gateLineIO_txt, 'r')
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

    p_area_pts = np.zeros((100, 2), np.int)
    #p_area_type: 0=end of data, 1=AB, 2=BC,... '-'=back to A (e.g.-4=DA, -5=EA) 
    p_area_type = np.zeros(100, np.int)
    typecode = "XABCDEFGHIJKLMNOPQRSTUVW"   

    i = 2     
    lines_num = 2
    for i in range(2, len(lines)):
        if len(lines[i]) > 5:
            lines_num = i+1
            
    if lines_num > 2:
        i = 2     
        cc = 0
        for i in range(2, lines_num):
            V3 = lines[i].split(",")
            j = 0
            for j in range(0, int(len(V3)/2)):
                p_area_type[cc] = i-1
                if i == lines_num-1:
                    p_area_type[cc] = -p_area_type[cc]
                p_area_pts[cc][0] = int(V3[2*j])
                p_area_pts[cc][1] = int(V3[2*j+1])
                cc = cc+1    
        
    #frame = cv2.imread('bk.jpg')
    #cv2.drawContours(frame, [contour], -1, (0, 255, 0), 5)   
    #frame = cv2.resize(frame, (1024, 540))
    #cv2.imshow('scene', frame) 
    #cv2.waitKey(100)

    # fp = open('台北市信義區松仁路_信義路五段路口80米_A.csv', 'r')
    fp = open(tracking_csv, 'r')
    lines = fp.readlines()

    # fout = open('台北市信義區松仁路_信義路五段路口80米_A_gate.csv', 'w')
    fout = open(gate_tracking_csv, 'w')

    i = 0
    for i in range(0, len(lines)):
        V = lines[i].split(",")
        
        if V[5] == 'p' or V[5] == 'u':
            if p_area_type[1] == 1:
                Cx = int((int(V[6])+int(V[8])+int(V[10])+int(V[12]))/4)
                Cy = int((int(V[7])+int(V[9])+int(V[11])+int(V[13]))/4)
                j = 0
                mindist = 9999
                minidx = -1
                for j in range(0, 100):
                    if p_area_type[j] == 0:
                        break
                    if p_area_type[j] == p_area_type[j+1]:
                        dist = P2L((p_area_pts[j][0],p_area_pts[j][1]),(p_area_pts[j+1][0],p_area_pts[j+1][1]),(Cx,Cy))
                        if dist < mindist:
                            mindist = dist
                            minidx = j
                if p_area_type[minidx] > 0:           
                    V[3] = typecode[p_area_type[minidx]]+typecode[p_area_type[minidx]+1]
                elif p_area_type[minidx] < 0:
                    V[3] = typecode[-p_area_type[minidx]]+'A'
                    
                Cx = int((int(V[-8])+int(V[-6])+int(V[-4])+int(V[-2]))/4)
                Cy = int((int(V[-7])+int(V[-5])+int(V[-3])+int(V[-1]))/4)
                j = 0
                mindist = 9999
                minidx = -1
                for j in range(0, 100):
                    if p_area_type[j] == 0:
                        break
                    if p_area_type[j] == p_area_type[j+1]:
                        dist = P2L((p_area_pts[j][0],p_area_pts[j][1]),(p_area_pts[j+1][0],p_area_pts[j+1][1]),(Cx,Cy))
                        if dist < mindist:
                            mindist = dist
                            minidx = j
                if p_area_type[minidx] > 0:           
                    V[4] = typecode[p_area_type[minidx]]+typecode[p_area_type[minidx]+1]
                elif p_area_type[minidx] < 0:
                    V[4] = typecode[-p_area_type[minidx]]+'A'
            else:       
                V[3] = 'X'
                V[4] = 'X'
            V = ",".join(V)
            fout.writelines(V)
            continue        

        firstenter = False
        lastenter = False    

        j = 6
        for j in range(6, len(V), 8):
            Cx = int((int(V[j])+int(V[j+2])+int(V[j+4])+int(V[j+6]))/4)
            Cy = int((int(V[j+1])+int(V[j+3])+int(V[j+5])+int(V[j+7]))/4)
            
            if cv2.pointPolygonTest(contour, (Cx, Cy), False) >= 0:
                if not firstenter:
                    firstenter = True
                    
                    minidx = len(bordertype)-1
                    if bordertype[minidx] > 0:
                        mindist = P2L(pts[minidx], pts[0], (Cx,Cy))
                    else:
                        mindist = 9999

                    k = 0                    
                    for k in range(0, len(bordertype)-1):
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
                minidx = len(bordertype)-1
                if bordertype[minidx] < 0:
                    mindist = P2L(pts[minidx], pts[0], (Cx,Cy))
                else:
                    mindist = 9999

                k = 0                    
                for k in range(0, len(bordertype)-1):
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
