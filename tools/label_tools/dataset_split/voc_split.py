# Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os.path as osp
import random
import xml.etree.ElementTree as ET
from .utils import list_files, is_pic, replace_ext
import os

def split_voc_dataset(dataset_dir, val_percent, test_percent, save_dir):
    if not osp.exists(osp.join(dataset_dir, "01_Annotations")):
        print("\'01_Annotations\' is not found in {}!".format(dataset_dir))

    if not osp.exists(osp.join(dataset_dir, "02_JPEGImages")):
        print("\'02_JPEGImages\' is not found in {}!".format(dataset_dir))
    
    if not osp.exists(osp.join(dataset_dir, "03_Labels/xml")):
        print("\'03_Labels\' is not found in {}!".format(dataset_dir))

    all_image_files = list_files(osp.join(dataset_dir, "02_JPEGImages"))

    image_anno_list = list()
    label_list      = list()
    for image_file in all_image_files:
        if not is_pic(image_file):
            continue
        anno_name = replace_ext(image_file, "xml")
        if osp.exists(osp.join(dataset_dir, "03_Labels/xml", anno_name)):
            image_anno_list.append([image_file, anno_name])
            try:
                tree = ET.parse(osp.join(dataset_dir, "03_Labels/xml", anno_name))
            except:
                raise Exception("文件{}不是一个良构的xml文件，请检查标注文件".format(osp.join(dataset_dir, "03_Labels/xml", anno_name)))
            
            objs = tree.findall("object")
            for i, obj in enumerate(objs):
                cname = obj.find('name').text
                if not cname in label_list:
                    label_list.append(cname)
        else:
            print("The annotation file {} doesn't exist!".format(anno_name))

    random.shuffle(image_anno_list)
    image_num = len(image_anno_list)
    val_num   = int(image_num * val_percent)
    test_num  = int(image_num * test_percent)
    train_num = image_num - val_num - test_num

    train_image_anno_list = image_anno_list[:train_num]
    val_image_anno_list   = image_anno_list[train_num:train_num + val_num]
    test_image_anno_list  = image_anno_list[train_num + val_num:]

    os.makedirs(save_dir, exist_ok=True)
    
    # train.txt
    with open(osp.join(save_dir, 'train.txt'), mode='w', encoding='utf-8') as f:
        for x in train_image_anno_list:
            file  = osp.join("02_JPEGImages", x[0])
            label = osp.join("03_Labels/xml", x[1])
            f.write('{} {}\n'.format(file, label))
    
    # val.txt
    with open(osp.join(save_dir, 'val.txt'), mode='w', encoding='utf-8') as f:
        for x in val_image_anno_list:
            file  = osp.join("02_JPEGImages", x[0])
            label = osp.join("03_Labels/xml", x[1])
            f.write('{} {}\n'.format(file, label))
    
    # test.txt
    if len(test_image_anno_list):
        with open(osp.join(save_dir, 'test.txt'), mode='w', encoding='utf-8') as f:
            for x in test_image_anno_list:
                file  = osp.join("02_JPEGImages", x[0])
                label = osp.join("03_Labels/xml", x[1])
                f.write('{} {}\n'.format(file, label))
    
    # all.txt
    with open(osp.join(save_dir, 'all.txt'), mode='w', encoding='utf-8') as f:
        for x in image_anno_list:
            file  = osp.join("02_JPEGImages", x[0])
            label = osp.join("03_Labels/xml", x[1])
            f.write('{} {}\n'.format(file, label))
    
    # label_list.txt
    with open(osp.join(save_dir, 'label_list.txt'), mode='w', encoding='utf-8') as f:
        for l in sorted(label_list):
            f.write('{}\n'.format(l))

    return train_num, val_num, test_num
