#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path

gui_root_path = Path(__file__).parent.resolve()

train_txt_path = gui_root_path / 'Model' / 'YOLOv4' / 'data' / 'train_vehicle8cls_723.txt'
val_txt_path = gui_root_path / 'Model' / 'YOLOv4' / 'data' / 'val_vehicle8cls_180.txt'
data_yaml_path = gui_root_path / 'Model' / 'YOLOv4' / 'data' / 'vehicle8cls_obb_1920_1080_total903train723val180.yaml'

with open(train_txt_path, 'r', encoding='utf-8') as infile:
    lines = infile.readlines()

for idx, line in enumerate(lines):
    new_line = gui_root_path / 'train_val_imgs_labels' / line[line.find('vehicle8cls_903'):]
    lines.pop(idx)
    lines.insert(idx, str(new_line))

with open(train_txt_path, 'w', encoding='utf-8') as outfile:
    outfile.writelines(lines)

with open(val_txt_path, 'r', encoding='utf-8') as infile:
    lines = infile.readlines()

for idx, line in enumerate(lines):
    new_line = gui_root_path / 'train_val_imgs_labels' / line[line.find('vehicle8cls_903'):]
    lines.pop(idx)
    lines.insert(idx, str(new_line))

with open(val_txt_path, 'w', encoding='utf-8') as outfile:
    outfile.writelines(lines)

with open(data_yaml_path, 'r', encoding='utf-8') as infile:
    lines = infile.readlines()

for idx, line in enumerate(lines):
    if line.split(':')[0]=='train':
        print('line', line)
        lines.pop(idx)
        lines.insert(idx,'train: {}\n'.format(str(train_txt_path)))

    if line.split(':')[0]=='val':
        print('line', line)
        lines.pop(idx)
        lines.insert(idx,'val: {}\n'.format(str(val_txt_path)))

    if line.split(':')[0]=='test':
        print('line', line)
        lines.pop(idx)
        lines.insert(idx,'test: {}\n'.format(str(val_txt_path)))

with open(data_yaml_path, 'w', encoding='utf-8') as outfile:
    outfile.writelines(lines)
