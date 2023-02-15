"""
參考(https://link.zhihu.com/?target=https%3A//github.com/hukaixuan19970627/DOTA_devkit_YOLO)


將各種dataset的label格式轉成YOLO旋轉框格式，標注資料必須明確標示出輪廓點順序

如果旋轉框有超出影像的部份不做處理直接超出去跟(https://github.com/hukaixuan19970627/YOLOv5_DOTA_OBB)處理方式一樣

"""


#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import shutil
import cv2
import glob
import transform_data_utils
import numpy as np
import math
import argparse

class Transform_data_to_yolo_format_obb:
    def __init__(self, images_dir_path, labels_dir_path, output_labels_dir_path, classnames_txt_path='', dataset='', output_label_format='xywhtheta', with_difficulty=False):
        """
        images_dir_path: 圖片的資料夾路徑
        labels_dir_path: 標注的資料夾路徑
        output_labels_dir_path: 轉換後存結果的資料夾路徑
        classnames_txt_path: 物體類別的txt檔(classnames_txt_path和dataset二選一即可，如果同時使用以classnames_txt_path優先)
        dataset: 數據集選擇

        if output_labels_dir_path exists, it will be deleted and remake directory.
        """
        self.imgs_dir_path = images_dir_path
        self.labels_dir_path = labels_dir_path
        self.output_labels_dir_path = output_labels_dir_path
        self.classnames_txt_path = classnames_txt_path
        self.dataset = dataset
        self.classnames_list = []
        self.imgs_path_list = []
        self.imgs_basename_list = []
        self.labels_path_list = []
        self.output_label_format = output_label_format
        self.with_difficulty = with_difficulty

        # Get classes name
        if classnames_txt_path is not '':
            with open(self.classnames_txt_path, 'r', encoding='utf-8') as infile:
                lines = infile.readlines()
                self.classnames_list = [line.strip() for line in lines if len(line.strip()) > 0]
        else:
            self.classnames_list = self.choose_dataset()

        # if outputs_dir exists, delete it and remake directory.
        if os.path.exists(self.output_labels_dir_path):
            shutil.rmtree(self.output_labels_dir_path)  # delete output folder

        os.makedirs(self.output_labels_dir_path)  # make new output folder

        # get all specified extension images path and basename without extension from image directory
        imgs_path_list_pkg = [[f, os.path.splitext(os.path.basename(f))[0]] for f_ in [glob.glob(self.imgs_dir_path+os.sep+'*'+e) for e in ['.png', '.jpg', '.bmp'] ] for f in f_ ]
        self.imgs_path_list, self.imgs_basename_list = zip(*imgs_path_list_pkg)

        # get all specified extension labels path from label directory
        self.labels_path_list = [f for f_ in [glob.glob(self.labels_dir_path+os.sep+'*'+e) for e in ['.txt'] ] for f in f_ ]

    def choose_dataset(self):
        if self.dataset == 'dota1.0':
            self.classnames_list = transform_data_utils.dota_1_0_classnames
        elif self.dataset == 'dota1.5':
            self.classnames_list = transform_data_utils.dota_1_5_classnames
        elif self.dataset == 'dota2.0':
            self.classnames_list = transform_data_utils.dota_2_0_classnames
        elif self.dataset == 'vehicle5cls':
            self.classnames_list = transform_data_utils.vehicle_5cls_classnames
        elif self.dataset == 'vehicle8cls':
            self.classnames_list = transform_data_utils.vehicle_8cls_classnames
        elif self.dataset == 'HRSC2016':
            pass
        else:
            #TODO: log
            print('The dataset is not supported yet. Please use \"classnames_txt_path\" to set your classes name file!!\n')
            exit(0)

    def draw_one_polygon(self, img, pts, which_cls=0):
        """
        draw one polygon on image, head line is white
        image will be modified becuase of reference calling
        you can receive return image if necessary

        Input:
            img: opencv format image
            which_cls: int value
            *pts: (x1,y1,x2,y2,x3,y3,x4,y4)

        Output:
            img: opencv format image
        """
        # int_pts = [int(p) for p in pts]
        # p1, p2, p3, p4 = (int_pts[0], int_pts[1]), (int_pts[2], int_pts[3]), \
        #                 (int_pts[4], int_pts[5]), (int_pts[6], int_pts[7])

        p1, p2, p3, p4 = tuple(map(tuple,pts.astype(np.int)))

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

 
class Transform_dota_to_yolo_obb(Transform_data_to_yolo_format_obb):
    """
    before use it, split dota image first
    """
    def __init__(self, images_dir_path, labels_dir_path, output_labels_dir_path, classnames_txt_path='', dataset='', output_label_format='xywhtheta', with_difficulty=False):
        super().__init__(images_dir_path, labels_dir_path, output_labels_dir_path, classnames_txt_path, dataset, output_label_format, with_difficulty)

        self.convert_label_format()
        # self.draw_labels()


    def convert_label_format(self):

        for img_idx, img_path in enumerate(self.imgs_path_list):
            label_path = self.labels_dir_path + os.sep + self.imgs_basename_list[img_idx] + '.txt'

            if not os.path.exists(label_path):
                # TODO: out log
                print('No corresponding labels! {}'.format(img_path))
                continue

            objects = transform_data_utils.parse_dota_poly(label_path)
            # print('objects', objects)
            '''
            objects =
            [{'name': 'ship', 
            'difficult': '1', 
            'poly': [(1054.0, 1028.0), (1063.0, 1011.0), (1111.0, 1040.0), (1112.0, 1062.0)], 
            'area': 1159.5
            },
            ...
            ]
            '''
            if os.name == 'nt':
                img = cv2.imdecode(np.fromfile(img_path,dtype=np.uint8),-1)
                img = cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
            else:
                img = cv2.imread(img_path)
            imgh, imgw = img.shape[:2]

            # Put image name on the image
            cv2.putText(img, os.path.basename(img_path), (10, 30), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(125, 50, 200), thickness=2, lineType=cv2.LINE_AA)

            img_rz = img.copy()
            # img_resize = cv2.resize(img_rz, (0,0), fx=1, fy=2)
            dst_path = self.output_labels_dir_path + os.sep + self.imgs_basename_list[img_idx] + '.txt'

            with open(dst_path, 'w', encoding='utf-8') as outf:
                for obj_id, obj in enumerate(objects):
                    poly = obj['poly'] # poly=[(x1,y1),(x2,y2),(x3,y3),(x4,y4)] to np.array([])
                    poly = np.float32(np.array(poly))
                    # print('original poly ', poly)

                    # check to output difficult label or not
                    if not self.with_difficulty:
                        continue

                    # 找class id
                    if obj['name'] in self.classnames_list:
                        cls_id = self.classnames_list.index(obj['name'])
                    else:
                        #TODO: log
                        print('物體類別不在預定類別中: {};已經排除該label,問題出現在: {}'.format(obj['name'], img_path))
                        continue
                    
                    # 目前不對角點做normalize，直接算minAreaRect準度才不會跑掉太多
                    rbox_xywhtheta = cv2.minAreaRect(poly)  # 得到最小外接矩形  (中心(x,y),(寬,高),旋轉角度)  旋轉角度[-90,0)可能有special case
                    # print('rbox_xywhtheta', rbox_xywhtheta)

                    # 原始dota內的多邊形label經過minAreaRect的處理後，出現錯誤直接排除該物體label
                    if not transform_data_utils.check_rbbox_valid(rbox_xywhtheta, imgw, imgh):
                        #TODO: log fullpath
                        continue                  

                    # 用cv2.boxPoints得到的角點，透過頭的中心點跟物體中心點，重新計算回角度時會跟cv2.minAreaRect所得到的角度有些微誤差
                    # 不過因為是ground truth的處理，dota dataset本身並沒有給原始角度，只要角度跟四個角點同時求得即可
                    # 所以中心點、長、寬、角度資訊採用cv2.boxPoints回推出來的結果
                    rbox4pts = cv2.boxPoints(rbox_xywhtheta)

                    # 利用cv2.boxPoints所求出的四個角點重新回推(x,y,width,height,theta,head_cx,head_cy)
                    # 順便回傳四個角點(第一點及順時針排序)
                    ordered_rbox_pts, rbox_xywhthetahxhy = transform_data_utils.cvt_back_xywhtheta(rbox4pts, poly)

                    # Draw rbox to check
                    self.draw_one_polygon(img, ordered_rbox_pts, cls_id)

                    # Normalize cx and width with image width, cy and height with image height
                    rbox_xywhthetahxhy[[0,2,5]]/=imgw
                    rbox_xywhthetahxhy[[1,3,6]]/=imgh
                    
                    rbox_xywhthetahxhy[2] = 1 if rbox_xywhthetahxhy[2] > 1 else rbox_xywhthetahxhy[2]
                    rbox_xywhthetahxhy[3] = 1 if rbox_xywhthetahxhy[3] > 1 else rbox_xywhthetahxhy[3]

                    # 移除中心點超出影像的label
                    if rbox_xywhthetahxhy[0] < 0 or rbox_xywhthetahxhy[0] > 1 or rbox_xywhthetahxhy[1] < 0 or rbox_xywhthetahxhy[1] > 1:
                        continue

                    out_line_str = str(cls_id) + ' ' + ' '.join(list(map(str, rbox_xywhthetahxhy[:5]))) + '\n'
                    # print('out_line_str', out_line_str)

                    outf.write(out_line_str)
 

            # cv2.namedWindow('img', flags=cv2.WINDOW_AUTOSIZE | cv2.WINDOW_GUI_NORMAL)
            # cv2.imshow('img', img)
            # cv2.waitKey(0)


