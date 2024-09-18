import numpy as np
import cv2
import scipy.ndimage
from config import conf
import os

def Backgroung_main(stab_video, background_img, display_callBack):
    cap = cv2.VideoCapture(stab_video)
    frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frameWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frameHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    skipframes = max(int(frameCount / 100), 1)  # 保證至少每隔一幀擷取
    buf = []

    fc = 0
    ret = True

    while fc < frameCount and ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, fc)
        ret, frame = cap.read()
        if ret and fc % skipframes == 0:
            buf.append(frame)
            # cv2.imshow("background", frame)
            cv2.waitKey(20)
            display_callBack(frame)
        fc += skipframes

    cap.release()

    if len(buf) > 0:
        median = np.median(np.array(buf), axis=0).astype(np.uint8)
        
        if os.name == 'nt':
            cv2.imencode(ext='.jpg', img=median)[1].tofile(background_img)
        else:
            cv2.imwrite(background_img, median)

    cv2.destroyAllWindows()


def Backgroung_main_old(stab_video,background_img):
    cap = cv2.VideoCapture(stab_video)
    frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frameWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frameHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))


    buf = np.empty((100, frameHeight, frameWidth, 3), np.dtype('uint8'))

    fc = 0
    ret = True 
    cap.set(cv2.CAP_PROP_POS_FRAMES, fc)
    skipframes = (frameCount-fc)/100

    while (fc < frameCount and ret):
        cap.set(cv2.CAP_PROP_POS_FRAMES, fc)
        if int(fc%skipframes) == 0:
            ret, buf[int(fc/skipframes)] = cap.read()
            cv2.imshow("background", buf[int(fc/skipframes)])
            cv2.waitKey(20) 
        else:
            cap.read()        
        fc = fc + skipframes
        
    cap.release()

    median = np.median(buf, axis=0)
    import os
    if os.name == 'nt':
        cv2.imencode(ext='.jpg',img=median)[1].tofile(background_img)
    else:
        cv2.imwrite(background_img, median)
    # bk = cv2.imread(background_img)
    # cv2.imshow("background", bk)
    # cv2.waitKey(0)
    cv2.destroyAllWindows()

