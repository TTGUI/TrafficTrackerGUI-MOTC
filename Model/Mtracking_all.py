import numpy as np
import cv2
import re
from Model.sort import *
import sys
import math
import pandas as pd
from logs import logger

#------------------------------------------------------------------------------
def inv_rotated_image(image, center, theta, width, height):
   ''' 
   Rotates OpenCV image around center with angle theta (in deg)
   then crops the image according to width and height.
   '''
   # Uncomment for theta in radians
   #theta *= 180/np.pi
   shape = (image.shape[1], image.shape[0]) # cv2.warpAffine expects shape in (length, height)
   matrix = cv2.getRotationMatrix2D( center=center, angle=theta, scale=1)
   image = cv2.warpAffine( src=image, M=matrix, dsize=shape)
   x = int(center[0] - width/2)
   y = int(center[1] - height/2)
   image = image[y:y+height, x:x+width]
   return image
#------------------------------------------------------------------------------
def rotate_box(w, h, cx, cy, angle):
#    if w%2 == 1:
#        w = w-1
#    if h%2 == 1:
#        h = h-1        
    c=math.cos(angle)/2
    s=math.sin(angle)/2
    p = np.zeros((4,2), np.float)
    p[0][0] = w*c-h*s+cx
    p[0][1] = w*s+h*c+cy
    p[1][0] = w*c+h*s+cx
    p[1][1] = w*s-h*c+cy   
    p[2][0] = -w*c+h*s+cx
    p[2][1] = -w*s-h*c+cy
    p[3][0] = -w*c-h*s+cx
    p[3][1] = -w*s+h*c+cy   

    box = np.int0(p)
    
    return box
#------------------------------------------------------------------------------