class Transform_vehicle8cls_to_yolo_obb(Transform_data_to_yolo_format_obb):
    """
    before use it, split dota image first
    """
    def __init__(self, images_dir_path, labels_dir_path, output_labels_dir_path, classnames_txt_path='', dataset='', output_label_format='xywhtheta'):
        super().__init__(images_dir_path, labels_dir_path, output_labels_dir_path, classnames_txt_path, dataset, output_label_format)

        self.convert_label_format()
        # self.draw_labels()


    def convert_label_format(self):

        for img_idx, img_path in enumerate(self.imgs_path_list):
            label_path = self.labels_dir_path + os.sep + self.imgs_basename_list[img_idx] + '.txt'
            print(label_path)

            if not os.path.exists(label_path):
                # TODO: out log
                print('No corresponding labels! {}'.format(img_path))
                continue

            objects = transform_data_utils.parse_vehicle8cls_poly(label_path)
            # print('objects', objects)
            '''
            objects =
            [{'name': 'ship', 
            'difficult': '1', 
            'poly': [(1054.0, 1028.0), (1063.0, 1011.0), (1111.0, 1040.0), (1112.0, 1062.0)], 
            'area': 1159.5
            },
            ...
            ]
            '''
            if os.name == 'nt':
                img = cv2.imdecode(np.fromfile(img_path,dtype=np.uint8),-1)
                img = cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
            else:
                img = cv2.imread(img_path)
            imgh, imgw = img.shape[:2]

            # Put image name on the image
            cv2.putText(img, os.path.basename(img_path), (10, 30), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(125, 50, 200), thickness=2, lineType=cv2.LINE_AA)

            img_rz = img.copy()
            # img_resize = cv2.resize(img_rz, (0,0), fx=1, fy=2)
            dst_path = self.output_labels_dir_path + os.sep + self.imgs_basename_list[img_idx] + '.txt'

            with open(dst_path, 'w', encoding='utf-8') as outf:
                for obj_id, obj in enumerate(objects):
                    poly = obj['poly'] # poly=[(x1,y1),(x2,y2),(x3,y3),(x4,y4)] to np.array([])
                    poly = np.float32(np.array(poly))
                    cls_id = int(obj['name'])
                    # print('original poly ', poly)

                    # 找class id
                    if int(obj['name']) >= len(self.classnames_list):
                        #TODO: log
                        print('物體類別不在預定類別中: {};已經排除該label,問題出現在: {}'.format(obj['name'], img_path))
                        continue
                    
                    # 目前不對角點做normalize，直接算minAreaRect準度才不會跑掉太多
                    rbox_xywhtheta = cv2.minAreaRect(poly)  # 得到最小外接矩形  (中心(x,y),(寬,高),旋轉角度)  旋轉角度[-90,0)可能有special case
                    # print('rbox_xywhtheta', rbox_xywhtheta)

                    # 原始dota內的多邊形label經過minAreaRect的處理後，出現錯誤直接排除該物體label
                    if not transform_data_utils.check_rbbox_valid(rbox_xywhtheta, imgw, imgh):
                        #TODO: log fullpath
                        # cv2.circle(img, (int(rbox_xywhtheta[0][0]),int(rbox_xywhtheta[0][1])), 3, (0,0,255),-1,cv2.LINE_AA)
                        # cv2.imshow('check img and label', img)
                        # cv2.waitKey(0)
                        # input('pause')
                        print('出現錯誤值: {};已經排除該label,問題出現在: {}'.format(obj['name'], img_path))
                        continue                  

                    # 用cv2.boxPoints得到的角點，透過頭的中心點跟物體中心點，重新計算回角度時會跟cv2.minAreaRect所得到的角度有些微誤差
                    # 不過因為是ground truth的處理，dota dataset本身並沒有給原始角度，只要角度跟四個角點同時求得即可
                    # 所以中心點、長、寬、角度資訊採用cv2.boxPoints回推出來的結果
                    rbox4pts = cv2.boxPoints(rbox_xywhtheta)

                    # 利用cv2.boxPoints所求出的四個角點重新回推(x,y,width,height,theta,head_cx,head_cy)
                    # 順便回傳四個角點(第一點及順時針排序)
                    ordered_rbox_pts, rbox_xywhthetahxhy = transform_data_utils.cvt_back_xywhtheta(rbox4pts, poly)

                    # Draw rbox to check
                    self.draw_one_polygon(img, ordered_rbox_pts, cls_id)

                    # Normalize cx, width and head x with image width, cy, height and head y with image height
                    rbox_xywhthetahxhy[[0,2,5]]/=imgw
                    rbox_xywhthetahxhy[[1,3,6]]/=imgh

                    rbox_xywhthetahxhy[2] = 1 if rbox_xywhthetahxhy[2] > 1 else rbox_xywhthetahxhy[2]
                    rbox_xywhthetahxhy[3] = 1 if rbox_xywhthetahxhy[3] > 1 else rbox_xywhthetahxhy[3]

                    # 移除中心點超出影像的label
                    if rbox_xywhthetahxhy[0] < 0 or rbox_xywhthetahxhy[0] > 1 or rbox_xywhthetahxhy[1] < 0 or rbox_xywhthetahxhy[1] > 1:
                        continue
              
                    """
                    aa=rbox_before_norm[rbox_before_norm[0]>=1]
                    bb=rbox_before_norm[rbox_before_norm[1]>=1]
                    cc=rbox_before_norm[rbox_before_norm[2]>=1]
                    dd=rbox_before_norm[rbox_before_norm[3]>=1]

                    if aa.shape[0] != 0 or aa.shape[0] != 0 or aa.shape[0] != 0 \
                        or aa.shape[0] != 0:
                        print('aa', aa)
                        print('bb', bb)
                        print('cc', cc)
                        print('dd', dd)
                        exit(0)
                    """

                    if self.output_label_format == 'xywhhxhy':
                        rbox_xywhthetahxhy = np.concatenate((rbox_xywhthetahxhy[:4], rbox_xywhthetahxhy[5:7]))
                        out_line_str = str(cls_id) + ' ' + ' '.join(list(map(str, rbox_xywhthetahxhy))) + '\n'
                    else:
                        out_line_str = str(cls_id) + ' ' + ' '.join(list(map(str, rbox_xywhthetahxhy[:5]))) + '\n'
                    # print('out_line_str', out_line_str)

                    outf.write(out_line_str)

            # if self.imgs_basename_list[img_idx] == '00192_merged':
            # cv2.namedWindow('img', flags=cv2.WINDOW_AUTOSIZE | cv2.WINDOW_GUI_NORMAL)
            # cv2.imshow('img', img)
            # cv2.waitKey(0)






