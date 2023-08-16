'''
Created on Mar 11, 2019

v1.13
Change List:
    1. Fix return to default zooming size after zoomed only.
    2. Fix mis-loading bounding box data of previous image after opened any labeled image

@author: lab-602-ubuntu1604
'''

import pyforms
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlImage
from pyforms.controls import ControlLabel
from pyforms.controls import ControlText
from pyforms.controls import ControlCheckBox
from pyforms.controls import ControlButton
from pyforms.controls import ControlDir

from confapp import conf
import settings
conf+=settings

import cv2
import os
import os.path as osp
import glob
import numpy as np

class LabelUI(BaseWidget):
    
    def __init__(self):
        super().__init__('Label it v1.13')
        
        # Definition of UI elements
        self._label_window = LabelItControlImage('Image')
        self._label_window.parent = self # for the sake of accessing the parameters defined in main window
        # Define ControlImage events
        self._label_window.click_event = self.__labelWindowClickEvent
        self._label_window.drag_event = self.__draggingEvent
        self._label_window.end_drag_event = self.__endDraggingEvent
        self._label_window.key_release_event = self.__hotKeyEvent
        
        # Define dragging state
        self._dragged = False # parameter to store if image dragged or not. If dragged LabelItControlImage will keep zooming while create or remove bbox
        self._end_drag = False # True if end dragged once, else False
        
        # Define labels
        self._hint_of_size_box_label = ControlLabel('Area of Bounding Box: (2k+1)^2')
        self._img_name_label = ControlLabel('File Name:')
        
        # Where the size of size box value is its half length, all the labeled box are square.
        self._size_box_of_pedestrian = ControlText(', k  =')
        self._size_box_of_bike = ControlText(', k  =')
        self._size_box_of_moto = ControlText(', k  =')
        
        # initialize size box value
        with open('box_size_setting.dat', 'r') as f_setting:
            info_ = f_setting.readline()
            setting_ = info_.split(',')
        self._size_box_of_pedestrian.value = setting_[0]
        self._size_box_of_bike.value = setting_[1]
        self._size_box_of_moto.value = setting_[2]
        
        # Define list to store labeled information
        self._labeled_list = []
        self._bbox_index = None
        
        # Other variables
        self._img_list = [] # Define path list to store files' path
        self._index_of_img_list = 0 # Define index of image list to control to go next or backward image
        self._origin_img = 0 # use for dragging event
        self._img_height = None
        self._img_width = None
        self._tx = 0 # use for dragging event, it means translation distance of x-axis
        self._ty = 0 # use for dragging event, it means translation distance of y-axis
        self._sum_of_prev_tx = 0 # use for draw square after dragging once
        self._sum_of_prev_ty = 0 # use for draw square after dragging once
        self._shifted_frame = None # use for dragging event and click event to make translate correct
        self._prev_shifted_frame = None # use for dragging event and click event to make translate correctly
        self._bbox_oringin_x = None # use for _drag_bbox, store coordinate before dragging bounding box, thus dragging correctly
        self._bbox_oringin_y = None # use for _drag_bbox, store coordinate before dragging bounding box, thus dragging correctly
        self._file_path = None
        
        # Define check boxes
        vehicle_check_box_helptext = "Press E(up) or D(down) to change vehicle type."
        self._check_box_of_pedestrian = ControlCheckBox('Pedestrian', helptext=vehicle_check_box_helptext)
        self._check_box_of_bike = ControlCheckBox('Bicycle', helptext=vehicle_check_box_helptext)
        self._check_box_of_moto = ControlCheckBox('Motorcycle', helptext=vehicle_check_box_helptext)
        create_or_remove_bbox_helptext = "Click left button to create new bounding box.\n" \
                                         "Click right button to remove bounding box.\n" \
                                         "Press (R) to switch to this mode."
        self._check_box_of_create_or_remove_bbox = ControlCheckBox('Create or Remove Bounding Box', helptext=create_or_remove_bbox_helptext)
        self._check_box_of_dragging = ControlCheckBox('Dragging Mode', helptext='(D)')
        self._check_box_of_dragging_bbox = ControlCheckBox('Dragging Bounding Box', helptext='(Space)')
        self._check_box_of_saving_label = ControlCheckBox('Saving while going to next or previous image')
        # Define check box event
        self._check_box_of_pedestrian.changed_event = self._check_state_of_pedestrian
        self._check_box_of_bike.changed_event = self._check_state_of_bike
        self._check_box_of_moto.changed_event = self._check_state_of_moto
        self._check_box_of_create_or_remove_bbox.changed_event = self._check_state_of_create_bbox
        self._check_box_of_dragging.changed_event = self._check_state_of_dragging
        self._check_box_of_dragging_bbox.changed_event = self._check_state_of_dragging_bbox
        
        # Define check box initial state
        self._check_box_of_pedestrian.value = True
        self._check_box_of_bike.value = False
        self._check_box_of_moto.value = False
        self._check_box_of_create_or_remove_bbox.value = False
        self._check_box_of_dragging.value = True
        self._check_box_of_dragging_bbox.value = False
        self._check_box_of_saving_label.value = True # set default to enable
        
        # Define load directory
        self._get_img_dir = ControlDir('Image Directory')
        self._img_dir = '' # let _get_img_dir save image directory to _img_dir 
        
        # Define buttons
        self._confirm_img_dir_button = ControlButton('Confirm')
        self._next_img_button = ControlButton('Next Image', helptext='(F)')
        self._prev_img_button = ControlButton('Prev Image', helptext='(S)')
        self._remove_last_square_button = ControlButton('Remove Last Square')
        self._copy_bbox_and_go_next_button = ControlButton('Copy and Go to Next', helptext='(V)')
        self._copy_bbox_and_go_prev_button = ControlButton('Copy and Go to Prev', helptext='(X)')
        # Define button action
        self._confirm_img_dir_button.value = self.__confirmImgDirAction
        self._next_img_button.value = self.__nextImgAction
        self._prev_img_button.value = self.__prevImgAction
        self._remove_last_square_button.value = self.__removeLastSquareAction
        self._copy_bbox_and_go_next_button.value = self.__cpAndNextAction
        self._copy_bbox_and_go_prev_button.value = self.__cpAndPrevAction
        
        # Define close event
        self.before_close_event = self.__beforeMainWindowClose
        
        print('control image:', self._label_window.form)
        print('control label:', self._hint_of_size_box_label.form)
        print('text box:', self._size_box_of_pedestrian.form)
        print('check box:', self._check_box_of_pedestrian.form)
        print('control button:', self._confirm_img_dir_button.form)
        
        # Define main menu
        self.mainmenu = [
            { 'File': [
                {'Open Image': self.__openImgEvent}
                ]
            },
            { 'Operation': [
                {'Save Current Box': self.__saveCurrentBoxEvent}
                ]
            }
        ]
        
        # Define the organization of forms
        self.formset = (
            ['_get_img_dir',
             (' ', '_confirm_img_dir_button'),
             ('_check_box_of_saving_label'),
             ('_next_img_button'),
             ('_prev_img_button'),
             ('_remove_last_square_button'),
             ('_copy_bbox_and_go_next_button'),
             ('_copy_bbox_and_go_prev_button'),
             ' '], '||',                        ['_img_name_label',
                                                 '_label_window'], '||', [ (' ', '_hint_of_size_box_label'),
                                                                         ('_check_box_of_pedestrian', '_size_box_of_pedestrian'),
                                                                         ('_check_box_of_bike', '_size_box_of_bike'),
                                                                         ('_check_box_of_moto', '_size_box_of_moto'),
                                                                         ('_check_box_of_create_or_remove_bbox'),
                                                                         ('_check_box_of_dragging'),
                                                                         ('_check_box_of_dragging_bbox'),
                                                                         ' '
                                                                       ]
                        )
        
        # Define open file action by override BaseWidget.load_form_filename
        self.load_form_filename = self._get_file_path_from_user
        
    # Define working functions
    def __openImgEvent(self):
        self._clear_translation_data()
        self._labeled_list.clear() # Initialize _label_list before open directory to prevent load wrong list.
        try:
            self.load_window()
            
            self._label_window.value = self._file_path
        except IndexError:
            print("Select cancel.")
    
    def __saveCurrentBoxEvent(self):
        img_width, img_height = self._label_window.value.shape[:2]
        print('X, Y:', img_height, img_width)
        with open(self._annotation_file_path, 'w') as output_f:
            for sqr in self._labeled_list:
                print('SaveBox:', (str(sqr.type) + ' ' + str(sqr.x/img_width) + ' ' + str(sqr.y/img_height) + ' ' + str((sqr.half_len*2)/img_width) + ' ' + str((sqr.half_len*2)/img_height)))
                # (class_index) (box_center_point_x/img_width) (box_center_point_y/img_height) (box_width/img_width) (box_height/img_height)
                output_f.write(str(sqr.type) + ' ' + str(sqr.x/img_width) + ' ' + str(sqr.y/img_height) + ' ' + str((sqr.half_len*2)/img_width) + ' ' + str((sqr.half_len*2)/img_height) + '\n')
    
    def _load_labeled_data_from_txt(self):
        '''
        load labeled data from .txt file under same directory with image
        '''
        self._labeled_list.clear()
        img_width, img_height = self._label_window.value.shape[:2]
        with open(self._annotation_file_path, 'r') as input_f:
            for line in input_f:
                infos = line.split(' ')
                x = float(infos[1])*img_width
                y = float(infos[2])*img_height
                half_len = (float(infos[3])*img_width)/2
                if int(infos[0]) == 0:
                    pedestrian_box = SquareBox(self, 'pedestrian', x, y, half_len)
                    self._labeled_list.append(pedestrian_box)
                    new_img = pedestrian_box._draw_square(self._label_window.value, (255, 0, 0))
                    self._label_window.value = new_img
                elif int(infos[0]) == 1:
                    bike_box = SquareBox(self, 'bike', x, y, half_len)
                    self._labeled_list.append(bike_box)
                    new_img = bike_box._draw_square(self._label_window.value, (0, 255, 0))
                    self._label_window.value = new_img
                elif int(infos[0]) == 2:
                    moto_box = SquareBox(self, 'moto', x, y, half_len)
                    self._labeled_list.append(moto_box)
                    new_img = moto_box._draw_square(self._label_window.value, (0, 0, 255))
                    self._label_window.value = new_img
                    
    def _load_labeled_data_from_list(self):
        '''
        load labeled data from _label_list
        '''
        blue = (255, 0, 0)
        green = (0, 255, 0)
        red = (0, 0, 255)
        line_color_table = {0: blue, 1: green, 2: red} # 0 is 'pedestrian', 1 is 'bike' and 2 is 'moto'
        for sqr in self._labeled_list:
                new_img = sqr._draw_square(self._label_window.value, line_color_table[sqr.type])
                self._label_window.value = new_img
    # Define button actions
    def __confirmImgDirAction(self):
        self._clear_translation_data()
        self._labeled_list.clear() # Initialize _label_list before open directory to prevent load wrong list.
        
        self._img_dir = self._get_img_dir.value
        print(self._img_dir)
        img_files_path = osp.join(self._img_dir, '*.jpg') # now only support .png file
        self._img_list = glob.glob(img_files_path)
        temp_list = []
        
        # sort file
        for path_ in self._img_list:
            #print(path_)
            base_name = osp.basename(path_)
            file_name = base_name.split('.')[0]
            temp_list.append([file_name, path_])
        temp_list.sort()
        self._img_list.clear()
        for data_ in temp_list:
            self._img_list.append(data_[1])
        '''
        print('\n\n')
        for i in self._img_list:
            print(i)
        '''
            
        self._index_of_img_list = 0
        #print(self._img_list[self._index_of_img_list])
        
        self._label_window.value = self._img_list[self._index_of_img_list]
            
    def __nextImgAction(self):
        self._clear_translation_data()
        if self._index_of_img_list <= (len(self._img_list) - 2): # prevent out of index from tail
            if not self._labeled_list:
                # if _labeled_list is empty, do nothing 
                pass
            else:
                # if _labeled_list isn't an empty list and auto saving is checked, save and then reset it
                if self._check_box_of_saving_label.value == True:
                    self.__saveCurrentBoxEvent() # save label before going to next 
                    self._labeled_list.clear() # initialize list before starting to label next image
                else:
                    self._labeled_list.clear()
            self._index_of_img_list = self._index_of_img_list + 1 # move to next image
            
            
            self._clear_dragging_state()
            self._clear_zooming_state()
            self._label_window.value = self._img_list[self._index_of_img_list]
        
    def __prevImgAction(self):
        self._clear_translation_data()
        if self._index_of_img_list >= 1: # prevent out of index from head
            if not self._labeled_list:
                # if _labeled_list is empty, do nothing 
                pass
            else:
                # if _labeled_list isn't an empty list and auto saving is checked, save and then reset it
                if self._check_box_of_saving_label.value == True:
                    self.__saveCurrentBoxEvent() # save label before going to previous
                    self._labeled_list.clear() # initialize list before starting to label next image
                else:
                    self._labeled_list.clear()
            self._index_of_img_list = self._index_of_img_list - 1
            
            
            self._clear_dragging_state()
            self._clear_zooming_state()
            self._label_window.value = self._img_list[self._index_of_img_list]
                
    def __removeLastSquareAction(self):
        if not self._labeled_list:
            print('list is empty')
        else:
            self._labeled_list.pop()
            if (self._tx != 0) or (self._ty != 0):
                self._label_window.value = self._shifted_frame.copy()
            else:
                self._label_window.value = cv2.imread(self._file_path)
                
            try:
                self._load_labeled_data_from_list() # load labeled data
            except FileNotFoundError:
                print('No label could be input.')
                
    def __cpAndNextAction(self):
        self._clear_translation_data()
        if self._index_of_img_list <= (len(self._img_list) - 2): # prevent out of index from tail
            if not self._labeled_list:
            # if _labeled_list is empty, do nothing 
                pass
            else:
            # if _labeled_list isn't an empty list and auto saving is checked, save and then reset it
                if self._check_box_of_saving_label.value == True:
                    self.__saveCurrentBoxEvent() # save label before going to next 
                    #self._labeled_list.clear() # copy it, so do not clear
                else:
                    pass
            self._index_of_img_list = self._index_of_img_list + 1 # move to next image
            
            
            self._clear_dragging_state()
            self._clear_zooming_state()
            self._label_window.value = self._img_list[self._index_of_img_list]
    
    def __cpAndPrevAction(self):
        self._clear_translation_data()
        if self._index_of_img_list >= 1: # prevent out of index from head
            if not self._labeled_list:
                # if _labeled_list is empty, do nothing 
                pass
            else:
                # if _labeled_list isn't an empty list and auto saving is checked, save and then reset it
                if self._check_box_of_saving_label.value == True:
                    self.__saveCurrentBoxEvent() # save label before going to previous
                else:
                    pass
            self._index_of_img_list = self._index_of_img_list - 1
            
            
            self._clear_dragging_state()
            self._clear_zooming_state()
            self._label_window.value = self._img_list[self._index_of_img_list]
    
    # override base function "load_form_filename(filename)" from BaseWidget
    def _get_file_path_from_user(self, filename):
        self._set_paths(filename) # set all needed paths while loading file
        
    def _set_paths(self, file_path):
        '''
        set new file path and name
        '''
        self._file_path = file_path
        self._img_dir = osp.dirname(file_path)
        self._full_file_name = self._file_path.split(os.sep)[-1]
        self._file_name = self._full_file_name.split('.')[0]
        self._annotation_full_file_name = self._file_name + '.txt'
        self._annotation_file_path = osp.join(self._img_dir, self._annotation_full_file_name)
        
    # override check_box changed_event
    def _check_state_of_pedestrian(self):
        if self._check_box_of_pedestrian.value == True:
            self._check_box_of_bike.value = False
            self._check_box_of_moto.value = False
            
            self._avoid_first_change_bug(self._check_box_of_pedestrian)
        
    def _check_state_of_bike(self):
        if self._check_box_of_bike.value == True:
            self._check_box_of_pedestrian.value = False
            self._check_box_of_moto.value = False
            
            self._avoid_first_change_bug(self._check_box_of_bike)
        
    def _check_state_of_moto(self):
        if self._check_box_of_moto.value == True:
            self._check_box_of_pedestrian.value = False
            self._check_box_of_bike.value = False
            
            self._avoid_first_change_bug(self._check_box_of_moto)
            
    def _check_state_of_create_bbox(self):
        if self._check_box_of_create_or_remove_bbox.value == True:
            self._check_box_of_dragging.value = False
            self._check_box_of_dragging_bbox.value = False
            
            self._avoid_first_change_bug(self._check_box_of_create_or_remove_bbox)
    def _check_state_of_dragging(self):
        if self._check_box_of_dragging.value == True:
            self._check_box_of_create_or_remove_bbox.value = False
            self._check_box_of_dragging_bbox.value = False
            
            self._avoid_first_change_bug(self._check_box_of_dragging)
            
    def _check_state_of_dragging_bbox(self):
        if self._check_box_of_dragging_bbox.value == True:
            self._check_box_of_create_or_remove_bbox.value = False
            self._check_box_of_dragging.value = False
            
            self._avoid_first_change_bug(self._check_box_of_dragging_bbox)
    
    # work around for unknown reason of clear all after first change check box
    def _avoid_first_change_bug(self, check_box): # object transfer like c++ reference, thus object could be control directly in this method
        if check_box.value == False:
            check_box.value = True
    
    # define click and dragging event functions
    def _create_bbox(self, x, y):
        if (self._check_box_of_pedestrian.value == 1) and (self._size_box_of_pedestrian.value != ''):
        # if pedestrian box was checked and size box entered pixels, draw square
            pedestrian_box = SquareBox(self, 'pedestrian', x, y, self._size_box_of_pedestrian.value)
            self._labeled_list.append(pedestrian_box)
        elif (self._check_box_of_bike.value == 1) and (self._size_box_of_bike.value != ''):
        # if bike box was checked and size box entered pixels, draw square
            bike_box = SquareBox(self, 'bike', x, y, self._size_box_of_bike.value)
            self._labeled_list.append(bike_box)
        elif (self._check_box_of_moto.value == 1) and (self._size_box_of_moto.value != ''):
        # if moto box was checked and size box entered pixels, draw square
            moto_box = SquareBox(self, 'moto', x, y, self._size_box_of_moto.value)
            self._labeled_list.append(moto_box)
    
    def _remove_clicked_bbox(self, x, y):
        i = 0
        data_lenth = len(self._labeled_list)
        while i < data_lenth:
        # while loop to find the first matched bounding box, and remove it from _label_list
            box = self._labeled_list[i]
            left_top_point = [box.x - box.half_len, box.y - box.half_len]
            right_bottom_point = [box.x + box.half_len, box.y + box.half_len]
            if ( (x <= right_bottom_point[0]) and (x >= left_top_point[0]) ) and ( (y <= right_bottom_point[1]) and (y >= left_top_point[1]) ):
                self._labeled_list.remove(self._labeled_list[i])
                data_lenth = data_lenth - 1
            i = i + 1
    
    def _translate_image(self, start_point, end_point):
        if self._dragged and self._end_drag:
        # If dragged, modify start and end point to real x, y
            x0 = start_point[0] - self._tx
            y0 = start_point[1] - self._ty
            x1 = end_point[0] - self._tx
            y1 = end_point[1] - self._ty
            
            temp_frame = self._prev_shifted_frame.copy()
        else:
            x0, y0 = start_point[0], start_point[1]
            x1, y1 = end_point[0], end_point[1]
            
            temp_frame = self._origin_img.copy()
            
        if (x0 != x1) and (y0 != y1): # avoid pressed but not move
            self._dragged = True
            
            # The following 5 lines do image translation, reference from opencv-python translation
            rows, cols = temp_frame.shape[:2]
            self._tx = x1 - x0
            self._ty = y1 - y0
            M = np.float32( [ [1,0,self._tx], [0,1,self._ty] ] )
            self._shifted_frame = cv2.warpAffine(temp_frame, M, (cols, rows)) # Finally get the shifted frame
            
            self._label_window.value = self._shifted_frame.copy()
            self._load_labeled_data_from_list()
        
    def _drag_bbox(self, start_point, end_point):
        if self._dragged and self._end_drag:
            x0 = start_point[0] - self._sum_of_prev_tx
            y0 = start_point[1] - self._sum_of_prev_ty
            x1 = end_point[0] - self._sum_of_prev_tx
            y1 = end_point[1] - self._sum_of_prev_ty
            
            temp_frame = self._prev_shifted_frame.copy()
        else:
            x0, y0 = start_point[0], start_point[1]
            x1, y1 = end_point[0], end_point[1]
            
            temp_frame = self._origin_img.copy()
            
        if (x0 != x1) and (y0 != y1): # avoid pressed but not move
            if self._bbox_index == None:
                i = 0
                data_lenth = len(self._labeled_list)
                while i < data_lenth:
                # while loop to find the first matched bounding box, and remove it from _label_list
                    box = self._labeled_list[i]
                    left_top_point = [box.x - box.half_len, box.y - box.half_len]
                    right_bottom_point = [box.x + box.half_len, box.y + box.half_len]
                    if ( (x0 <= right_bottom_point[0]) and (x0 >= left_top_point[0]) ) and ( (y0 <= right_bottom_point[1]) and (y0 >= left_top_point[1]) ):
                        self._bbox_index = i
                        self._bbox_oringin_x = box.x
                        self._bbox_oringin_y = box.y
                        
                        i = data_lenth + 1 # leave while loop after dragged bbox
                        
                    i = i + 1
            else:
                self._labeled_list[self._bbox_index].x = self._bbox_oringin_x + (x1 - x0)
                self._labeled_list[self._bbox_index].y = self._bbox_oringin_y + (y1 - y0)
                
                self._label_window.value = temp_frame.copy()
                self._load_labeled_data_from_list()
    
    # override ControlImage events
    def __labelWindowClickEvent(self, event, x, y):
    # While mouse dragging(of course, before mouse release), _translate_image will create new _tx and _ty. These two parameter do not add to
    # _sum_of_prev_tx and _sum_of_prev_ty yet, thus the coordinate in SquareBox._draw_square need to add both like
    # x0 = round(left_top_point[0] + self._parent._tx + self._parent._sum_of_prev_tx). The other action like _create_or_remove_bbox or _drag_bbox,
    # They all working after __endDraggingEvent, here _tx and _ty are not meaningful. So the real coordinate will be input_x + _sum_of_prev_tx.
    # That's why there equations are different. 
    
        mouse_click_event_table = {'LeftButton': 1, 'RightButton': 2} # number is defined same as Qt.MouseButton
        
        if not self._file_path:
            print('Please load image first.')
        else:
            self._origin_img = cv2.imread(self._file_path)
            print('x:', x, 'y:', y)
            if self._dragged and self._end_drag:
                x = x - self._sum_of_prev_tx
                y = y - self._sum_of_prev_ty
                temp_frame = self._prev_shifted_frame.copy()
            else:
                temp_frame = self._origin_img.copy()
        
        # all the x, y here must use real coordinate
        if self._check_box_of_create_or_remove_bbox.value == True:
        # if create or remove bbox is checked do the following, else do dragging
            if self._label_window._imageWidget._mouse_clicked_event.button == mouse_click_event_table['LeftButton']: # if clicked left button, create new box
                self._create_bbox(x, y)
            elif self._label_window._imageWidget._mouse_clicked_event.button == mouse_click_event_table['RightButton']: # if clicked right button, remove the bounding box user clicked
                self._remove_clicked_bbox(x, y)
            
            self._label_window.value = temp_frame.copy()
            try:
                self._load_labeled_data_from_list() # load labeled data
            except:
                print('Remove bounding box failed in __labelWindowClickEvent')
        
        
    def __draggingEvent(self, start_point, end_point):
        if self._label_window.value is not None:
        # every thing need input image
            if self._check_box_of_dragging.value == True:
                self._translate_image(start_point, end_point)
            elif self._check_box_of_dragging_bbox.value == True:
                self._drag_bbox(start_point, end_point)
            
    def __endDraggingEvent(self, start_point, end_point):
        if self._label_window.value is not None:
        # every thing need input image
            if (start_point[0] != end_point[0]) and (start_point[1] != end_point[1]): # avoid pressed but not move
                print('end drag')
                if self._check_box_of_dragging.value == True:
                    self._prev_shifted_frame = self._shifted_frame.copy()
                    self._sum_of_prev_tx = self._sum_of_prev_tx + self._tx
                    self._sum_of_prev_ty = self._sum_of_prev_ty + self._ty
                    self._end_drag = True
            if self._check_box_of_dragging_bbox.value == True:
                self._bbox_index = None
                self._bbox_oringin_x = None
                self._bbox_oringin_y = None
    
    def __hotKeyEvent(self, event):
        key_table = {'Space': 32, 'D':68, 'E':69, 'F':70, 'R':82, 'S':83, 'V':86, 'W':87, 'X':88} # key table all based on print(QtCore.Qt.Key) value
        if event.key() == key_table['F']: # QtCore.Qt.Key_F
            self.__nextImgAction() # go to next image
        elif event.key() == key_table['S']: # QtCore.Qt.Key_S
            self.__prevImgAction() # go to previous image
        elif event.key() == key_table['D']: # QtCore.Qt.Key_D
        # go to next vehicle check box
            create_box_state = [self._check_box_of_pedestrian, self._check_box_of_bike, self._check_box_of_moto]
            index = None
            for i in range(len(create_box_state)):
                if create_box_state[i].value == True:
                    index = (i + 1) % 3 # use mod to avoid over index
            
            if index is not None:
                create_box_state[index].value = True
        elif event.key() == key_table['E']:  # QtCore.Qt.Key_E
        # go to previous vehicle check box
            create_box_state = [self._check_box_of_pedestrian, self._check_box_of_bike, self._check_box_of_moto]
            index = None
            for i in range(len(create_box_state)):
                if create_box_state[i].value == True:
                    index = (i - 1) % 3 # use mod to avoid over index
            
            if index is not None:
                create_box_state[index].value = True
        elif event.key() == key_table['W']:
            self._check_box_of_dragging.value = True
        elif event.key() == key_table['R']:
            self._check_box_of_create_or_remove_bbox.value = True
        elif event.key() == key_table['Space']:
            self._check_box_of_dragging_bbox.value = True
        elif event.key() == key_table['V']:
            self.__cpAndNextAction()
        elif event.key() == key_table['X']:
            self.__cpAndPrevAction()
        
    def __beforeMainWindowClose(self):
        with open('box_size_setting.dat', 'w') as f_save_setting:
            f_save_setting.write(self._size_box_of_pedestrian.value + ',' + self._size_box_of_bike.value + ',' + self._size_box_of_moto.value)
    
    def _clear_translation_data(self):
        self._tx, self._ty = 0, 0
        self._sum_of_prev_tx, self._sum_of_prev_ty = 0, 0
    
    def _clear_dragging_state(self):
        self._dragged = False
        self._end_drag = False
        
    def _clear_zooming_state(self):
        self._label_window._imageWidget._zoomed = False
    
        
