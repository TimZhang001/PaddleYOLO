# Copyright (c) 2019 PaddlePaddle Authors. All Rights Reserved.
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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import os.path as osp
import re
import random

__all__ = ['create_list']


def create_list(devkit_dir, years, output_dir):
    """
    create following list:
        1. trainval.txt
        2. test.txt
    """
    trainval_list = []
    test_list = []
    for year in years:
        trainval, test = _walk_voc_dir(devkit_dir, year, output_dir)
        trainval_list.extend(trainval)
        test_list.extend(test)

    random.shuffle(trainval_list)
    with open(osp.join(output_dir, 'trainval.txt'), 'w') as ftrainval:
        for item in trainval_list:
            ftrainval.write(item[0] + ' ' + item[1] + '\n')

    with open(osp.join(output_dir, 'test.txt'), 'w') as fval:
        ct = 0
        for item in test_list:
            ct += 1
            fval.write(item[0] + ' ' + item[1] + '\n')


def _get_voc_dir(devkit_dir, year, type):
    return osp.join(devkit_dir, 'VOC' + year, type)


def _walk_voc_dir(devkit_dir, year, output_dir):
    filelist_dir = _get_voc_dir(devkit_dir, year, 'ImageSets/Main')
    annotation_dir = _get_voc_dir(devkit_dir, year, 'Annotations')
    img_dir = _get_voc_dir(devkit_dir, year, 'JPEGImages')
    trainval_list = []
    test_list = []
    added = set()

    for _, _, files in os.walk(filelist_dir):
        for fname in files:
            img_ann_list = []
            if re.match(r'[a-z]+_trainval\.txt', fname):
                img_ann_list = trainval_list
            elif re.match(r'[a-z]+_test\.txt', fname):
                img_ann_list = test_list
            else:
                continue
            fpath = osp.join(filelist_dir, fname)
            for line in open(fpath):
                name_prefix = line.strip().split()[0]
                if name_prefix in added:
                    continue
                added.add(name_prefix)
                ann_path = osp.join(
                    osp.relpath(annotation_dir, output_dir),
                    name_prefix + '.xml')
                img_path = osp.join(
                    osp.relpath(img_dir, output_dir), name_prefix + '.jpg')
                img_ann_list.append((img_path, ann_path))

    return trainval_list, test_list


def bbox_iou(bbox_gt, bbox_pred):
    """
    Calculate the Intersection of Unions (IoUs) between bounding boxes.
    Args:
        bbox_gt (list): [x1, y1, x2, y2]
        bbox_pred (list): [x1, y1, width, height]
    Returns:
        float: IoU
    """
    x1_gt, y1_gt, x2_gt, y2_gt = bbox_gt
    x1_pred, y1_pred, w_pred, h_pred = bbox_pred

    x2_pred = x1_gt + w_pred
    y2_pred = y1_gt + h_pred

    # get the overlap rectangle
    x1 = max(x1_gt, x1_pred)
    y1 = max(y1_gt, y1_pred)
    x2 = min(x2_gt, x2_pred)
    y2 = min(y2_gt, y2_pred)

    # calculate the area of the overlap rectangle
    w = max(0, x2 - x1)
    h = max(0, y2 - y1)
    inter = w * h

    # calculate the area of both bboxes
    area_gt   = (x2_gt   - x1_gt)   * (y2_gt   - y1_gt)
    area_pred = (x2_pred - x1_pred) * (y2_pred - y1_pred)
    iou       = inter / (area_gt + area_pred - inter)

    return iou

def get_key_from_value(dictionary, target_value):
    for key, value in dictionary.items():
        if value == target_value:
            return key
    return None

# 根据bboxs、class_ids和bbox_res，判断正常检测、过检测 、漏检测
def cal_bboxs_iou(bboxs_gt, class_ids_gt, catid2name, draw_thresh, bboxs_res):
    """
    Calculate iou between bboxs_gt and bboxs_res
    """
    
    iou_thresh   = 0.20
    bboxs_gt     = bboxs_gt.tolist()
    bboxs_gt_new = []
    for bbox_gt in bboxs_gt:
        bboxs_gt_new.append({"bbox":bbox_gt}) 
    
    # 在bboxs_res中找到阈值大于draw_thresh的bboxs
    bboxs_res_new = []
    for i, bbox_res in enumerate(bboxs_res):
        cur_class_id = int(bbox_res['category_id'])
        
        # 如果threshold是一个dict,且包含catid2name[catid]的key
        if isinstance(draw_thresh, dict):
            cur_key       = get_key_from_value(catid2name, cur_class_id)
            cur_threshold = draw_thresh.get(cur_key, 0.5)
        else:
            cur_threshold = draw_thresh
        
        if bbox_res['score'] < cur_threshold:
            continue
        bboxs_res_new.append(bbox_res)

    
    # 遍历bboxs_res_new，判断正常检测、过检测
    overkill_flg = 0
    for i, bbox_res in enumerate(bboxs_res_new):

        # 类别相同，且iou大于0.5，正常检测
        for j, bbox_gt in enumerate(bboxs_gt_new):
            if class_ids_gt[j] != bbox_res['category_id']:
                continue
            iou = bbox_iou(bbox_gt['bbox'], bbox_res['bbox'])
            if iou >= iou_thresh:
                bbox_res['status'] = 'normal'
                break
        
        # 否则都是过检测
        if 'status' not in bbox_res:
            bbox_res['status'] = 'over'
            overkill_flg = 1

    # 遍历bboxs_gt，判断正常检测、判断漏检测
    misskill_flg = 0
    for i, bbox_gt in enumerate(bboxs_gt_new):

        # 类别相同，且iou大于0.5，正常检测
        for j, bbox_res in enumerate(bboxs_res_new):
            if class_ids_gt[i] != bbox_res['category_id']:
                continue
            iou = bbox_iou(bbox_gt['bbox'], bbox_res['bbox'])
            if iou >= iou_thresh:
                bbox_gt['status'] = 'normal'
                break
        
        # 否则都是漏检测
        if 'status' not in bbox_gt:
            bbox_gt['status'] = 'over'
            misskill_flg      = 2

    return overkill_flg + misskill_flg


def get_file_name_from_roidbs(roidbs, im_id):
    im_file = None
    for idx, roidb in enumerate(roidbs):
        if roidb['im_id'] == im_id:
            im_file = roidb['im_file']
            if "Gap" in im_file and im_id != idx:
                a = 1
            break
    return im_file
