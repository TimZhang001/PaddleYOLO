import os
import re

from pypinyin import lazy_pinyin

# 将文件名中的 中文 替换为 拼音
def replace_chinese_with_pinyin(folder_path):
    total_num = 0
    
    # 遍历文件夹及其子目录中的所有文件
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            # 检查文件名是否包含中文
            if re.search("[\u4e00-\u9fa5]", filename):
                # 获取文件名中的中文部分并转换为拼音
                chinese_part = re.findall("[\u4e00-\u9fa5]+", filename)[0]
                pinyin_part = ''.join(lazy_pinyin(chinese_part))
                # 将中文替换为拼音
                new_filename = filename.replace(chinese_part, pinyin_part)
                # 构建文件的完整路径
                old_path = os.path.join(root, filename)
                new_path = os.path.join(root, new_filename)
                
                # 重命名文件
                os.rename(old_path, new_path)
                print(f"Renamed: {old_path} -> {new_path}")

                total_num += 1
    print(f"Total number of files renamed: {total_num}")

# 将文件名中的 - 替换为 _
def replace_dash_with_underscore(folder_path):
    
    total_num = 0
    # 遍历文件夹及其子目录中的所有文件
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            # 检查文件名是否包含 ' '
            if ' ' in filename:
                # 将 - 替换为 _
                new_filename = filename.replace(' ', '_')
                # 构建文件的完整路径
                old_path = os.path.join(root, filename)
                new_path = os.path.join(root, new_filename)
                # 重命名文件
                os.rename(old_path, new_path)
                print(f"Renamed: {old_path} -> {new_path}")

                total_num += 1
    print(f"Total number of files renamed: {total_num}")

# 指定要处理的文件夹路径
folder_path = "/raid/zhangss/dataset/Detection/Mura/TrueMuraDefect_V1.0.4_20240411/holeMura/data/"

# 调用函数进行处理
replace_chinese_with_pinyin(folder_path)
replace_dash_with_underscore(folder_path)