class SquareBox(object):
    '''
    labeled square box object
    '''
    def __init__(self, parent, object_name, x, y, half_len):
        '''
        where x, y are center of square box
        half_len is half length of square
        '''
        class_id_table = {'pedestrian': 0, 'bike':1, 'moto': 2}
        self.type = class_id_table[object_name]
        # x, y is center point
        self._x = round(float(x))
        self._y = round(float(y))
        self._half_len = round(float(half_len))
        self._parent = parent # to save and load parent class variable
        
    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self, value):
        self._x = round(float(value))
        
    @property
    def y(self):
        return self._y
    
    @y.setter
    def y(self, value):
        self._y = round(float(value))
        
    @property
    def half_len(self):
        return self._half_len
    
    @half_len.setter
    def half_len(self, value):
        self._half_len = round(float(value))
        
    def _draw_square(self, background_img, line_color, line_width = 2):
        '''
        draw square box on new image, and return it
        '''
        left_top_point = (self._x-self._half_len, self._y-self._half_len)
        right_bottom_point = (self._x+self._half_len, self._y+self._half_len)
        if (self._parent._tx != 0) or (self._parent._ty != 0):
        # The following change point to the translated coordinate after dragged
            if self._parent._end_drag:
            # If dragged, modify start and end point to real x, y
                if self._parent._check_box_of_dragging.value == True:
                # here convert real coordinate(that store in _label_list) to screen coordinate in dragging mode
                    x0 = round(left_top_point[0] + self._parent._tx + self._parent._sum_of_prev_tx)
                    y0 = round(left_top_point[1] + self._parent._ty + self._parent._sum_of_prev_ty)
                    x1 = round(right_bottom_point[0] + self._parent._tx + self._parent._sum_of_prev_tx)
                    y1 = round(right_bottom_point[1] + self._parent._ty + self._parent._sum_of_prev_ty)
                elif (self._parent._check_box_of_create_or_remove_bbox.value == True) or (self._parent._check_box_of_dragging_bbox.value == True):
                # self._parent._check_box_of_create_or_remove_bbox.value will never let _end_drage to be False
                # here convert real coordinate(that store in _label_list) to screen coordinate in click mode
                    x0 = round(left_top_point[0] + self._parent._sum_of_prev_tx)
                    y0 = round(left_top_point[1] + self._parent._sum_of_prev_ty)
                    x1 = round(right_bottom_point[0] + self._parent._sum_of_prev_tx)
                    y1 = round(right_bottom_point[1] + self._parent._sum_of_prev_ty)
                
            else:
                x0 = round(left_top_point[0] + self._parent._tx)
                y0 = round(left_top_point[1] + self._parent._ty)
                x1 = round(right_bottom_point[0] + self._parent._tx)
                y1 = round(right_bottom_point[1] + self._parent._ty)
                
            
            left_top_point = (x0, y0)
            right_bottom_point = (x1, y1)
        new_img = cv2.rectangle(background_img, left_top_point, right_bottom_point, line_color, line_width)
        return new_img


