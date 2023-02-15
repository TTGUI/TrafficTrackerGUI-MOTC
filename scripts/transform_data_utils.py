"""
參考
https://link.zhihu.com/?target=https%3A//github.com/hukaixuan19970627/DOTA_devkit_YOLO
"""

# -*- coding: utf-8 -*-
import sys
import codecs
import numpy as np

import shapely.geometry as shgeo
import os
import re
import math
import shutil
import cv2
import glob
# import polyiou
"""
    some basic functions which are useful for process DOTA data
"""

dota_1_0_classnames = ['plane', 'baseball-diamond', 'bridge', 'ground-track-field', 'small-vehicle', 'large-vehicle', 'ship', 'tennis-court',
               'basketball-court', 'storage-tank',  'soccer-ball-field', 'roundabout', 'harbor', 'swimming-pool', 'helicopter']
dota_1_5_classnames = ['plane', 'baseball-diamond', 'bridge', 'ground-track-field', 'small-vehicle', 'large-vehicle', 'ship', 'tennis-court',
                'basketball-court', 'storage-tank',  'soccer-ball-field', 'roundabout', 'harbor', 'swimming-pool', 'helicopter', 'container-crane']
dota_2_0_classnames = []
vehicle_5cls_classnames = ['sedan', 'truck', 'bus', 'trailer', 'cargo']
vehicle_8cls_classnames = ['sedan', 'truck', 'bus', 'trailer', 'cargo', 'person', 'bike', 'moto']
hrsc2016 = ['ship']

def custombasename(fullname):
    return os.path.basename(os.path.splitext(fullname)[0])

def GetFileFromThisRootDir(dir,ext = None):
  allfiles = []
  needExtFilter = (ext != None)
  for root,dirs,files in os.walk(dir):
    for filespath in files:
      filepath = os.path.join(root, filespath)
      extension = os.path.splitext(filepath)[1][1:]
      if needExtFilter and extension in ext:
        allfiles.append(filepath)
      elif not needExtFilter:
        allfiles.append(filepath)
  return allfiles

def TuplePoly2Poly(poly):
    outpoly = [poly[0][0], poly[0][1],
                       poly[1][0], poly[1][1],
                       poly[2][0], poly[2][1],
                       poly[3][0], poly[3][1]
                       ]
    return outpoly

def parse_dota_poly(filename):
    """
        parse the dota ground truth in the format:
        [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
    """
    objects = []
    #print('filename:', filename)
    f = []
    if (sys.version_info >= (3, 5)):
        fd = open(filename, 'r')
        f = fd
    elif (sys.version_info >= 2.7):
        fd = codecs.open(filename, 'r')
        f = fd
    # count = 0
    while True:
        line = f.readline()
        # count = count + 1
        # if count < 2:
        #     continue
        if line:
            splitlines = line.strip().split(' ')
            object_struct = {}
            ### clear the wrong name after check all the data
            #if (len(splitlines) >= 9) and (splitlines[8] in classname):
            if (len(splitlines) < 9):
                continue
            if (len(splitlines) >= 9):
                    object_struct['name'] = splitlines[8]
            if (len(splitlines) == 9):
                object_struct['difficult'] = '0'
            elif (len(splitlines) >= 10):
                # if splitlines[9] == '1':
                # if (splitlines[9] == 'tr'):
                #     object_struct['difficult'] = '1'
                # else:
                object_struct['difficult'] = splitlines[9]
                # else:
                #     object_struct['difficult'] = 0
            object_struct['poly'] = [(float(splitlines[0]), float(splitlines[1])),
                                     (float(splitlines[2]), float(splitlines[3])),
                                     (float(splitlines[4]), float(splitlines[5])),
                                     (float(splitlines[6]), float(splitlines[7]))
                                     ]
            gtpoly = shgeo.Polygon(object_struct['poly'])
            object_struct['area'] = gtpoly.area
            # poly = list(map(lambda x:np.array(x), object_struct['poly']))
            # object_struct['long-axis'] = max(distance(poly[0], poly[1]), distance(poly[1], poly[2]))
            # object_struct['short-axis'] = min(distance(poly[0], poly[1]), distance(poly[1], poly[2]))
            # if (object_struct['long-axis'] < 15):
            #     object_struct['difficult'] = '1'
            #     global small_count
            #     small_count = small_count + 1
            objects.append(object_struct)
        else:
            break
    return objects


