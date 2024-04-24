import os
import json
from PIL import Image

def create_empty_json(image_folder, json_path):
    # 获取图像文件列表
    image_files = os.listdir(image_folder)
    
    # 初始化 JSON 数据
    json_data = {
        "flags": {},
        "imageData": None,
        "imageHeight": None,
        "imageWidth": None,
        "shapes": [],
        "version": "SmartIBW_2.02.01"
    }
    
    # 遍历图像文件列表
    for image_file in image_files:
        # 构造图像路径
        image_path = os.path.join(image_folder, image_file)
        
        # 构造图像名称
        image_name = os.path.splitext(image_file)[0]
        
        # 打开图像并获取其大小
        with Image.open(image_path) as img:
            width, height = img.size
        
        # 构造图像对应的 JSON 数据
        shape_data = {}
        
        # 构造完整的 JSON 数据
        json_data["imagePath"] = "/" + image_file
        json_data["imageHeight"] = height
        json_data["imageWidth"] = width
        json_data["shapes"] = [shape_data]
        
        # 写入 JSON 文件
        with open(os.path.join(json_path, image_name + ".json"), "w") as f:
            json.dump(json_data, f, indent=4)

# 示例用法
image_folder = "/raid/zhangss/dataset/Detection/Mura/TrueMuraDefect_V1.0.4_20240411/OK/image/"
json_path = "/raid/zhangss/dataset/Detection/Mura/TrueMuraDefect_V1.0.4_20240411/OK/data/"
create_empty_json(image_folder, json_path)
