#!/usr/bin/env python
# coding: utf-8
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

import cv2
import json
import os
import os.path as osp
import shutil
import numpy as np
from .base import MyEncoder, is_pic, get_encoding, add_text_file
from matplotlib import pyplot as plt
import xml.dom.minidom as minidom
from .defect_type import MuraCommList, MuraLineList, MuraAllList

class X2VOC(object):
    def __init__(self):
        pass

    def convert(self, image_dir, json_dir, dataset_save_dir):
        """转换。
        Args:
            image_dir (str): 图像文件存放的路径。
            json_dir (str): 与每张图像对应的json文件的存放路径。
            dataset_save_dir (str): 转换后数据集存放路径。
        """
        assert osp.exists(image_dir), "The image folder does not exist!"
        assert osp.exists(json_dir), "The json folder does not exist!"
        if not osp.exists(dataset_save_dir):
            os.makedirs(dataset_save_dir)
        # Convert the image files.
        new_image_dir = osp.join(dataset_save_dir, "JPEGImages")
        if osp.exists(new_image_dir):
            raise Exception(
                "The directory {} is already exist, please remove the directory first".
                format(new_image_dir))
        os.makedirs(new_image_dir)
        for img_name in os.listdir(image_dir):
            if is_pic(img_name):
                shutil.copyfile(
                    osp.join(image_dir, img_name),
                    osp.join(new_image_dir, img_name))
        # Convert the json files.
        xml_dir = osp.join(dataset_save_dir, "Annotations")
        if osp.exists(xml_dir):
            raise Exception(
                "The directory {} is already exist, please remove the directory first".
                format(xml_dir))
        os.makedirs(xml_dir)
        self.json2xml(new_image_dir, json_dir, xml_dir)