def parse_vehicle8cls_poly(filename):
    """
        parse the dota ground truth in the format:
        [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
    """
    objects = []
    #print('filename:', filename)
    f = []
    if (sys.version_info >= (3, 5)):
        fd = open(filename, 'r')
        f = fd
    elif (sys.version_info >= 2.7):
        fd = codecs.open(filename, 'r')
        f = fd
    # count = 0
    while True:
        line = f.readline()
        # count = count + 1
        # if count < 2:
        #     continue
        if line:
            splitlines = line.strip().split(' ')
            object_struct = {}
            ### clear the wrong name after check all the data
            #if (len(splitlines) >= 9) and (splitlines[8] in classname):
            if len(splitlines) != 14:
                continue

            object_struct['name'] = splitlines[0]
            object_struct['poly'] = [(float(splitlines[5]), float(splitlines[6])),
                                     (float(splitlines[7]), float(splitlines[8])),
                                     (float(splitlines[9]), float(splitlines[10])),
                                     (float(splitlines[11]), float(splitlines[12]))
                                     ]
            gtpoly = shgeo.Polygon(object_struct['poly'])
            object_struct['area'] = gtpoly.area
            # poly = list(map(lambda x:np.array(x), object_struct['poly']))
            # object_struct['long-axis'] = max(distance(poly[0], poly[1]), distance(poly[1], poly[2]))
            # object_struct['short-axis'] = min(distance(poly[0], poly[1]), distance(poly[1], poly[2]))
            # if (object_struct['long-axis'] < 15):
            #     object_struct['difficult'] = '1'
            #     global small_count
            #     small_count = small_count + 1
            objects.append(object_struct)
        else:
            break
    return objects





def parse_longsideformat(filename):  # filename=??.txt
    """
        parse the longsideformat ground truth in the format:
        objects[i] : [classid, x_c, y_c, longside, shortside, theta]
    """
    objects = []
    f = []
    if (sys.version_info >= (3, 5)):
        fd = open(filename, 'r')
        f = fd
    elif (sys.version_info >= 2.7):
        fd = codecs.open(filename, 'r')
        f = fd
    # count = 0
    while True:
        line = f.readline()
        if line:
            splitlines = line.strip().split(' ')
            object_struct = {}
            ### clear the wrong name after check all the data
            #if (len(splitlines) >= 9) and (splitlines[8] in classname):
            if (len(splitlines) < 6) or (len(splitlines) > 6):
                print('labels长度不为6,出现错误,与预定形式不符')
                continue
            object_struct = [int(splitlines[0]), float(splitlines[1]),
                             float(splitlines[2]), float(splitlines[3]),
                             float(splitlines[4]), float(splitlines[5])
                            ]
            objects.append(object_struct)
        else:
            break
    return objects

def parse_dota_poly2(filename):
    """
        parse the dota ground truth in the format:
        [x1, y1, x2, y2, x3, y3, x4, y4]
    """
    objects = parse_dota_poly(filename)
    for obj in objects:
        obj['poly'] = TuplePoly2Poly(obj['poly'])
        obj['poly'] = list(map(int, obj['poly']))
    return objects

def parse_dota_rec(filename):
    """
        parse the dota ground truth in the bounding box format:
        "xmin, ymin, xmax, ymax"
    """
    objects = parse_dota_poly(filename)
    for obj in objects:
        poly = obj['poly']
        bbox = dots4ToRec4(poly)
        obj['bndbox'] = bbox
    return objects
## bounding box transfer for varies format