def Tracking_main(stab_video,yolo_txt,tracking_csv) :
    # 讀入穩定化影片
    video = cv2.VideoCapture(stab_video)
    #"C_高雄市鼓山區裕誠路 _ 博愛二路.avi"

    # 讀入影片對應之Oriented YOLOv4偵測結果
    txt = open(yolo_txt, "r")
    # yolo_txt = frameNumber, class, conf, ( x1, y1 ) ~ ( x4, y4 ) 逆時針
    if not video.isOpened():
        sys.exit()
    first_frame = True
    #ok, frame = video.read()

    mot_tracker = Sort()

    # 預設 20000條以內軌跡  10fps下20分鐘(20mins*60secs*10fps*[中心座標(2) or 4角點(8)]=[24000 or 96000])以內影片
    trackNumber = 70000 # 20000
    centers = np.zeros((trackNumber,30000), np.short) #24000
    corners = np.zeros((trackNumber,120000), np.short) #96000
    # 車中心至車頭方向
    heads = np.zeros((trackNumber,30000), np.short)
    # 0:行人(紅) 1:自行車(橘) 2:機車(黃) 3:小客車(白) 4:貨車(綠) 5:大客車(水藍) 6:聯結車頭(粉紅) 7:聯結車身(藍) 
    typecode = "pumctbhg"
    colors = [(0,0,255), (0,128,255), (0,255,255), (255,255,255), (0,255,0), (255,255,0), (255,0,255), (255,0,0)]
    types = np.zeros((trackNumber,8), np.short)
    enableID = np.zeros(trackNumber, bool)

    #Mdata2=[]
    #Mdata2.append([])
    #Mdata2.append([])

    # 新增csv軌跡檔
    fp = open(tracking_csv, "w")
    # with open(conf.tracking_csv, "w") as f:
    #     f.readlines()
    #fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    #out = cv2.VideoWriter("A_高雄市鼓山區裕誠路 & 博愛二路_detection.avi",fourcc, 9.99, (2048,1080))

    framecount = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    print("ALL Frames : " + str(framecount))


        
    i = 1
    for i in range(1, framecount):   
        line = txt.readline()
        pos_xy = re.split(' ', line)
        pos_len = int(len(pos_xy)/10)
        pos_type = np.zeros(pos_len, np.int)
        conf = np.zeros(pos_len, np.float)
        pos = np.zeros((pos_len,8), np.int)

        ok, frame = video.read()
        if not ok:
            break
        frame2 = frame.copy()
        
    ###############################################################################
        dets = np.ones((pos_len,5), np.float)
    ###############################################################################
        j = 0
        for j in range(0, pos_len): 
            pos_type[j] = int(pos_xy[10*j+1])
            conf[j] = float(pos_xy[10*j+2])
            k = 0
            for k in range(0, 8):
                pos[j][k] = pos_xy[10*j+3+k]
    ###############################################################################
            dets[j,0] = np.min(pos[j][0::2])
            dets[j,1] = np.min(pos[j][1::2])
            dets[j,2] = np.max(pos[j][0::2])
            dets[j,3] = np.max(pos[j][1::2])
            dets[j,4] = conf[j]            
    ###############################################################################
        trackers = mot_tracker.update(dets)    
        for d in trackers:
            ID = int(d[4])            
            enableID[ID] = True
            
            maxiou = 0
            maxidx = -1
            jj = 0
            for jj in range(0, pos_len):
                iouvalue = iou(d[0:3],dets[jj][0:3]) 
                if  iouvalue > maxiou:
                    maxiou = iouvalue
                    maxidx = jj
                    
    #        if maxiou > 0.1 and pos_type[maxidx] == 5: 
            if maxiou > 0.1:             
                types[ID][pos_type[maxidx]] = types[ID][pos_type[maxidx]]+1
                k = 0
                for k in range(0, 8):
                    corners[ID][8*i+k] = pos[maxidx][k]
                centers[ID][2*i] = int((pos[maxidx][0]+pos[maxidx][2]+pos[maxidx][4]+pos[maxidx][6])/4)
                centers[ID][2*i+1] = int((pos[maxidx][1]+pos[maxidx][3]+pos[maxidx][5]+pos[maxidx][7])/4)
                
                heads[ID][2*i] = int((pos[maxidx][0]+pos[maxidx][2])/2 - centers[ID][2*i])
                heads[ID][2*i+1] = int((pos[maxidx][1]+pos[maxidx][3])/2 - centers[ID][2*i+1])
                
                cv2.line(frame, (pos[maxidx][0], pos[maxidx][1]), (pos[maxidx][2], pos[maxidx][3]), (0, 0, 255), 4)
                cv2.line(frame, (pos[maxidx][2], pos[maxidx][3]), (pos[maxidx][4], pos[maxidx][5]), colors[pos_type[maxidx]], 4)
                cv2.line(frame, (pos[maxidx][4], pos[maxidx][5]), (pos[maxidx][6], pos[maxidx][7]), colors[pos_type[maxidx]], 4)
                cv2.line(frame, (pos[maxidx][6], pos[maxidx][7]), (pos[maxidx][0], pos[maxidx][1]), colors[pos_type[maxidx]], 4)
                cv2.putText(frame, str(ID), (int(d[0]),int(d[1])), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,255),2)

    ###############################################################################
    #            px = pos[maxidx][0]
    #            py = pos[maxidx][1]
    #            ox = pos[maxidx][2]
    #            oy = pos[maxidx][3]
    #            qx = pos[maxidx][4]
    #            qy = pos[maxidx][5]
    #            width = int(math.sqrt((px-ox)*(px-ox)+(py-oy)*(py-oy)))
    #            height = int(math.sqrt((qx-ox)*(qx-ox)+(qy-oy)*(qy-oy)))
    #            theta = math.atan2(py-oy, ox-px)
    #            roi = frame2[int(d[1]):int(d[3]), int(d[0]):int(d[2])]
    #            cv2.imwrite('tmp.bmp', roi)
    #            roi2 = inv_rotated_image(roi, ((d[2]-d[0])/2, (d[3]-d[1])/2), theta, width, height)  
    #            
    #            cv2.imshow('vehicle', roi2)
    #            cv2.waitKey(10)
    ###############################################################################
        isShow = False

        if isShow:
            showframe = cv2.resize(frame,(1024,540))
            cv2.imshow('V_pos',showframe) 
    #       out.write(frame) 

            cv2.waitKey(10)
    ###############################################################################
    # i = 0
    for i in range(0, trackNumber) :
        print(i , end='\r')
        if ~enableID[i]:
            continue        
        traj = centers[i]
        traj = traj.reshape(int(traj.shape[0]/2),2)
        df = pd.DataFrame(traj)          
        df[df == 0] = np.nan

        startframe = df.first_valid_index()
        endframe = df.last_valid_index()    
        if endframe-startframe < 5:
            continue
                
        df = df.loc[startframe:endframe].interpolate(method='linear')

        #T = df.as_matrix()
        T = df.values
        T = T.reshape(2*(endframe-startframe+1))
    ###############################################################################    
    # ID, startframe, endframe
        fp.write(str(int(i))+","+str(startframe)+","+str(endframe-1)+",")
    # In, Out
        fp.write("X,X,")
    # Type
        fp.write(typecode[np.argmax(types[i])])

    ###############################################################################    
    # Pos[4]
        last2frame = 2*(endframe-startframe)
        AA = 0
        j = 0
        preAA = 9999
        preh = 0
        prew = 0
        
        for j in range(0, last2frame, 2) :                
            j2 = j
            dist = 0
            for j2 in range(j+2, last2frame+2, 2):
                dist = math.sqrt((T[j2]-T[j])*(T[j2]-T[j])+(T[j2+1]-T[j+1])*(T[j2+1]-T[j+1]))
                if  dist > 10:
                    break
            ss = 8*startframe+4*j    
            if dist > 10:
                #軌跡角度可信
                sx = T[j2]-T[j]
                sy = T[j2+1]-T[j+1]
                AA = math.atan2(sy, sx)
                w = math.sqrt(math.pow(corners[i][ss]-corners[i][ss+2], 2)+math.pow(corners[i][ss+1]-corners[i][ss+3], 2))
                h = math.sqrt(math.pow(corners[i][ss+4]-corners[i][ss+2], 2)+math.pow(corners[i][ss+5]-corners[i][ss+3], 2))
                j2 = 0
                if centers[i][int(ss/4)] == 0 and centers[i][int(ss/4+1)] == 0:
                    #前身長寬可信
                    box = rotate_box(preh, prew, T[j], T[j+1], AA)
                    for j2 in range(0,4):    
                        fp.write(","+str(int(box[j2][0]))+","+str(int(box[j2][1])))

                else:
                    #自身長寬可信
                    AA2 = math.atan2(heads[i][int(ss/4)], heads[i][int(ss/4+1)])
                    prew = w
                    preh = h  
                    # if math.acos(math.cos(max(AA2,AA)-min(AA2,AA))) < math.pi/3:  #大於60度
                    if abs(AA2 - AA) < math.pi/3:  #大於60度
                        #軌跡角度可信
                        if preAA == 9999:
                            box = rotate_box(h, w, T[j], T[j+1], AA)
                        else:
                            box = rotate_box(h, w, T[j], T[j+1], AA)  
                        for j2 in range(0,4):    
                            fp.write(","+str(int(box[j2][0]))+","+str(int(box[j2][1])))
                    else:
                        #自身角度可信 
                        preAA = AA
                        for j2 in range(0, 8, 2):    
                            fp.write(","+str(corners[i][ss+j2])+","+str(corners[i][ss+j2+1])) 
            else:
                #前例軌跡角度可信
                j2 = 0
                if centers[i][int(ss/4)] == 0 and centers[i][int(ss/4+1)] == 0:
                    #前身長寬可信
                    box = rotate_box(preh, prew, T[j], T[j+1], AA)
                    for j2 in range(0,4):    
                        fp.write(","+str(int(box[j2][0]))+","+str(int(box[j2][1])))
                else:
                    #自身長寬可信
                    prew = math.sqrt(math.pow(corners[i][ss]-corners[i][ss+2], 2)+math.pow(corners[i][ss+1]-corners[i][ss+3], 2))
                    preh = math.sqrt(math.pow(corners[i][ss+4]-corners[i][ss+2], 2)+math.pow(corners[i][ss+5]-corners[i][ss+3], 2))
                    for j2 in range(0, 8, 2):    
                        fp.write(","+str(corners[i][ss+j2])+","+str(corners[i][ss+j2+1]))
                        
        fp.write("\n")         
        
        
    fp.close()    
    #out.release()

    cv2.waitKey(100)            
    cv2.destroyAllWindows()
    logger.info("[Mtracking_all.py] ->> save file :" + tracking_csv)    