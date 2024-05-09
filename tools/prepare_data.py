from label_tools.copy2dataset import Copy2Dataset
from label_tools.x2voc import LabelMe2VOC, X2VOC
from label_tools.x2coco import X2COCO
from label_tools.dataset_split.voc_split import split_voc_dataset

if __name__ == "__main__":
    
    project_path  = "/raid/zhangss/dataset/Detection/Mura_Project_AD" #Mura_Project_Large Mura_Project_Small Mura_Project_AD
    project_types = ["Alls"] # "Alls"
    #project_types = ["Commons"]
    target_size   = 1280 if "Large" in project_path  or "AD" in project_path else  512
    
    # 1. 将原始的数据集拷贝到指定的目录下，形成项目数据集
    if 0:
        copy2dataset = Copy2Dataset(project_path)
        copy2dataset.convert2dataset(project_types)

    # 2. 将json文件转化为xml文件 ------------------------------------------------------   
    if 1:
        json2voc      = LabelMe2VOC(target_size=target_size)
        for project_type in project_types:
            image_dir = "{}/{}/02_JPEGImages".format(project_path, project_type)
            json_dir  = "{}/{}/03_Labels/json".format(project_path, project_type)
            xml_dir   = "{}/{}/03_Labels/xml".format(project_path, project_type)
            json2voc.json2xml(image_dir, json_dir, xml_dir, project_type)
            json2voc.defect_statistic(image_dir, json_dir)
            print("Convert {} Done!".format(project_type))

        # 将数据集划分为训练集(0.8)、验证集(0.1)和测试集(0.1) ----------------------------------------------
        for project_type in project_types:
            dataset_dir  = "{}/{}".format(project_path, project_type)
            val_value    = 0.15
            test_value   = 0.0
            save_dir     = "{}/{}".format(project_path, project_type)
            split_voc_dataset(dataset_dir, val_value, test_value, save_dir)
            print("Split {} Done!".format(project_type))
    