def dots4ToRec4(poly):
    """
    求出poly四点的最小外接水平矩形
    @param poly: poly[4]  [x,y]
    @return: xmin,xmax,ymin,ymax
    """
    xmin, xmax, ymin, ymax = min(poly[0][0], min(poly[1][0], min(poly[2][0], poly[3][0]))), \
                            max(poly[0][0], max(poly[1][0], max(poly[2][0], poly[3][0]))), \
                             min(poly[0][1], min(poly[1][1], min(poly[2][1], poly[3][1]))), \
                             max(poly[0][1], max(poly[1][1], max(poly[2][1], poly[3][1])))
    return xmin, ymin, xmax, ymax
def dots4ToRec8(poly):
    xmin, ymin, xmax, ymax = dots4ToRec4(poly)
    return xmin, ymin, xmax, ymin, xmax, ymax, xmin, ymax
    #return dots2ToRec8(dots4ToRec4(poly))
def dots2ToRec8(rec):
    xmin, ymin, xmax, ymax = rec[0], rec[1], rec[2], rec[3]
    return xmin, ymin, xmax, ymin, xmax, ymax, xmin, ymax

def groundtruth2Task1(srcpath, dstpath):
    filelist = GetFileFromThisRootDir(srcpath)
    # names = [custombasename(x.strip())for x in filelist]
    filedict = {}
    for cls in wordname_15:
        fd = open(os.path.join(dstpath, 'Task1_') + cls + r'.txt', 'w')
        filedict[cls] = fd
    for filepath in filelist:
        objects = parse_dota_poly2(filepath)

        subname = custombasename(filepath)
        pattern2 = re.compile(r'__([\d+\.]+)__\d+___')
        rate = re.findall(pattern2, subname)[0]

        for obj in objects:
            category = obj['name']
            difficult = obj['difficult']
            poly = obj['poly']
            if difficult == '2':
                continue
            if rate == '0.5':
                outline = custombasename(filepath) + ' ' + '1' + ' ' + ' '.join(map(str, poly))
            elif rate == '1':
                outline = custombasename(filepath) + ' ' + '0.8' + ' ' + ' '.join(map(str, poly))
            elif rate == '2':
                outline = custombasename(filepath) + ' ' + '0.6' + ' ' + ' '.join(map(str, poly))

            filedict[category].write(outline + '\n')

def Task2groundtruth_poly(srcpath, dstpath):
    thresh = 0.1
    filedict = {}
    Tasklist = GetFileFromThisRootDir(srcpath, '.txt')

    for Taskfile in Tasklist:
        idname = custombasename(Taskfile).split('_')[-1]
        # idname = datamap_inverse[idname]
        f = open(Taskfile, 'r')
        lines = f.readlines()
        for line in lines:
            if len(line) == 0:
                continue
            # print('line:', line)
            splitline = line.strip().split(' ')
            filename = splitline[0]
            confidence = splitline[1]
            bbox = splitline[2:]
            if float(confidence) > thresh:
                if filename not in filedict:
                    # filedict[filename] = codecs.open(os.path.join(dstpath, filename + '.txt'), 'w', 'utf_16')
                    filedict[filename] = codecs.open(os.path.join(dstpath, filename + '.txt'), 'w')
                # poly = util.dots2ToRec8(bbox)
                poly = bbox
                #               filedict[filename].write(' '.join(poly) + ' ' + idname + '_' + str(round(float(confidence), 2)) + '\n')
            # print('idname:', idname)

            # filedict[filename].write(' '.join(poly) + ' ' + idname + '_' + str(round(float(confidence), 2)) + '\n')

                filedict[filename].write(' '.join(poly) + ' ' + idname + '\n')


def polygonToRotRectangle(bbox):
    """
    :param bbox: The polygon stored in format [x1, y1, x2, y2, x3, y3, x4, y4]
    :return: Rotated Rectangle in format [cx, cy, w, h, theta]
    """
    bbox = np.array(bbox,dtype=np.float32)
    bbox = np.reshape(bbox,newshape=(2,4),order='F')
    angle = math.atan2(-(bbox[0,1]-bbox[0,0]),bbox[1,1]-bbox[1,0])

    center = [[0],[0]]

    for i in range(4):
        center[0] += bbox[0,i]
        center[1] += bbox[1,i]

    center = np.array(center,dtype=np.float32)/4.0

    R = np.array([[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]], dtype=np.float32)

    normalized = np.matmul(R.transpose(),bbox-center)

    xmin = np.min(normalized[0,:])
    xmax = np.max(normalized[0,:])
    ymin = np.min(normalized[1,:])
    ymax = np.max(normalized[1,:])

    w = xmax - xmin + 1
    h = ymax - ymin + 1

    return [float(center[0]),float(center[1]),w,h,angle]

