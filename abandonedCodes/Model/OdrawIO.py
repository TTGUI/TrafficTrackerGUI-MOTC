import cv2
import numpy as np
from config import conf

point1 = (0, 0)
tpPointsChoose = []
drawing = False
gate = []

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

def draw_ROI(event, x, y, flags, param):
    global point1, tpPointsChoose,pts,drawing
    if event == cv2.EVENT_LBUTTONDOWN and (len(tpPointsChoose) == 0 or drawing == True):
        drawing = True
        point1 = (x, y)
        tpPointsChoose.append((x, y))  # 用于画点
    elif event == cv2.EVENT_RBUTTONDOWN and len(tpPointsChoose) >= 3:
        if drawing == True:
            drawing = False
            pts = np.array([tpPointsChoose], np.int)
            print(pts)
            for i in range(len(tpPointsChoose)):
                gate.append(0)
        else:
            mindist = P2L(tpPointsChoose[-1], tpPointsChoose[0], (x, y))
            idxi = -1
            for i in range(len(tpPointsChoose)-1):
                dist = P2L(tpPointsChoose[i], tpPointsChoose[i+1], (x, y))
                if dist < mindist:
                    mindist = dist
                    idxi = i
            gate[idxi] = (gate[idxi]+1)%3
            
        fp = open(conf.gateLineIO_txt, "w")  # output file setting
        i - 0
        idcount = 1
        for i in range(len(tpPointsChoose)):
            if gate[i] == 0:
                idcount = idcount+1            
                fp.write('0,')
            elif gate[i] == 1:
                fp.write(str(idcount)+',')
            elif gate[i] == 2:
                fp.write(str(-idcount)+',')
        fp.write("\n") 
        i - 0
        for i in range(len(tpPointsChoose)):
            fp.write(str(int(tpPointsChoose[i][0]*2))+","+str(int(tpPointsChoose[i][1]*2))+",")
        fp.close()    
        
            
    elif event == cv2.EVENT_MBUTTONDOWN and len(tpPointsChoose) > 0:
        drawing = True
        tpPointsChoose.pop(-1)
        pts = []
    elif event == cv2.EVENT_MOUSEMOVE:
        point1 = (x, y)
               
cv2.namedWindow('scene')
cv2.setMouseCallback('scene',draw_ROI)
import os
if os.name == 'nt':
    frame = cv2.imdecode(np.fromfile(conf.background_img,dtype=np.uint8),-1)
    frame = cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
else:
    frame = cv2.imread(conf.background_img)
frame = cv2.resize(frame, (int(frame.shape[1]/2), int(frame.shape[0]/2)), interpolation=cv2.INTER_CUBIC)
colors = [(255, 255, 255), (0, 255, 0), (0, 0, 255)]

while True:
    frame2 = frame.copy()
    # display the resulting frame
    if drawing == True:  # 鼠标点击
        cv2.circle(frame2, point1, 5, (0, 255, 0), 2)
        for i in range(len(tpPointsChoose) - 1):
            cv2.line(frame2, tpPointsChoose[i], tpPointsChoose[i + 1], (255, 0, 0), 2)
        cv2.line(frame2, tpPointsChoose[-1], point1, (255, 0, 0), 2)    
    elif len(tpPointsChoose) >= 3:
        i = -1
        for i in range(-1, len(tpPointsChoose)-1):
            cv2.line(frame2, tpPointsChoose[i], tpPointsChoose[i+1], colors[gate[i]], 2)
            
    cv2.imshow('scene', frame2)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # 按q键退出
        break
    
cv2.destroyAllWindows() 