class LabelMe2VOC(X2VOC):
    """将使用LabelMe标注的数据集转换为VOC数据集。
    """

    def __init__(self, target_size=512):
        self.defect_info = {}
        self.comm_list   = MuraCommList
        self.line_list   = MuraLineList
        self.target_size = target_size

    # 解析缺陷信息
    def _parse_defect_info(self, shape, project_type):

        if len(shape) == 0:
            return None, None, None, None, None
        
        if 'shape_type' in shape:
            if shape["shape_type"] != "rectangle":
                return None, None, None, None, None
            (xmin, ymin), (xmax, ymax) = shape["points"]
            xmin, xmax = sorted([xmin, xmax])
            ymin, ymax = sorted([ymin, ymax])
        else:
            points     = shape["points"]
            points_num = len(points)
            x = [points[i][0] for i in range(points_num)]
            y = [points[i][1] for i in range(points_num)]
            xmin = min(x)
            xmax = max(x)
            ymin = min(y)
            ymax = max(y)
        label = shape["label"]
        
        # 对标签进行个性化修改 多个类别
        if 1:
            if project_type == "Commons" and label not in self.comm_list:
                if label == "HLine":
                    label = "HShort"
                elif label == "VLine":
                    label = "VShort"
                else:
                    return None, None, None, None, None
            elif project_type == "Lines" and label not in self.line_list:
                if label == "HShort":
                    label = "HLine"
                elif label == "VShort":
                    label = "VLine"
                else:
                    return None, None, None, None, None
            elif project_type == "Alls":
                pass
        
        # 对标签进行个性化修改 单个类别
        if 0:
            if project_type == "Commons":
                if label not in self.comm_list:
                    return None, None, None, None, None
                else:
                    label = "Common"
            elif project_type == "Lines":
                if label not in self.line_list:
                    return None, None, None, None, None
                else:
                    label = "Line"
            elif project_type == "Alls":
                label = "defect"

        return xmin, ymin, xmax, ymax, label
        
    # 绘制缺陷信息
    def _plot_defect_infos(self, save_file, key, defect_center_x, defect_center_y, defect_aspect_ratio, defect_area, defect_width, defect_height):
        
        # 绘制缺陷的中心点
        show_image = np.zeros((512, 512, 3), dtype=np.uint8)
        plt.figure(dpi=200)
        plt.imshow(show_image)
        plt.scatter(defect_center_x, defect_center_y, c='r', s=10)
        plt.title("The center points of the defects in {}".format(key))
        plt.show()
        plt.savefig(osp.join(save_file, "{}_center.png".format(key)))
        plt.close()

        # 绘制缺陷的长宽比
        plt.figure(dpi=200)
        plt.hist(defect_aspect_ratio, bins=20, color='steelblue', edgecolor='k', alpha=0.7)
        plt.title("The aspect ratio of the defects in {}".format(key))
        plt.show()
        plt.savefig(osp.join(save_file, "{}_aspect_ratio.png".format(key)))
        plt.close()

        # 绘制缺陷的面积
        plt.figure(dpi=200)
        plt.hist(defect_area, bins=20, color='steelblue', edgecolor='k', alpha=0.7)
        plt.title("The area of the defects in {}".format(key))
        plt.show()
        plt.savefig(osp.join(save_file, "{}_area.png".format(key)))
        plt.close()

        # 绘制缺陷的宽度
        plt.figure(dpi=200)
        plt.hist(defect_width, bins=20, color='steelblue', edgecolor='k', alpha=0.7)
        plt.title("The width of the defects in {}".format(key))
        plt.show()
        plt.savefig(osp.join(save_file, "{}_width.png".format(key)))
        plt.close()

        # 绘制缺陷的高度
        plt.figure(dpi=200)
        plt.hist(defect_height, bins=20, color='steelblue', edgecolor='k', alpha=0.7)
        plt.title("The height of the defects in {}".format(key))
        plt.show()
        plt.savefig(osp.join(save_file, "{}_height.png".format(key)))
        plt.close()

    # 对缺陷信息进行按类别统计，统计每个缺陷的宽度、高度、面积、位置、长宽比等信息
    def defect_statistic(self, image_dir, json_dir):
        
        # 获取image_dir路径的上一级目录
        project_dir           = osp.dirname(image_dir)
        defect_statistic_file = osp.join(project_dir, "04_DefectStatistic")
        os.makedirs(defect_statistic_file, exist_ok=True)

        # 创建一个文本文件进行信息的保存
        file_name = osp.join(defect_statistic_file, "000_defect_info.txt")
        with open(file_name, "w") as file:
            file.write("The defect information of the dataset:\n\n")
        
        # 如果self.defect_info为空，进行json文件的读取
        if len(self.defect_info) == 0:
            for img_name in os.listdir(image_dir):
                img_name_part = osp.splitext(img_name)[0]
                json_file     = osp.join(json_dir, img_name_part + ".json")
                if not osp.exists(json_file):
                    os.remove(osp.join(image_dir, img_name))
                    continue
                
                with open(json_file, mode="r", encoding=get_encoding(json_file)) as j:
                    json_info = json.load(j)
                    for shape in json_info["shapes"]:
                        xmin, ymin, xmax, ymax, label = self._parse_defect_info(shape)
                        if xmin is None:
                            continue
                        
                        if label not in self.defect_info:
                            self.defect_info[label] = []
                        self.defect_info[label].append([xmin, ymin, xmax, ymax])    
        
        # 进行缺陷信息的统计
        for key in self.defect_info.keys():
            defect_num = len(self.defect_info[key])
            if defect_num == 0:
                continue
            defect_info   = np.array(self.defect_info[key])

            # 计算缺陷的宽度、高度、面积、长宽比等信息
            defect_width  = defect_info[:, 2] - defect_info[:, 0]
            defect_height = defect_info[:, 3] - defect_info[:, 1]
            defect_area   = defect_width * defect_height
            defect_aspect_ratio = defect_width / defect_height

            # 计算缺陷的中心点
            defect_center_x = (defect_info[:, 0] + defect_info[:, 2]) / 2
            defect_center_y = (defect_info[:, 1] + defect_info[:, 3]) / 2

            # 结果的绘制
            self._plot_defect_infos(defect_statistic_file, key, defect_center_x, \
                                    defect_center_y, defect_aspect_ratio, defect_area, defect_width, defect_height)
    
            # 输出缺陷的统计信息的均值和方差
            add_text_file(file_name, "The defect information of {}:".format(key))
            add_text_file(file_name, "The number of the defects: {}".format(defect_num))
            add_text_file(file_name, "The mean and var of the defect width:  {:.2f}, {:.2f}".format(np.mean(defect_width), np.std(defect_width)))
            add_text_file(file_name, "The mean and var of the defect height: {:.2f}, {:.2f}".format(np.mean(defect_height), np.std(defect_height)))
            add_text_file(file_name, "The mean and var of the defect area:   {:.2f}, {:.2f}".format(np.mean(defect_area), np.std(defect_area)))
            add_text_file(file_name, "The mean and var of the defect aspect ratio: {:.2f}, {:.2f}".format(np.mean(defect_aspect_ratio), np.std(defect_aspect_ratio)))
            add_text_file(file_name, "\n")

        # 统计每个类别缺陷的数量
        defect_num = 0
        for key in self.defect_info.keys():
            defect_num += len(self.defect_info[key])
            add_text_file(file_name, "The number of the defects in {}: {}".format(key, len(self.defect_info[key])))
        add_text_file(file_name, "The total number of the defects: {}".format(defect_num))
        print("The total number of the defects: {}".format(defect_num))

        # 进行数量的绘制, 需要把数量放在柱状图上方，类别信息垂直显示，避免重叠
        defect_num_list = [len(self.defect_info[key]) for key in self.defect_info.keys()]
        plt.figure(dpi=200)
        plt.bar(range(len(defect_num_list)), defect_num_list, color='steelblue', alpha=0.8)
        plt.title("The number of the defects in each class")
        plt.xticks(range(len(defect_num_list)), self.defect_info.keys(), rotation=45)
        for x, y in enumerate(defect_num_list):
            plt.text(x, y + 1, "%s" % y, ha='center', va='bottom', fontsize=10)
        plt.show()
        plt.savefig(osp.join(defect_statistic_file, "000_defect_num.png"))
        plt.close()
    
    # 
    def json2xml(self, image_dir, json_dir, xml_dir, project_type):
                
        self.defect_info = {}
        for img_name in os.listdir(image_dir):
            img_name_part = osp.splitext(img_name)[0]
            json_file     = osp.join(json_dir, img_name_part + ".json")
            
            # 没有json文件，直接删除图片 
            if not osp.exists(json_file):
                os.remove(osp.join(image_dir, img_name))
                continue
            xml_doc = minidom.Document()
            root    = xml_doc.createElement("annotation")
            xml_doc.appendChild(root)
            node_folder = xml_doc.createElement("folder")
            node_folder.appendChild(xml_doc.createTextNode("JPEGImages"))
            root.appendChild(node_folder)
            node_filename = xml_doc.createElement("filename")
            node_filename.appendChild(xml_doc.createTextNode(img_name))
            root.appendChild(node_filename)
            
            # 读取json文件 
            with open(json_file, mode="r", encoding=get_encoding(json_file)) as j:
                json_info = json.load(j)
                           
                if 'imageHeight' in json_info and 'imageWidth' in json_info:
                    h = json_info["imageHeight"]
                    w = json_info["imageWidth"]

                    if h != self.target_size or w != self.target_size:                  
                        img_file  = osp.join(image_dir, img_name)
                        im_data   = cv2.imread(img_file)
                        scale_x, scale_y = self.target_size / w, self.target_size / h
                        im_data   = cv2.resize(im_data, [self.target_size,self.target_size])
                        h, w      = self.target_size, self.target_size
                        cv2.imwrite(img_file, im_data)
                    else:
                        scale_x, scale_y = 1.0, 1.0
                else:
                    assert "The imageHeight is not in the json file. {}".format(json_file)
                        
                node_size  = xml_doc.createElement("size")
                node_width = xml_doc.createElement("width")
                node_width.appendChild(xml_doc.createTextNode(str(w)))
                node_size.appendChild(node_width)
                
                node_height = xml_doc.createElement("height")
                node_height.appendChild(xml_doc.createTextNode(str(h)))
                node_size.appendChild(node_height)
                node_depth = xml_doc.createElement("depth")
                node_depth.appendChild(xml_doc.createTextNode(str(3)))
                node_size.appendChild(node_depth)
                root.appendChild(node_size)
                
                # 进行缺陷信息的获取
                for shape in json_info["shapes"]:
                    xmin, ymin, xmax, ymax, label = self._parse_defect_info(shape, project_type)
                    if xmin is None:
                        continue
                    
                    # 进行scale的操作
                    xmin = int(xmin * scale_x)
                    ymin = int(ymin * scale_y)
                    xmax = int(xmax * scale_x)
                    ymax = int(ymax * scale_y)
                    
                    node_obj  = xml_doc.createElement("object")
                    node_name = xml_doc.createElement("name")
                    node_name.appendChild(xml_doc.createTextNode(label))
                    node_obj.appendChild(node_name)
                    node_diff = xml_doc.createElement("difficult")
                    node_diff.appendChild(xml_doc.createTextNode(str(0)))
                    node_obj.appendChild(node_diff)
                    node_box  = xml_doc.createElement("bndbox")
                    node_xmin = xml_doc.createElement("xmin")
                    node_xmin.appendChild(xml_doc.createTextNode(str(xmin)))
                    node_box.appendChild(node_xmin)
                    node_ymin = xml_doc.createElement("ymin")
                    node_ymin.appendChild(xml_doc.createTextNode(str(ymin)))
                    node_box.appendChild(node_ymin)
                    node_xmax = xml_doc.createElement("xmax")
                    node_xmax.appendChild(xml_doc.createTextNode(str(xmax)))
                    node_box.appendChild(node_xmax)
                    node_ymax = xml_doc.createElement("ymax")
                    node_ymax.appendChild(xml_doc.createTextNode(str(ymax)))
                    node_box.appendChild(node_ymax)
                    node_obj.appendChild(node_box)
                    root.appendChild(node_obj)

                    if label not in self.defect_info:
                        self.defect_info[label] = []
                    self.defect_info[label].append([xmin, ymin, xmax, ymax])
            
            # 保存xml文件
            with open(osp.join(xml_dir, img_name_part + ".xml"), 'w') as fxml:
                xml_doc.writexml(fxml, indent='\t', addindent='\t', newl='\n', encoding="utf-8")