if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, default='vehicle8cls', help='choose dataset (e.g., vehicle8cls, dota1.0, dota1.5, HRSC2016...)')
    parser.add_argument('--img-dir-path', type=str, default='images', help='images dir')
    parser.add_argument('--label-dir-path', type=str, default='rlabel_Txt', help='label dir')
    parser.add_argument('--output-label-dir-path', type=str, default='rlabels', help='output label dir')
    parser.add_argument('--output-label-format', type=str, default='xywhtheta', help='e.g., xywhtheta, xywhhxhy, xywhsin(theta)cos(theta)')
    parser.add_argument('--with-difficulty', action='store_true', help='output dota label with difficult label')
    opt = parser.parse_args()

    # images_dir_path = '/media/lab602-video1/test_doata_transform2yolo'
    # images_dir_path = '/media/lab602-video1/jacklin/train_data/DOTA/DOTA_devkit/dotatrainsplit1.0_608_150/images'
    # labels_dir_path = '/media/lab602-video1/jacklin/train_data/DOTA/DOTA_devkit/dotatrainsplit1.0_608_150/labelTxt'
    # DOTA1.0
    # images_dir_path = '/media/lab602/1C1051B41051959C/DOTA1.0/trainsplit_1024_512/images'
    # labels_dir_path = '/media/lab602/1C1051B41051959C/DOTA1.0/trainsplit_1024_512/r_labelTxt'
    # output_labels_dir_path = '/media/lab602/1C1051B41051959C/DOTA1.0/trainsplit_1024_512/rlabels'
    classnames_txt_path = '/media/lab602/1C1051B41051959C/DOTA1.0/dota1.0.names'

    # output_img_label_dir_path = '/media/lab602-video1/jacklin/train_data/DOTA/DOTA_devkit/test_output_check_img_label_dir'

    # vehicle8cls
    # images_dir_path = '/media/lab602/1C1051B41051959C/vehicle8cls_653_1920x1080/images'
    # labels_dir_path = '/media/lab602/1C1051B41051959C/vehicle8cls_653_1920x1080/labels'
    # output_labels_dir_path = '/media/lab602/1C1051B41051959C/vehicle8cls_653_1920x1080/rlabels_headcxy_wh_norm_w_imagewh_repair'
    # classnames_txt_path = '/home/lab602/lin_data/Experiment_data/data/vehicle8cls/classes_vehicle8cls.txt'
    # output_img_label_dir_path = '/media/lab602-video1/jacklin/train_data/8cls_dataset/vehicle8cls_merged_1920_1080_250/check_rlabels_img'

    images_dir_path = opt.img_dir_path
    labels_dir_path = opt.label_dir_path
    output_labels_dir_path = opt.output_label_dir_path

    if opt.dataset.find('dota') != -1:
        aaa = Transform_dota_to_yolo_obb(images_dir_path=images_dir_path, labels_dir_path=labels_dir_path,
                                        output_labels_dir_path=output_labels_dir_path, classnames_txt_path=classnames_txt_path, \
                                        dataset=opt.dataset, output_label_format=opt.output_label_format)
    elif opt.dataset == 'vehicle8cls':
        aaa = Transform_vehicle8cls_to_yolo_obb(images_dir_path=images_dir_path, labels_dir_path=labels_dir_path,
                                        output_labels_dir_path=output_labels_dir_path, classnames_txt_path=classnames_txt_path, \
                                        dataset=opt.dataset, output_label_format=opt.output_label_format)

    # transform_data_utils.draw_rlabels_to_check(img_dir_path=images_dir_path, label_dir_path=output_labels_dir_path, 
    #                                 output_img_dir_path=output_img_label_dir_path, classnames_txt_path=classnames_txt_path)

    # aaa = Transform_dota_v1_0_to_yolo_obb()
    # aaa.print_path()
    print('Done!')
    # TODO:

