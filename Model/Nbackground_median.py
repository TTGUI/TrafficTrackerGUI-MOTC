import numpy as np
import cv2
import scipy.ndimage
from config import conf


def Backgroung_main(stab_video,background_img):
    cap = cv2.VideoCapture(stab_video)
    frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frameWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frameHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))


    buf = np.empty((31, frameHeight, frameWidth, 3), np.dtype('uint8'))

    fc = 0
    ret = True
    skipframes = frameCount/30

    while (fc < frameCount and ret):
        if int(fc%skipframes) == 0:
            ret, buf[int(fc/skipframes)] = cap.read()
            cv2.imshow("background", buf[int(fc/skipframes)])
            cv2.waitKey(20) 
        else:
            cap.read()        
        fc = fc+1

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