def cal_line_length(point1, point2):
    return math.sqrt( math.pow(point1[0] - point2[0], 2) + math.pow(point1[1] - point2[1], 2))

def get_best_begin_point(coordinate):
    x1 = coordinate[0][0]
    y1 = coordinate[0][1]
    x2 = coordinate[1][0]
    y2 = coordinate[1][1]
    x3 = coordinate[2][0]
    y3 = coordinate[2][1]
    x4 = coordinate[3][0]
    y4 = coordinate[3][1]
    xmin = min(x1, x2, x3, x4)
    ymin = min(y1, y2, y3, y4)
    xmax = max(x1, x2, x3, x4)
    ymax = max(y1, y2, y3, y4)
    combinate = [[[x1, y1], [x2, y2], [x3, y3], [x4, y4]], [[x2, y2], [x3, y3], [x4, y4], [x1, y1]],
                 [[x3, y3], [x4, y4], [x1, y1], [x2, y2]], [[x4, y4], [x1, y1], [x2, y2], [x3, y3]]]
    dst_coordinate = [[xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax]]
    force = 100000000.0
    force_flag = 0
    for i in range(4):
        temp_force = cal_line_length(combinate[i][0], dst_coordinate[0]) + cal_line_length(combinate[i][1],
                                                                                           dst_coordinate[
                                                                                               1]) + cal_line_length(
            combinate[i][2], dst_coordinate[2]) + cal_line_length(combinate[i][3], dst_coordinate[3])
        if temp_force < force:
            force = temp_force
            force_flag = i
    if force_flag != 0:
        print("choose one direction!")
    return  combinate[force_flag]


def dots4ToRecC(poly, img_w, img_h):
    """
    求poly四点坐标的最小外接水平矩形,并返回yolo格式的矩形框表现形式xywh_center(归一化)
    @param poly: poly – poly[4] [x,y]
    @param img_w: 对应图像的width
    @param img_h: 对应图像的height
    @return: x_center,y_center,w,h(均归一化)
    """
    xmin, ymin, xmax, ymax = dots4ToRec4(poly)
    x = (xmin + xmax)/2
    y = (ymin + ymax)/2
    w = xmax - xmin
    h = ymax - ymin
    return x/img_w, y/img_h, w/img_w, h/img_h


