import cv2
import math
import numpy as np
import csv
from Model.sort6 import SORT
from Model.sort6 import iou_rotated

def read_file(file_name):
    with open(file_name, 'r') as f:
        lines = f.readlines()
    return lines

def parse_line(line):
    data = list(map(float, line.split()))
    frame_no = int(data[0])
    rects = []
    for i in range(1, len(data), 10):
        class_id = int(data[i])
        conf = data[i+1]
        points = np.array(data[i+2:i+10]).reshape(4, 2)
        rects.append((class_id, conf, points))
    return frame_no, rects

def dist(point1, point2):
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5


def rotated_rect_to_5_params(points2):
    points = np.array(points2, dtype=np.int32).reshape(4, 2)
    rect2 = cv2.minAreaRect(points)
    (cx, cy), (w, h), a = rect2
    # h = math.dist(points[0], points[1]) those code only work in python 3.8 or higher version cause math.dist.
    # w = math.dist(points[0], points[3]) current version is 3.6.7
    h = dist(points[0], points[1])
    w = dist(points[0], points[3])
    a=a+90
    if points[0][0] == min(points[0][0],points[1][0],points[2][0],points[3][0]):
        a = 180 - a
        if points[0][0] == points[1][0]:
            a = 180
    elif points[0][1] == min(points[0][1],points[1][1],points[2][1],points[3][1]):
        a = 90 - a
        if points[0][1] == points[1][1]:
            a = 90          
    elif points[0][1] == max(points[0][1],points[1][1],points[2][1],points[3][1]):
        a = 270 - a
        if points[0][1] == points[1][1]:
            a = 270      
    elif points[0][0] == max(points[0][0],points[1][0],points[2][0],points[3][0]):
        a = 360 - a
        if points[0][0] == points[1][0]:
            a = 0        
    return np.array([cx, cy, w, h, a], dtype=np.float32)

def add_trajectory(dict_IDs, ID, frame, style, pos):
    if ID not in dict_IDs:
        # 初始化一個新的軌跡列表，列表的第一個元素是 ID，第二個元素是 frame，之後是位置
        dict_IDs[ID] = [ID, frame, 0, 0, 0, 0, 0, 0, 0, 0, 0, []]
    
    # 添加新的位置到軌跡列表並更新 frame
    dict_IDs[ID][11].extend([pos])
    dict_IDs[ID][2] = frame
    dict_IDs[ID][3+style] = dict_IDs[ID][3+style] + 1
    return dict_IDs

def interpolate_zeros(pos_list):
    # 找到所有連續零值的範圍（開始和結束索引）
    zero_ranges = []
    start_index = None
    for i in range(1, len(pos_list)-1):
        if np.all(pos_list[i] == 0):  # 使用 numpy 的 all() 來檢查陣列中的所有元素
            if start_index is None:
                start_index = i
        else:
            if start_index is not None:
                zero_ranges.append((start_index, i))
                start_index = None

    # 如果我們在列表的末尾找到零值，我們需要手動添加這個範圍
    if start_index is not None:
        zero_ranges.append((start_index, len(pos_list)))

    # 檢查最後一個零值範圍是否延伸到列表的末尾，如果是的話，刪除這些元素
    if zero_ranges and zero_ranges[-1][1] == len(pos_list):
        pos_list = pos_list[:zero_ranges[-1][0]]
        zero_ranges = zero_ranges[:-1]

    # 對於每個零值範圍，計算開始索引和結束索引之間的位置的插值
    for start_index, end_index in zero_ranges:
        start_pos = pos_list[start_index-1]
        end_pos = pos_list[end_index]

        # 計算插值的增量
        increment = (end_pos - start_pos) / (end_index - start_index + 1)

        # 替換零值
        for i in range(start_index, end_index):
            pos_list[i] = np.round(start_pos + (i - start_index + 1) * increment).astype(int) # 使用 numpy 的 round 函數四捨五入

    return pos_list