from pyforms_gui.controls.control_player.AbstractGLWidget import AbstractGLWidget
#from AnyQt import QtCore

from AnyQt import _api
class LabelItAbstractGLWidget(AbstractGLWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._zoomed = False
    
    def wheelEvent(self, event):
        
        if not self._move_img:
            self._zoomed = True
            
            # Zoom the video
            self._mouseX = event.x()
            self._mouseY = event.y()

            if _api.USED_API == _api.QT_API_PYQT5:
                p = event.angleDelta()
                delta = p.y()
            elif _api.USED_API == _api.QT_API_PYQT4:
                delta = event.delta()
        
            zoom_factor = delta / float(1500)

            self.zoom -= zoom_factor # I just override this line, to make wheel action being upside down.

            if self.zoom < -.98 and delta < 0:
                self.zoom = -0.98

            if self.zoom > 7 and delta > 0: # zoom limits
                self.zoom = 7

            # self.logger.debug("Wheel event | Current zoom: %s | Delta: %s | Zoom factor: %s", self.zoom, event.delta(), zoom_factor)
            self.update()
    
    def keyReleaseEvent(self, event):
    # override this function to clear parent class default hot key settings
        super(AbstractGLWidget, self).keyPressEvent(event)
        
        self.on_key_release(event)
        

from AnyQt.QtOpenGL import QGLWidget
class LabelItVideoGLWidget(LabelItAbstractGLWidget, QGLWidget): pass



from pyforms_gui.controls.control_base import ControlBase
from pyforms_gui.utils import tools
from AnyQt import uic

class LabelItControlImage(ControlImage):
    '''
    Change list:
        1. Let click event do nothing while keep pressing mouse.
        2. Compact program, move all file path initialization into ControlImage.value.setter
        3. Clear hot key setting.
        4. Change wheel action to be upside down.
    '''
    
    
    def init_form(self):
        control_path = tools.getFileInSameDirectory(__file__, "image.ui")
        self._form = uic.loadUi(control_path)
        self._imageWidget = LabelItVideoGLWidget()
        #self._imageWidget = LabelItVideoQt5GLWidget()
        self._form.imageLayout.addWidget(self._imageWidget)
        ControlBase.init_form(self)
    
    
    @ControlImage.value.setter
    def value(self, value):
        '''
        Give me string value will generate path informations
        If use cv2.imread to get nparray and send to here, function will work like the original version of ControlImage
        '''
        if type(value) is str:
        # move file path initialize to here
            self.parent._set_paths(value)
            self._value = cv2.imread(value)
            self.parent._img_name_label.value = 'File Name:' + self.parent._full_file_name
            if not self.parent._labeled_list:
            # if click next or previous image, program will clear _label_list to empty, so we need to load from txt. and so as __confirmImgDirAction
                try:
                    self.parent._load_labeled_data_from_txt() # load labeled data from .txt file
                except FileNotFoundError:
                    print('No label could be input.')
            else:
            # if click copy and go to next/previous, program will remain old _label_list and copy to new image, so we load from list again
                try:
                    self.parent._load_labeled_data_from_list() # load labeled data from list
                except FileNotFoundError:
                    print('No label could be input.')
                
            ControlImage.value.fset(self, self._value) # method fset is built in setter name in property
        else:
            ControlImage.value.fset(self, value) # method fset is built in setter name in property
        
        if self.parent._dragged == True or self._imageWidget._zoomed == True:
        # if dragged or zoomed, keep zooming size, else recover to normal scale when read image
            pass
        else:
            height, width = self._value.shape[:2]
            if (height*1.77) > float(width):
                self._imageWidget.zoom = 0.4 # get this value by try and error
            else:
                self._imageWidget.zoom = 0.0 # default value for normal rectangle size image
    

if __name__ == '__main__':
    pyforms.start_app(LabelUI)
    
    
    