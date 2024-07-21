# 输入数据集的图片路径和标注文件路径，输出VOC格式的数据集
# 标签的格式如下 
# 0 0.033205 0.855468 0.046872 0.089844   #目标1 类别 x y w h  全部转化为0-1之间的值
# 0 0.141601 0.734376 0.033204 0.062500   #目标2 类别 x y w h
# 0 0.681643 0.402344 0.062502 0.039064   #目标3 类别 x y w h
# 0 0.961916 0.426760 0.060546 0.037108   #目标4 类别 x y w h

# 如果标签文件内部为空，代表没有目标，是正常样本

# 生成的voc xml文件格式如下
# <annotation>
#     <folder>images</folder>
#     <filename>000001.jpg</filename>
#     <size>
#         <width>1920</width>
#         <height>1080</height>
#         <depth>3</depth>
#     </size>
#     <object>
#         <name>0</name>
#         <difficult>0</difficult>
#         <bndbox>
#             <xmin>0</xmin>
#             <ymin>0</ymin>
#             <xmax>0</xmax>
#             <ymax>0</ymax>
#         </bndbox>
#     </object>
#     <object>
#         <name>0</name>
#         <difficult>0</difficult>
#         <bndbox>
#             <xmin>0</xmin>
#             <ymin>0</ymin>
#             <xmax>0</xmax>
#             <ymax>0</ymax>
#         </bndbox>
#     </object>
# # </annotation> 


import os
import os.path as osp
import random
import cv2
import json
import numpy as np

import xml.etree.ElementTree as ET


def get_label_info():
    # 0- bite
    # 1- circuit
    # 2- Short

    label_info = dict()
    label_info['0'] = 'Mouse_bite'
    label_info['1'] = 'Open_circuit'
    label_info['2'] = 'Short'
    label_info['3'] = 'Spur'
    label_info['4'] = 'Spurious_copper'

    return label_info

def transform_annotation_xml(root_image_path, root_label_path, output_path):
    
    # 获取image_path中包含的所有图片
    image_path_list = []
    for root, dirs, files in os.walk(root_image_path):
        for file in files:
            if file.endswith('.jpg') or file.endswith('.png') or file.endswith('.jpeg'):
                image_path_list.append(os.path.join(root, file))

    # 获取label_path中包含的所有标签文件
    label_path_list = []
    for root, dirs, files in os.walk(root_label_path):
        for file in files:
            if file.endswith('.txt'):
                label_path_list.append(os.path.join(root, file))

    
    label_info = get_label_info()
    count_num = 0

    
    # 生成VOC格式的数据集
    for image_path in image_path_list:
        # 判断是否存在对应的标签文件
        label_path = image_path.replace(root_image_path, root_label_path)
        # 后缀名替换为txt
        label_path = label_path.replace('.png', '.txt')
        if label_path not in label_path_list:
            print('标签文件不存在：', label_path)
            continue

        # 读取图片
        img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), -1)
        h, w, c = img.shape
        count_num += 1

        # 读取标签文件
        with open(label_path, 'r') as f:
            lines          = f.readlines()
            base_name      = os.path.basename(image_path).replace('.png', '.xml')
            xml_label_path = os.path.join(output_path, base_name)
            xml_file = open(xml_label_path, 'w')
            xml_file.write('<annotation>\n')
            xml_file.write('    <folder>images</folder>\n')
            xml_file.write('    <filename>' + image_path.split('/')[-1] + '</filename>\n')
            xml_file.write('    <size>\n')
            xml_file.write('        <width>' + str(w) + '</width>\n')
            xml_file.write('        <height>' + str(h) + '</height>\n')
            xml_file.write('        <depth>' + str(c) + '</depth>\n')
            xml_file.write('    </size>\n')
            for line in lines:
                line       = line.strip().split(' ')
                label      = line[0]
                label_name = label_info[label]
                x          = float(line[1]) * w
                y          = float(line[2]) * h
                width      = float(line[3]) * w
                height     = float(line[4]) * h
                xml_file.write('    <object>\n')
                xml_file.write('        <name>' + label_name + '</name>\n')
                xml_file.write('        <difficult>0</difficult>\n')
                xml_file.write('        <bndbox>\n')
                xml_file.write('            <xmin>' + str(x) + '</xmin>\n')
                xml_file.write('            <ymin>' + str(y) + '</ymin>\n')
                xml_file.write('            <xmax>' + str(x + width) + '</xmax>\n')
                xml_file.write('            <ymax>' + str(y + height) + '</ymax>\n')
                xml_file.write('        </bndbox>\n')
                xml_file.write('    </object>\n')
            xml_file.write('</annotation>\n')
            xml_file.close()

        if count_num % 20 == 0:
            print('正在处理：', count_num)
        

