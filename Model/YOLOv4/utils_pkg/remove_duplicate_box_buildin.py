from .Rotated_IoU import oriented_iou_loss
import math
import numpy as np
import torch
from pathlib import Path
import time

def remove_duplicate_box(path, iou_thres=0.8):
    print("remove duplicate box...", end="\r")
    start = time.time()
    with open(path, 'r') as infile:
        lines = infile.readlines()

    tokens = [line.strip().split(' ') for line in lines]

    output_8cls_str_temp = ''
    # loop frame
    ind = 0
    for frame_token in tokens:
        ind += 1
        print(f"({ind}/{len(tokens)})", end='\r')
        
        nobj = int((len(frame_token)-1)/10)

        frame_id = frame_token[0]
        

        objs_info = []
        for obj_id in range(nobj):
            obj_cls = frame_token[obj_id*10+1]
            conf = frame_token[obj_id*10+2]
            
            objs_info.append([float(obj_cls), float(conf), float(frame_token[obj_id*10+3]), float(frame_token[obj_id*10+4]), float(frame_token[obj_id*10+5]),
                            float(frame_token[obj_id*10+6]), float(frame_token[obj_id*10+7]), float(frame_token[obj_id*10+8]),
                            float(frame_token[obj_id*10+9]), float(frame_token[obj_id*10+10])])
            

        objs_info_np = np.array(objs_info)
        i = 0
        if len(objs_info_np) >= 2:
            while i < len(objs_info_np)-1:
                j = i+1

                while j < len(objs_info_np):
                    objs4xy = objs_info_np[i,2:]
                    objs4xy2 = objs_info_np[j,2:]

                    x = (objs4xy[0]+objs4xy[4])/2
                    y = (objs4xy[1]+objs4xy[5])/2

                    x2 = (objs4xy2[0]+objs4xy2[4])/2
                    y2 = (objs4xy2[1]+objs4xy2[5])/2

                    if ((x2-x)**2+(y2-y)**2)**0.5 < 20:
                        w = ((objs4xy[2]-objs4xy[0])**2+(objs4xy[3]-objs4xy[1])**2)**0.5
                        h = ((objs4xy[4]-objs4xy[2])**2+(objs4xy[5]-objs4xy[3])**2)**0.5
                        fpx = (objs4xy[0]+objs4xy[2])/2
                        fpy = (objs4xy[1]+objs4xy[3])/2
                        dx, dy = fpx-x, fpy-y
                        theta = torch.atan2(torch.tensor(-dy),torch.tensor(dx))
                        theta = torch.where(theta<0, theta+2*math.pi, theta)
                        iou_y = -y
                        iou_theta = torch.where(theta-math.pi/2<0, theta-math.pi/2+2*math.pi, theta-math.pi/2)
                        b1 = torch.tensor([x,iou_y,w,h,iou_theta])

                        w = ((objs4xy2[2]-objs4xy2[0])**2+(objs4xy2[3]-objs4xy2[1])**2)**0.5
                        h = ((objs4xy2[4]-objs4xy2[2])**2+(objs4xy2[5]-objs4xy2[3])**2)**0.5
                        fpx = (objs4xy2[0]+objs4xy2[2])/2
                        fpy = (objs4xy2[1]+objs4xy2[3])/2
                        dx, dy = fpx-x2, fpy-y2
                        theta = torch.atan2(torch.tensor(-dy),torch.tensor(dx))
                        theta = torch.where(theta<0, theta+2*math.pi, theta)
                        iou_y = -y2
                        iou_theta = torch.where(theta-math.pi/2<0, theta-math.pi/2+2*math.pi, theta-math.pi/2)
                        b2 = torch.tensor([x2,iou_y,w,h,iou_theta])

                        # iou,_,_,_ = oriented_iou_loss.cal_iou(b1.unsqueeze(0).unsqueeze(0).cuda(), b2.unsqueeze(0).unsqueeze(0).cuda())
                        iou,_,_,_ = oriented_iou_loss.cal_iou(b1.unsqueeze(0).unsqueeze(0).cuda(), b2.unsqueeze(0).unsqueeze(0).cuda(), 0)

                        if iou[0,0] > iou_thres:
                            objs_info_np = np.delete(objs_info_np, j, 0)
                            j-=1
                 
                    j+=1
                i+=1

        output_8cls_str_temp += str(frame_id)
        for obj_info in objs_info_np:
            pts = obj_info[2:].astype(int)
            output_8cls_str_temp += ' ' + str(int(obj_info[0])) + ' ' + '{:.2f}'.format(obj_info[1]) \
                                + ' ' + str(pts[0]) + ' ' + str(pts[1]) \
                                + ' ' + str(pts[2]) + ' ' + str(pts[3]) + ' ' + str(pts[4]) \
                                + ' ' + str(pts[5]) + ' ' + str(pts[6]) + ' ' + str(pts[7])   

        output_8cls_str_temp += '\n'
        
    with open(path, 'w') as outfile:
        outfile.writelines(output_8cls_str_temp)
    end = time.time()
    print(f"remove duplicate box done. cost time: {end-start}s")

if __name__ == '__main__':
    path = "E:/PyTorch_YOLOv4/check_nms/苗栗縣至公路_文發路_民族路路口120米_B_stab_8cls.txt"
    TSPath = u"e:\Traffic\Block01_台北_台南_桃園\台北市信義區松仁路_信義路五段路口80米_C架次\空拍影片\行人偵測分支\20230628行人偵測\台北市信義區松仁路_信義路五段路口80米_C_stab_8cls.txt"
    newP = Path(TSPath)

    remove_duplicate_box(newP,0.8)
    print("done")
