import cv2
import numpy as np
from logs import logger

# drawIO2 是為了路口設計的

class Draw:
    def __init__(self,io_txt,bk_jpg):
        self.io_txt = io_txt
        self.bk_jpg = bk_jpg

        self.point1 = (0, 0)
        self.tpPointsChoose = []
        self.pts = []
        self.pts.append([])
        self.p_area_num = 1
        self.drawing = False
        self.gate = []
        self.w = 0
        self.h = 0

    def P2L(self,Lp1,Lp2,p):
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

    def draw_ROI(self,event, x, y, flags, param):
        # global self.point1, self.tpPointsChoose, self.pts, self.drawing, self.p_area_num
        
        border = False
        if x < 20:
            x = 0
            border = True
        elif self.w/2-x < 20:
            x = int(self.w/2)  
            border = True
        if y < 20:
            y = 0
            border = True
        elif self.h/2-y < 20:
            y = int(self.h/2)
            border = True
        
        if event == cv2.EVENT_LBUTTONDOWN and (len(self.tpPointsChoose) == 0 or self.drawing == True):
            self.drawing = True
            self.point1 = (x, y)
            self.tpPointsChoose.append((x, y))
        elif event == cv2.EVENT_RBUTTONDOWN and len(self.tpPointsChoose) >= 3:
            if self.drawing == True:
                self.drawing = False

                for i in range(len(self.tpPointsChoose)):
                    self.gate.append(0)
            else:
                mindist = self.P2L(self.tpPointsChoose[-1], self.tpPointsChoose[0], (x, y))
                idxi = -1
                for i in range(len(self.tpPointsChoose)-1):
                    dist = self.P2L(self.tpPointsChoose[i], self.tpPointsChoose[i+1], (x, y))
                    if dist < mindist:
                        mindist = dist
                        idxi = i
                self.gate[idxi] = (self.gate[idxi]+1)%3
                
                fp = open(self.io_txt, "w")            
                i = 0
                idcount = 1
                for i in range(len(self.tpPointsChoose)):
                    if self.gate[i] == 0:
                        idcount = idcount+1            
                        fp.write('0,')
                    elif self.gate[i] == 1:
                        fp.write(str(idcount)+',')
                    elif self.gate[i] == 2:
                        fp.write(str(-idcount)+',')
                fp.write("\n") 
                i = 0
                for i in range(len(self.tpPointsChoose)):
                    fp.write(str(int(self.tpPointsChoose[i][0]*2))+","+str(int(self.tpPointsChoose[i][1]*2))+",")
                fp.close()    
        
        elif event == cv2.EVENT_LBUTTONDOWN and len(self.tpPointsChoose) >= 3 and self.drawing == False:
            if len(self.pts[self.p_area_num-1]) == 0 and border == True:
                self.pts[self.p_area_num-1].append((x,y))
            elif border == True:
                self.pts[self.p_area_num-1].append((x,y))
            
                fp = open(self.io_txt, "a")            
                fp.write("\n")
                j = 0
                for j in range(len(self.pts[self.p_area_num-1])):
                    fp.write(str(int(self.pts[self.p_area_num-1][j][0]*2))+","+str(int(self.pts[self.p_area_num-1][j][1]*2))+",")
                fp.close()    
                
                self.pts.append([])
                self.p_area_num = self.p_area_num+1
            else:
                self.pts[self.p_area_num-1].append((x,y))
                
        elif event == cv2.EVENT_MOUSEMOVE:
            self.point1 = (x, y)

    def main(self):
        cv2.namedWindow('scene')
        import os
        if os.name == 'nt':
            frame = cv2.imdecode(np.fromfile(self.bk_jpg,dtype=np.uint8),-1)
            # frame = cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
        else:
            frame = cv2.imread(self.bk_jpg)
        self.w = frame.shape[1]
        self.h = frame.shape[0]
        frame = cv2.resize(frame, (int(self.w/2), int(self.h/2)), interpolation=cv2.INTER_CUBIC)
        cv2.setMouseCallback('scene',self.draw_ROI)
        colors = [(255, 255, 255), (0, 255, 0), (0, 0, 255), (255, 0, 0)]

        while True:
            frame2 = frame.copy()
            # display the resulting frame
            cv2.circle(frame2, self.point1, 5, (0, 255, 0), 2)
            if self.drawing == True:  
                for i in range(len(self.tpPointsChoose) - 1):
                    cv2.line(frame2, self.tpPointsChoose[i], self.tpPointsChoose[i + 1], colors[0], 2)
                cv2.line(frame2, self.tpPointsChoose[-1], self.point1, colors[0], 2)    
            elif len(self.tpPointsChoose) >= 3:
                i = -1
                for i in range(-1, len(self.tpPointsChoose)-1):
                    cv2.line(frame2, self.tpPointsChoose[i], self.tpPointsChoose[i+1], colors[self.gate[i]], 2)
                i = 0
                for i in range(self.p_area_num):
                    j = 0
                    for j in range(1, len(self.pts[i])):
                        cv2.line(frame2, self.pts[i][j-1], self.pts[i][j], colors[3], 2)
                if len(self.pts[self.p_area_num-1]) > 0:
                    cv2.line(frame2, self.pts[self.p_area_num-1][-1], self.point1, colors[3], 2)

            cv2.imshow('scene', frame2)
            if cv2.waitKey(1) & 0xFF == ord('q'):  # 按q键退出
                break
            
        cv2.destroyAllWindows()
        logger.info("[drawIO2.py] ->> save file : " + self.io_txt) 



