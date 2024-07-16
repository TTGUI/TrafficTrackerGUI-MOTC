import cv2
import numpy as np
import os

# 打開影片
folder = r'D:\Traffic\Block17\桃園市\1130705_桃園市中壢區中華路一段成功路口_120M\A架次\空拍影片\HD(穩像影片)'
stabFileName = "桃園市中壢區中華路一段成功路口A_stab.avi"
stabPath = os.path.join(os.path.abspath(folder), stabFileName)
print(stabPath)
# cap = cv2.VideoCapture('國道3號忠和交流道_300米_20240521_162413_C架次_6Kcpu_stab.avi')
cap = cv2.VideoCapture(stabPath)
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

frame2 = np.zeros((1920,1920,3), dtype=np.uint8)

# 設置視頻輸出
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
# out = cv2.VideoWriter('國道3號忠和交流道_300米_20240521_162413_C架次_reshape.avi', fourcc, 10, (1920, 1920))
outputName = "桃園市中壢區中華路一段成功路口A_reshape.avi"
outputPath = os.path.join(os.path.abspath(folder), outputName)
out = cv2.VideoWriter(outputPath, fourcc, 10, (1920, 1920))


# cap.set(cv2.CAP_PROP_POS_FRAMES, 3600)

# i = -1

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # i = i+1

    # if i%3 != 0:
    #     continue
    # if i > 25200:
    #     break    

    # center = (w // 2, h // 2)
    # 取得旋轉矩陣，並在旋轉時保留圖像的邊界
    # M = cv2.getRotationMatrix2D(center, -20, 1.0)
    # 旋轉圖像
    # r_frame = cv2.warpAffine(frame, M, (w, h), borderValue=(255,255,255))
    # 3840x2160
    # (x,y,w,h) = (600,800,1920,960)
    # (x,y,w,h) = (1920,800,1920,960)
    frame2[0:960,:,:] = frame[800:800+960,600:600+1920,:]
    frame2[960:1920,:,:] = frame[800:800+960,1920:1920+1920,:]
    #5452x3056
    # (x,y,w,h) = (2620,1700,1920,440)
    # (x,y,w,h) = (1330,1770,1920,780)
    # (x,y,w,h) = (0,2070,1920,700)
    # frame2[0:440,:,:] = frame[1700:1700+440,2620:2620+1920,:]
    # frame2[440:1220,:,:] = frame[1770:1770+780,1330:1330+1920,:]
    # frame2[1220:1920,:,:] = frame[2070:2070+700,0:0+1920,:]

    out.write(frame2)
    cv2.imshow('frame', frame2)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()