def cvminAreaRectPostProcess(x_c, y_c, width, height, theta):
    """
    貌似OpenCV4.1.2.30這個版本的minAreaRect有一些bug，所以做一些後處理
    
    Input   (directly catch the output of cv2.minAreaRect())
        ((rect_cx, rect_cy), (rect_w, rect_h), theta)
        definition of width and height can be found in OpenCV doc
        theta should be in the range [-90,0)

    Output
        


    """






    '''
    trans minAreaRect(x_c, y_c, width, height, θ) to longside format(x_c, y_c, longside, shortside, θ)
    两者区别为:
            当opencv表示法中width为最长边时（包括正方形的情况），则两种表示方法一致
            当opencv表示法中width不为最长边 ，则最长边表示法的角度要在opencv的Θ基础上-90度         
    @param x_c: center_x
    @param y_c: center_y
    @param width: x轴逆时针旋转碰到的第一条边
    @param height: 与width不同的边
    @param theta: x轴逆时针旋转与width的夹角，由于原点位于图像的左上角，逆时针旋转角度为负 [-90, 0)
    @return: 
            x_c: center_x
            y_c: center_y
            longside: 最长边
            shortside: 最短边
            theta_longside: 最长边和x轴逆时针旋转的夹角，逆时针方向角度为负 [-180, 0)
    '''
    '''
    意外情况:(此时要将它们恢复符合规则的opencv形式：wh交换，Θ置为-90)
    竖直box：box_width < box_height  θ=0
    水平box：box_width > box_height  θ=0
    '''

    

    if theta == 0:
        theta = -90
        buffer_width = width
        width = height
        height = buffer_width

    if theta > 0:
        if theta != 90:  # Θ=90说明wh中有为0的元素，即gt信息不完整，无需提示异常，直接删除
            print('θ计算出现异常，当前数据为：%.16f, %.16f, %.16f, %.16f, %.1f;超出opencv表示法的范围：[-90,0)' % (x_c, y_c, width, height, theta))
        return False

    if theta < -90:
        print('θ计算出现异常，当前数据为：%.16f, %.16f, %.16f, %.16f, %.1f;超出opencv表示法的范围：[-90,0)' % (x_c, y_c, width, height, theta))
        return False

    if width != max(width, height):  # 若width不是最长边
        longside = height
        shortside = width
        theta_longside = theta - 90
    else:  # 若width是最长边(包括正方形的情况)
        longside = width
        shortside = height
        theta_longside = theta

    if longside < shortside:
        print('旋转框转换表示形式后出现问题：最长边小于短边;[%.16f, %.16f, %.16f, %.16f, %.1f]' % (x_c, y_c, longside, shortside, theta_longside))
        return False
    if (theta_longside < -180 or theta_longside >= 0):
        print('旋转框转换表示形式时出现问题:θ超出长边表示法的范围：[-180,0);[%.16f, %.16f, %.16f, %.16f, %.1f]' % (x_c, y_c, longside, shortside, theta_longside))
        return False

    return x_c, y_c, longside, shortside, theta_longside


def check_rbbox_valid(xywhtheta, imgw, imgh):
    """
    確認旋轉框的值是否合法
    貌似OpenCV4.1.2.30這個版本的minAreaRect有一些bug，所以做一些後處理
    
    Input   (directly catch the output of cv2.minAreaRect())
        ((rect_cx, rect_cy), (rect_w, rect_h), theta)
        definition of width and height can be found in OpenCV doc
        theta should be in the range [-90,0)

    Output
        if rotate bounding box is valid
            return true
        otherwise return false
        
    """

    cx,cy,w,h,theta = *xywhtheta[0],*xywhtheta[1],xywhtheta[2]
    
    if cx < 0 or cx >= imgw or cy < 0 or cy >= imgh:
        #TODO: log
        print('旋轉框中心點超出影像，目前數據為：{:.16f}, {:.16f}, {:.16f}, {:.16f}, {:.16f}'.format(cx,cy,w,h,theta))
        return False

    if w <= 0 or h <= 0:
        #TODO: log
        print('旋轉框轉換表示形式出現問題：邊長小於等於0;[{:.16f}, {:.16f}, {:.16f}, {:.16f}, {:.16f}]'.format(cx,cy,w,h,theta))
        return False

    #不用檢查角度是否介於[-90,0)後面不會用到
    # if theta < -90 or 0 < theta:
    #     #TODO: log
    #     print('旋轉框 θ計算出現異常，目前數據為：{:.16f}, {:.16f}, {:.16f}, {:.16f}, {:.16f} ;超出OpenCV表示法範圍[-90,0)'.format(cx,cy,w,h,theta))
    #     return False
    # if theta == 0:
    #     # 目前沒用到只是先做修正
    #     theta = -90
    #     buffer_width = w
    #     w = h
    #     h = buffer_width

    return True