class EasyData2VOC(X2VOC):
    """将使用EasyData标注的分割数据集转换为VOC数据集。
    """

    def __init__(self):
        pass

    def json2xml(self, image_dir, json_dir, xml_dir):
        import xml.dom.minidom as minidom
        for img_name in os.listdir(image_dir):
            img_name_part = osp.splitext(img_name)[0]
            json_file = osp.join(json_dir, img_name_part + ".json")
            if not osp.exists(json_file):
                os.remove(osp.join(image_dir, img_name))
                continue
            xml_doc = minidom.Document()
            root = xml_doc.createElement("annotation")
            xml_doc.appendChild(root)
            node_folder = xml_doc.createElement("folder")
            node_folder.appendChild(xml_doc.createTextNode("JPEGImages"))
            root.appendChild(node_folder)
            node_filename = xml_doc.createElement("filename")
            node_filename.appendChild(xml_doc.createTextNode(img_name))
            root.appendChild(node_filename)
            img = cv2.imread(osp.join(image_dir, img_name))
            h = img.shape[0]
            w = img.shape[1]
            node_size = xml_doc.createElement("size")
            node_width = xml_doc.createElement("width")
            node_width.appendChild(xml_doc.createTextNode(str(w)))
            node_size.appendChild(node_width)
            node_height = xml_doc.createElement("height")
            node_height.appendChild(xml_doc.createTextNode(str(h)))
            node_size.appendChild(node_height)
            node_depth = xml_doc.createElement("depth")
            node_depth.appendChild(xml_doc.createTextNode(str(3)))
            node_size.appendChild(node_depth)
            root.appendChild(node_size)
            with open(json_file, mode="r", \
                              encoding=get_encoding(json_file)) as j:
                json_info = json.load(j)
                for shape in json_info["labels"]:
                    label = shape["name"]
                    xmin = shape["x1"]
                    ymin = shape["y1"]
                    xmax = shape["x2"]
                    ymax = shape["y2"]
                    node_obj = xml_doc.createElement("object")
                    node_name = xml_doc.createElement("name")
                    node_name.appendChild(xml_doc.createTextNode(label))
                    node_obj.appendChild(node_name)
                    node_diff = xml_doc.createElement("difficult")
                    node_diff.appendChild(xml_doc.createTextNode(str(0)))
                    node_obj.appendChild(node_diff)
                    node_box = xml_doc.createElement("bndbox")
                    node_xmin = xml_doc.createElement("xmin")
                    node_xmin.appendChild(xml_doc.createTextNode(str(xmin)))
                    node_box.appendChild(node_xmin)
                    node_ymin = xml_doc.createElement("ymin")
                    node_ymin.appendChild(xml_doc.createTextNode(str(ymin)))
                    node_box.appendChild(node_ymin)
                    node_xmax = xml_doc.createElement("xmax")
                    node_xmax.appendChild(xml_doc.createTextNode(str(xmax)))
                    node_box.appendChild(node_xmax)
                    node_ymax = xml_doc.createElement("ymax")
                    node_ymax.appendChild(xml_doc.createTextNode(str(ymax)))
                    node_box.appendChild(node_ymax)
                    node_obj.appendChild(node_box)
                    root.appendChild(node_obj)
            with open(osp.join(xml_dir, img_name_part + ".xml"), 'w') as fxml:
                xml_doc.writexml(
                    fxml,
                    indent='\t',
                    addindent='\t',
                    newl='\n',
                    encoding="utf-8")
