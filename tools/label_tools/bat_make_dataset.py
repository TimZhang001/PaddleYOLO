import os


def get_dirs_list(path):
    """
    Get all directories in a path.
    """
    return [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]

def check_str_in_list(str, list):
    """
    Check if a string is in a list.
    """  
    for sub_str in list:
        if sub_str in str:
            return True
    return False



if __name__ == "__main__":
    comm_list = "Blob",  "Ring",  "Zara",   "Twill",   "HShort", "VShort", "Gap"
    line_list = "HLine", "VLine", "HBlock", "VBlock",  "HSplit", "VSplit"
    file_list_all = "MonoMuraGeneralDataSet_V1.0/ideal", \
                    "MonoMuraGeneralDataSet_V1.0/particle", \
                    "MonoMuraGeneralDataSet_V1.0/widthBorder_OLED", \
                    "MonoMuraGeneralDataSet_V1.0/withBorder_LCD",\
                    "MonoMuraGeneralDataSet_V1.0/withMorie",    

    base_path = "/raid/zhangss/dataset/Detection/Mura/"
    
    # -----------------ideal-------------------------------------------------------
    for file_list in file_list_all:
        file_list = os.path.join(base_path, file_list)
        data_list = get_dirs_list(file_list)
        for NAME in data_list:
            if check_str_in_list(NAME, comm_list):
                os.system('cp {}/{}/annotation/*.png ../04_DataSet_Com/01_Annotations'.format(file_list, NAME))
                os.system('cp {}/{}/image/*.tif      ../04_DataSet_Com/02_JPEGImages'.format(file_list,  NAME))
                os.system('cp {}/{}/data/*.json      ../04_DataSet_Com/03_Labels/json'.format(file_list, NAME))

            if check_str_in_list(NAME, line_list):
                os.system('cp {}/{}/annotation/*.png ../04_DataSet_Line/01_Annotations'.format(file_list, NAME))
                os.system('cp {}/{}/image/*.tif      ../04_DataSet_Line/02_JPEGImages'.format(file_list,  NAME))
                os.system('cp {}/{}/data/*.json      ../04_DataSet_Line/03_Labels/json'.format(file_list, NAME))


    # -----------------trueDefect Comm-------------------------------------------------------
    data_list = "Blob", "Gap", "Particle", "VShort"
    for NAME in data_list:
        os.system('cp trueDefect/{}/annotation/*.png ../04_DataSet_Com/01_Annotations'.format(NAME))
        os.system('cp trueDefect/{}/image/*.tif      ../04_DataSet_Com/02_JPEGImages'.format(NAME))
        os.system('cp trueDefect/{}/data/*.json      ../04_DataSet_Com/03_Labels/json'.format(NAME))

    # -----------------trueDefect Line-------------------------------------------------------
    data_list = "HLine", "Particle", "VLine", "VSplit"
    for NAME in data_list:
        os.system('cp trueDefect/{}/annotation/*.png ../04_DataSet_Line/01_Annotations'.format(NAME))
        os.system('cp trueDefect/{}/image/*.tif      ../04_DataSet_Line/02_JPEGImages'.format(NAME))
        os.system('cp trueDefect/{}/data/*.json      ../04_DataSet_Line/03_Labels/json'.format(NAME))