"""
print('Import yolov4 related path to python path')
from os import sys, path
yolo_root_dir_path = path.dirname(path.abspath(__file__))
sys.path.insert(0,  yolo_root_dir_path)
sys.path.insert(0,  path.join(yolo_root_dir_path, 'models'))
sys.path.insert(0,  path.join(yolo_root_dir_path, 'utils'))
print('sys.path', sys.path)
"""
"""
sys.path.insert(0,  path.join(yolo_root_dir_path, 'utils', 'box_utils'))
sys.path.insert(0,  path.join(yolo_root_dir_path, 'utils', 'Rotated_IoU'))

"""