def cvt_back_xywhtheta(rbox_pts, quad_pts):
    """
    quad_pts: ground truth pts
    rbox_pts: 擬合外接矩形四個點
    Point in quad_pts is ordered in clockwise, index 0 is first point
    Point in rbox_pts is ordered in clockwise, but we don't know the first point

    rbox_pts shape (4,2)
    quad_pts shape (4,2)

    return np.array([cx,cy,w,h,theta,hx,hy])
    """
    # print('quad_pts', quad_pts)
    # Repeat first point for calculating distance with rbox four points
    quad_p1 = quad_pts[0].reshape(1,-1).repeat(4, axis=0)
    # 找quad_pts的第一個點與rbox_pts哪個點距離最小 視為rbox_pts的第一個點
    first_p_idx = np.argmin(np.sum(np.power((quad_p1-rbox_pts),2), axis=1))
    # 因為點都已經順時針排序，所以只要rolling rbox_pts內的點到正確順序即可
    ordered_rbox_pts = np.roll(rbox_pts, -first_p_idx, axis=0)
    # print('ordered_rbox_pts', ordered_rbox_pts)

    ordered_rbox_pts = ordered_rbox_pts.astype(np.float64)

    cx, cy = (ordered_rbox_pts[0]+ordered_rbox_pts[2])/2
    head_cx, head_cy = (ordered_rbox_pts[0]+ordered_rbox_pts[1])/2
    dx, dy = head_cx-cx, head_cy-cy
    angle = np.arctan2(-dy, dx)   # (-π,π]
    angle = angle+2*math.pi if angle < 0 else angle  # [0,2π)
    if angle == 2*math.pi: angle = 0  # 確保只有0-359度
    w = sum((ordered_rbox_pts[0]-ordered_rbox_pts[1])**2)**0.5
    h = sum((ordered_rbox_pts[1]-ordered_rbox_pts[2])**2)**0.5

    return ordered_rbox_pts, np.array((cx, cy, w, h, angle, head_cx, head_cy))
    # return ordered_rbox_pts, angle


def draw_rlabels_to_check(img_dir_path, label_dir_path, output_img_dir_path, classnames_txt_path):
    """
    img_dir_path
    label_dir_path
    output_img_dir_path
    classnames_txt_path
    """
    # if outputs_dir exists, delete it and remake directory.
    if os.path.exists(output_img_dir_path):
        shutil.rmtree(output_img_dir_path)  # delete output folder

    os.makedirs(output_img_dir_path)  # make new output folder

    imgs_path_list_pkg = [[f, os.path.splitext(os.path.basename(f))[0]] for f_ in [glob.glob(img_dir_path+os.sep+'*'+e) for e in ['.png', '.jpg', '.bmp'] ] for f in f_ ]
    imgs_path_list, imgs_basename_list = zip(*imgs_path_list_pkg)
    
    for img_idx, img_path in enumerate(imgs_path_list):
        if os.name == 'nt':
            img = cv2.imdecode(np.fromfile(img_path,dtype=np.uint8),-1)
            img = cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
        else:
            img = cv2.imread(img_path)
        imgh, imgw = img.shape[:2]
        label_path = label_dir_path + os.sep + imgs_basename_list[img_idx] + '.txt'

        with open(label_path, 'r', encoding='utf-8') as infile:
            line_list = infile.readlines()

            for line in line_list:  # every rbox
                token = line.strip().split(' ')
                result = [int(t) if idx==0 else float(t) for idx, t in enumerate(token)]
                cls_id,x,y,w,h,theta = result
                rbox = np.array([[x,y,w,h,theta]])
                rbox[:,[0,2]] *= imgw
                rbox[:,[1,3]] *= imgh

                rbox4pts = xywhtheta24xy_new(rbox).squeeze()
                draw_one_polygon(img, rbox4pts.reshape(4,2), which_cls=cls_id)

        if os.name == 'nt':
            cv2.imencode(ext='.jpg',img=img)[1].tofile(output_img_dir_path+os.sep+os.path.basename(img_path))
        else:
            cv2.imwrite(output_img_dir_path+os.sep+os.path.basename(img_path), img)

        # cv2.namedWindow('img', flags=cv2.WINDOW_AUTOSIZE | cv2.WINDOW_GUI_NORMAL)
        # cv2.imshow('img', img)
        # cv2.waitKey(0)