def main(stab_video,yolo_txt,tracking_csv,show, trk1_set=(10, 2, 0.01), trk2_set=(10, 2, 0.1)):
    # file_name = '高雄市前鎮區二聖二路_復興三路口80米_A_stab'
    lines = read_file(yolo_txt)   
    
    if show:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        cap = cv2.VideoCapture(stab_video)
        # out = cv2.VideoWriter(tracking_csv[0:-4]+'_result.mp4', fourcc, 9.99, (1920, 1080))
 
    # trackers_1 = SORT(max_age=10, min_hits=2, iou_threshold=0.01)
    # trackers_2 = SORT(max_age=10, min_hits=2, iou_threshold=0.1)
    trackers_1 = SORT(trk1_set[0], trk1_set[1], trk1_set[2])
    trackers_2 = SORT(trk2_set[0], trk2_set[1], trk2_set[2])
    track1 = {} 
    track2 = {}
    count = 1
    for line in lines:
        
        print(f"{count} / {len(lines)}", end='\r')
        count += 1
        frame_no, rects = parse_line(line)
        # frame = np.zeros((1836, 3264, 3), dtype=np.uint8)
        # frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
        if show:
            ret, frame = cap.read()

        i = 0 
        for rect in rects:
            i = i+1
            class_id, conf, points = rect
            points = points.astype(np.int32)
            if show:
                cv2.polylines(frame, [points], True, (0, 255, 255), 4)
                cv2.line(frame, tuple(points[0]), tuple(points[1]), (0, 0, 255), 3)
            center = np.mean(points, axis=0).astype(np.int32)
            # cv2.putText(frame, f"{i}", tuple(center), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        
        rect_5_params2 = [-1,-1,1,1,0]    
        group1 = []
        group2 = []
        for rect in rects:
            class_id, conf, points = rect
            rect_5_params = rotated_rect_to_5_params(points)
            iou = iou_rotated(rect_5_params, rect_5_params2)
            if iou > 0.5:
                # cv2.putText(frame, str(int(iou*100))+'%', (int(rect_5_params[0]), int(rect_5_params[1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 3)
                # cv2.imwrite(str(frame_no)+'.jpg', frame)
                continue
            rect_5_params2 = rect_5_params.copy()
            fullparams = np.concatenate((np.array(rect_5_params).flatten('C'), np.array(points).flatten('C'), [class_id]), axis=0)
    
            
            if class_id in [0, 1, 2]:
                group1.append(fullparams)
            else:
                group2.append(fullparams)

        tracked_objects_1 = trackers_1.update(np.array(group1))
        tracked_objects_2 = trackers_2.update(np.array(group2))

        for track_id, rect, rect2, vote in tracked_objects_1:
            # boxPoints角度定義不同
            # box2 = cv2.boxPoints([(rect[0],rect[1]),(rect[2],rect[3]),180-rect[4]])
            box90 = cv2.boxPoints(((rect[0],rect[1]),(rect[2],rect[3]),-rect[4]))
            # box = np.intp(box2) 
            box = np.intp(box90) 
            # t0 = int(rect[0]+rect[2]/2*math.cos(rect[4] / 180.0 * np.pi))
            # t1 = int(rect[1]-rect[2]/2*math.sin(rect[4] / 180.0 * np.pi))
            # cv2.line(frame, (int(rect[0]), int(rect[1])), (t0, t1), (255, 255, 255), 3)
            if show:
                cv2.drawContours(frame, [box], 0, (255, 0, 0), 3)
                cv2.line(frame, tuple(box[0]), tuple(box[1]), (255, 128, 128), 3)
        
            rect3 = rect2.astype(int).reshape(-1, 2)
            if show:
                cv2.line(frame, tuple(rect3[0]), tuple(rect3[1]), (0, 0, 255), 2)
                cv2.polylines(frame, [rect3], True, (128, 128, 255), 1)
                cv2.putText(frame, str(track_id), (int(rect[0]), int(rect[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)    
            if rect2[0] == 0 and rect2[1] == 0:
                track1 = add_trajectory(track1, track_id, frame_no, vote, np.zeros((1,8), dtype=np.int32))
            else:
                track1 = add_trajectory(track1, track_id, frame_no, vote, rect3.reshape(1,8))
         
        for track_id, rect, rect2, vote in tracked_objects_2:
            # boxPoints角度定義不同
            # box2 = cv2.boxPoints([(rect[0],rect[1]),(rect[2],rect[3]),180-rect[4]])
            box90 = cv2.boxPoints(((rect[0],rect[1]),(rect[2],rect[3]),-rect[4]))
            # box = np.intp(box2) 
            box = np.intp(box90) 
            # t0 = int(rect[0]+rect[2]/2*math.cos(rect[4] / 180.0 * np.pi))
            # t1 = int(rect[1]-rect[2]/2*math.sin(rect[4] / 180.0 * np.pi))
            # cv2.line(frame, (int(rect[0]), int(rect[1])), (t0, t1), (255, 255, 255), 3)
            if show:
                cv2.drawContours(frame, [box], 0, (255, 0, 0), 3)
                cv2.line(frame, tuple(box[0]), tuple(box[1]), (255, 128, 128), 3)
       
            rect3 = rect2.astype(int).reshape(-1, 2)
            if show:
                cv2.line(frame, tuple(rect3[0]), tuple(rect3[1]), (0, 0, 255), 2)
                cv2.polylines(frame, [rect3], True, (128, 128, 255), 1)
                cv2.putText(frame, str(track_id), (int(rect[0]), int(rect[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

            if rect2[0] == 0 and rect2[1] == 0:
                track2 = add_trajectory(track2, track_id, frame_no, vote, rect3.reshape(1,8))
            else:
                track2 = add_trajectory(track2, track_id, frame_no, vote, rect3.reshape(1,8))
        
        if show:
            # out.write(frame)  
            cv2.imshow('Frame', frame)
            # cv2.imwrite(str(frame_no)+'.jpg', frame)
        
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

    # 開啟文件，並用寫入模式 'w'
    V_type = "pumctbhg" 
    with open(tracking_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        i = 0
        for id, data in track2.items():
            if len(data[11]) > 20:
                traj = interpolate_zeros(data[11])
                writer.writerow([i, data[1], data[1]+len(traj)-1, 'X', 'X', V_type[np.argmax(data[3:11])]] + list(np.array(traj).flatten()))
                i = i+1

        for id, data in track1.items():
            if len(data[11]) > 20:
                traj = interpolate_zeros(data[11])
                writer.writerow([i, data[1], data[1]+len(traj)-1, 'X', 'X', V_type[np.argmax(data[3:11])]] + list(np.array(traj).flatten()))
                i = i+1
    
    if show:
        cap.release()    
        # out.release()
        csvfile.close()
        cv2.destroyAllWindows()