def transform_annotation_json(root_image_path, root_label_path, output_path):
        
        # 获取image_path中包含的所有图片
        image_path_list = []
        for root, dirs, files in os.walk(root_image_path):
            for file in files:
                if file.endswith('.jpg') or file.endswith('.png') or file.endswith('.jpeg'):
                    image_path_list.append(os.path.join(root, file))
    
        # 获取label_path中包含的所有标签文件
        label_path_list = []
        for root, dirs, files in os.walk(root_label_path):
            for file in files:
                if file.endswith('.txt'):
                    label_path_list.append(os.path.join(root, file))
    
        
        label_info = get_label_info()
        count_num = 0
        
        # 生成VOC格式的数据集
        for image_path in image_path_list:
            # 判断是否存在对应的标签文件
            label_path = image_path.replace(root_image_path, root_label_path)
            # 后缀名替换为txt
            label_path = label_path.replace('.png', '.txt')
            if label_path not in label_path_list:
                print('标签文件不存在：', label_path)
                continue
    
            # 读取图片
            img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), -1)
            h, w, c = img.shape
            count_num += 1

            json_data = {
                "flags": {},
                "imageData": None,
                "imageHeight": None,
                "imageWidth": None,
                "shapes": [],
                "version": "SmartIBW_2.02.01"
            }
    
            # 读取标签文件
            with open(label_path, 'r') as f:
                json_data["imagePath"]    = "/" + os.path.basename(image_path)
                json_data["imageHeight"]  = h
                json_data["imageWidth"]   = w
                json_data["imageData"]    = None
                json_data["flags"]        = {}
                
                lines = f.readlines()
                for line in lines:
                    line       = line.strip().split(' ')
                    label      = line[0]
                    label_name = label_info[label]
                    x          = float(line[1]) * w
                    y          = float(line[2]) * h
                    width      = float(line[3]) * w
                    height     = float(line[4]) * h
                    shape_data = {
                        "label": label_name,
                        "line_color": None,
                        "fill_color": None,
                        "points": [[x, y], [x + width, y + height]],
                        "shape_type": "rectangle",
                        "flags": {}
                    }
                    json_data["shapes"].append(shape_data)

                base_name       = os.path.basename(image_path).replace('.png', '.json')
                json_label_path = os.path.join(output_path, base_name)
                with open(json_label_path, "w") as f:
                    json.dump(json_data, f, indent=4)


            if count_num % 20 == 0:
                print('正在处理：', count_num)


# 获取train val list
def get_dataset_list(image_path, save_dir):
    # 获取image_path中包含的所有图片
    image_path_list = []
    for root, dirs, files in os.walk(image_path):
        for file in files:
            if file.endswith('.jpg') or file.endswith('.png') or file.endswith('.jpeg'):
                image_path_list.append(os.path.join(root, file))

    image_anno_list = []
    for image_path in image_path_list:
        base_image_name = os.path.basename(image_path)
        base_label_name = base_image_name.replace('.png', '.xml')
        image_anno_list.append([base_image_name, base_label_name])
        
        # train.txt
    with open(osp.join(save_dir, 'dataset.txt'), mode='w', encoding='utf-8') as f:
        for x in image_anno_list:
            file  = osp.join("02_JPEGImages", x[0])
            label = osp.join("03_Labels/xml", x[1])
            f.write('{} {}\n'.format(file, label))
        

if __name__ == '__main__':
    root_paht   = r"D:\Dataset\AI质检2024\裁剪图片\dataset_crop_good - 副本"
    image_path  = os.path.join(root_paht, 'images/val') 
    label_path  = os.path.join(root_paht, 'labels/val')
    output_path = os.path.join(root_paht, 'xml/val')
    #transform_annotation_xml(image_path, label_path, output_path)
    output_path = os.path.join(root_paht, 'json/val') 
    #transform_annotation_json(image_path, label_path, output_path)
    
    datalistname = os.path.join(root_paht, 'val')
    get_dataset_list(image_path, datalistname)
    
    print('转换完成')