def draw_one_polygon(img, pts, which_cls=0):
    """
    draw one polygon on image, head line is white
    image will be modified becuase of reference calling
    you can receive return image if necessary

    Input:
        img: opencv format image
        which_cls: int value
        pts = shape [4(four vertices),2(x,y)]
        *pts: (x1,y1,x2,y2,x3,y3,x4,y4)

    Output:
        img: opencv format image
    """
    # int_pts = [int(p) for p in pts]
    # p1, p2, p3, p4 = (int_pts[0], int_pts[1]), (int_pts[2], int_pts[3]), \
    #                 (int_pts[4], int_pts[5]), (int_pts[6], int_pts[7])

    p1, p2, p3, p4 = tuple(map(tuple,pts.astype(np.int32)))

    # 可以增加 e.g.,[0,0.3,0.5,0.7]  [1,0.7,0.5,0.3]
    bgr_weight_list = [0,0.5,0.7]
    bgr_weight_list2 = [1,0.7,0.5]

    # 不可變
    bgr_bit_list = [[0,0,1],[0,1,1],[0,1,0],[1,1,0],[1,0,0],[1,0,1]]

    total_num_colors = len(bgr_bit_list)*len(bgr_weight_list)

    # 可以增加 e.g.,[255,245,235,225,215]
    start_bgr_list = [250, 200, 150]
    start_bgr_idx = (which_cls // total_num_colors) % len(start_bgr_list)

    which_cls = which_cls - total_num_colors * (which_cls//total_num_colors)
    which_color = which_cls % len(bgr_bit_list)

    if sum(bgr_bit_list[which_color]) == 1:
        bgr_bit_is_one_idx = bgr_bit_list[which_color].index(1)
        pre_bgr_bit_idx = bgr_bit_is_one_idx-1
        bgr_color_bit = bgr_bit_list[which_color]
        which_weight = (which_cls//len(bgr_bit_list)) % len(bgr_weight_list)

        if which_cls % total_num_colors >= len(bgr_bit_list):
            bgr_color_bit[pre_bgr_bit_idx] = bgr_weight_list[int(which_weight)]
    elif sum(bgr_bit_list[which_color]) == 2:
        bgr_color_bit = bgr_bit_list[which_color]
        if bgr_color_bit == [0,1,1]: pos_bgr_bit_idx = 2
        elif bgr_color_bit == [1,1,0]: pos_bgr_bit_idx = 1
        elif bgr_color_bit == [1,0,1]: pos_bgr_bit_idx = 0

        which_weight = (which_cls//len(bgr_bit_list)) % len(bgr_weight_list2)

        if which_cls % total_num_colors >= len(bgr_bit_list):
            bgr_color_bit[pos_bgr_bit_idx] *= bgr_weight_list2[int(which_weight)]

    body_line_color = [int(bgr_color*start_bgr_list[start_bgr_idx]) for bgr_color in bgr_color_bit]

    head_line_color = (255,255,255)

    cv2.line(img, p1, p2, head_line_color, 2, lineType=cv2.LINE_AA)
    cv2.line(img, p2, p3, body_line_color, 2, lineType=cv2.LINE_AA)
    cv2.line(img, p3, p4, body_line_color, 2, lineType=cv2.LINE_AA)
    cv2.line(img, p4, p1, body_line_color, 2, lineType=cv2.LINE_AA)

    return img




def xywhtheta24xy_new(x):
    """
    numpy ndarray
    dtype float32
    shape (n,5)  n rboxes 5:x, y, w, h, theta
    return (n,8) x1,y1,x2,y2,x3,y3,x4,y4
    """

    # print('x', x)
    
    # x[:,4] = np.where(x[:,4] > math.pi, 2*math.pi-x[:,4], x[:,4])
    # hcx = np.cos(x[:,4])*(x[:,3]/2)+x[:,0]

    # a_part = np.sqrt((x[:,3]/2)**2-(hcx-x[:,0])**2)
    # b_part = x[:,1]

    # hcy = np.where(a_part+b_part >= 0, a_part+b_part, b_part-a_part)
    
    # 中心點到任一角點的距離，因為是矩形到四個角點距離相等
    r = (x[:,2]**2+x[:,3]**2)**0.5/2
    # print('r', r)
    # 中心點到第一點的向量與中心點到頭中點的向量角度會小於90度所以不用再判斷值是否小於0
    diff_radian = np.arctan2((x[:,2]/2),(x[:,3]/2))
    # print('diff_radian', diff_radian)
    # 先將矩形平躺到x軸上0度位置，找出四個角點
    p1x, p1y = r*np.cos(diff_radian)+x[:,0], -r*np.sin(diff_radian)+x[:,1]
    p2x, p2y = r*np.cos(diff_radian)+x[:,0], r*np.sin(diff_radian)+x[:,1]
    p3x, p3y = -r*np.cos(diff_radian)+x[:,0], r*np.sin(diff_radian)+x[:,1]
    p4x, p4y = -r*np.cos(diff_radian)+x[:,0], -r*np.sin(diff_radian)+x[:,1]
    # print('p1x', p1x)
    # print('p1x dtype', p1x.dtype)
    # 三角函數是在平面直角座標系上計算角度為逆時針，但直接將角度放在影像座標系時，
    # 因為y軸相反所以會變成順時針，為了使旋轉角正確用2pi減掉原本角度
    r_angle = 2*math.pi-x[:,4]

    #TODO 將公式改為矩陣運算
    # 透過旋轉公式將平躺的矩形旋轉到原來位置，以求得新的四個角點
    x1 = (p1x-x[:,0])*np.cos(r_angle) - (p1y-x[:,1])*np.sin(r_angle) + x[:,0]
    y1 = (p1x-x[:,0])*np.sin(r_angle) + (p1y-x[:,1])*np.cos(r_angle) + x[:,1]
    x2 = (p2x-x[:,0])*np.cos(r_angle) - (p2y-x[:,1])*np.sin(r_angle) + x[:,0]
    y2 = (p2x-x[:,0])*np.sin(r_angle) + (p2y-x[:,1])*np.cos(r_angle) + x[:,1]
    x3 = (p3x-x[:,0])*np.cos(r_angle) - (p3y-x[:,1])*np.sin(r_angle) + x[:,0]
    y3 = (p3x-x[:,0])*np.sin(r_angle) + (p3y-x[:,1])*np.cos(r_angle) + x[:,1]
    x4 = (p4x-x[:,0])*np.cos(r_angle) - (p4y-x[:,1])*np.sin(r_angle) + x[:,0]
    y4 = (p4x-x[:,0])*np.sin(r_angle) + (p4y-x[:,1])*np.cos(r_angle) + x[:,1]

    # print('r_angle', r_angle[0])
    # for x11,y11,x22,y22,x33,y33,x44,y44, degree in zip(x1,y1,x2,y2,x3,y3,x4,y4, r_angle):
    #     print('degree', degree*180/math.pi)
    #     cv2.line(img, (x11,y11), (x22,y22), (0,0,255), thickness=2, lineType=cv2.LINE_AA)
    #     cv2.line(img, (x22,y22), (x33,y33), (0,255,0), thickness=2, lineType=cv2.LINE_AA)
    #     cv2.imshow('123', img)
    #     cv2.waitKey(0)

    # First point
    # x1 = r*np.cos(x[:,4]+diff_radian)+x[:,0]
    # y1 = -(r*np.sin(x[:,4]+diff_radian))+x[:,1]

    # # Second point
    # x2 = r*np.cos(x[:,4]-diff_radian)+x[:,0]
    # y2 = -(r*np.sin(x[:,4]-diff_radian))+x[:,1]

    # # Third point
    # x3 = -r*np.cos(x[:,4]+diff_radian)+x[:,0]
    # y3 = r*np.sin(x[:,4]+diff_radian)+x[:,1]

    # # Fourth point
    # x4 = -r*np.cos(x[:,4]-diff_radian)+x[:,0]
    # y4 = r*np.sin(x[:,4]-diff_radian)+x[:,1]

    return np.stack((x1,y1,x2,y2,x3,y3,x4,y4), axis=0).T