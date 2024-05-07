import os
from .defect_type import MuraCommList, MuraLineList, MuraAllList

class Copy2Dataset():
    def __init__(self, project_path):
        self.comm_list      = MuraCommList
        self.line_list      = MuraLineList
        
        # 模拟数据集的路径
        self.sim_data_list  = (#"MonoMuraGeneralDataSet_V1.0", \
                               #"MonoMuraGeneralDataSet_V1.1_20221010",\
                               #"ColorGeneralDataSet_L10_V1.0_20240407", \
                               #"ColorGeneralDataSet_L128_V1.0_20240407",
                               #"ColorGeneralDataSet_Total_V1.0_20240407",
                               )
        
        # 真实数据集的路径
        self.true_data_list = (#"TrueMuraDefect_V1.0.0_20220926", \
                               #"TrueMuraDefect_V1.0.1_20230616", \
                               #"TrueMuraDefect_V1.0.2_20240112", \
                               #"TrueMuraDefect_V1.0.4_20240411", \
                               #"TrueMuraDefect_V1.0.3_20240411",
                               "ColorMuraDefect_Project_V1.0.0_20240429",
                               )
        
        # 背景的类型
        self.back_data_list = ("ideal", "particle", "widthBorder_OLED", "widthBorder", \
                               "withBorder_LCD", "withBorder", "withHole", "withRC", "withDefect") # "withMorie" 
        
        # 数据集的根目录
        self.dataset_path   = "/raid/zhangss/dataset/Detection/Mura"
        
        # 项目路径
        self.project_path   = project_path

    def get_dirs_list(self, path):
        """
        Get all directories in a path.
        """
        # 如果路径不存在，直接continue
        if not os.path.exists(path):
            return []
        
        return [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]

    def get_files_list(self, path):
        """
        Get all files in a path.
        """
        # 如果路径不存在，直接continue
        if not os.path.exists(path):
            return []
        
        return [name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))]

    def check_str_in_list(self, str, list):
        """
        Check if a string is in a list.
        """  
        for sub_str in list:
            if sub_str in str:
                return True
        return False

    def copy_files_2_project(self, file_path, file_type, project_type):
        src_path = os.path.join(file_path, file_type)
        dst_path = os.path.join(self.project_path, project_type)
        
        # 创建文件夹
        os.makedirs(os.path.join(dst_path, "01_Annotations"), exist_ok=True)
        os.makedirs(os.path.join(dst_path, "02_JPEGImages"),  exist_ok=True)
        os.makedirs(os.path.join(dst_path, "03_Labels", "json"), exist_ok=True)
        os.makedirs(os.path.join(dst_path, "03_Labels", "xml"),  exist_ok=True)

        # 进行文件的拷贝
        
        # 拷贝annotation文件--------------------------------------------------------------------
        cur_src_path = os.path.join(src_path, "masks")
        files_list   = self.get_files_list(cur_src_path)
        if len(files_list) == 0:
            print("No annotation files in {}".format(cur_src_path))
        else:
            os.system('cp {}/masks/*.png {}/01_Annotations'.format(src_path, dst_path))

        # 拷贝image文件--------------------------------------------------------------------
        cur_src_path = os.path.join(src_path, "images")
        files_list   = self.get_files_list(cur_src_path)
        if len(files_list) == 0:
            print("No image files in {}".format(cur_src_path))
        else:
            if "tif" in files_list[0] or 1:
                os.system('cp {}/images/*.tif      {}/02_JPEGImages'.format(src_path,  dst_path))
            
            if "bmp" in files_list[0] or 1:
                os.system('cp {}/images/*.bmp      {}/02_JPEGImages'.format(src_path,  dst_path))

        # 拷贝json文件--------------------------------------------------------------------
        cur_src_path = os.path.join(src_path, "annotations")
        files_list   = self.get_files_list(cur_src_path)
        if len(files_list) == 0:
            print("No json files in {}".format(cur_src_path))
        else:
            os.system('cp {}/annotations/*.json      {}/03_Labels/json'.format(src_path, dst_path))
 
    def convert2dataset(self, project_types = ["Alls"]):
        
        for project_type in project_types:
            
            # 删除self.project_path目录下的所有文件夹和文件
            cur_project_path = os.path.join(self.project_path, project_type)
            os.system('rm -rf {}/*'.format(cur_project_path))

            # -----------------模拟数据集-------------------------------------------------------    
            for file_sim in self.sim_data_list:
                cur_file_sim = os.path.join(self.dataset_path, file_sim)
                for file_back in self.back_data_list:
                    cur_file_sim_back = os.path.join(cur_file_sim, file_back)     
                        
                    # 进行数据集的拷贝
                    data_list = self.get_dirs_list(cur_file_sim_back)
                    for NAME in data_list:
                        if project_type == "Commons":
                            if self.check_str_in_list(NAME, self.comm_list):
                                self.copy_files_2_project(cur_file_sim_back, NAME, "Commons")

                        if project_type == "Lines":
                            if self.check_str_in_list(NAME, self.line_list):
                                self.copy_files_2_project(cur_file_sim_back, NAME, "Lines")

                        if project_type == "Alls":        
                            self.copy_files_2_project(cur_file_sim_back, NAME, "Alls") 

                        
            # -----------------真实数据集-------------------------------------------------------
            for file_true in self.true_data_list:
                cur_file_true = os.path.join(self.dataset_path, file_true)   
                    
                # 进行数据集的拷贝
                data_list = self.get_dirs_list(cur_file_true)
                for NAME in data_list:
                    if project_type == "Commons":
                        if self.check_str_in_list(NAME, self.comm_list):
                            self.copy_files_2_project(cur_file_true, NAME, "Commons")

                    if project_type == "Lines":
                        if self.check_str_in_list(NAME, self.line_list):
                            self.copy_files_2_project(cur_file_true, NAME, "Lines")

                    if project_type == "Alls":        
                        self.copy_files_2_project(cur_file_true, NAME, "Alls") 


if __name__ == "__main__":
    copy2dataset = Copy2Dataset()
    copy2dataset.convert2dataset()
    print("Copy Done!")