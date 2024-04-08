import os

class Copy2Dataset():
    def __init__(self):
        self.comm_list      = ("Blob",  "Ring",  "Zara",   "Twill",   "HShort", "VShort", "Gap", "Dirty")
        self.line_list      = ("HLine", "VLine", "HBlock", "VBlock",  "HSplit", "VSplit", "MultiLine")
        
        # 模拟数据集的路径
        self.sim_data_list  = ("MonoMuraGeneralDataSet_V1.0", \
                               "MonoMuraGeneralDataSet_V1.1_20221010",\
                               "ColorGeneralDataSet_L10_V1.0_20240407", )
        
        # 真实数据集的路径
        self.true_data_list = ("TrueMuraDefect_V1.0.0_20220926", \
                               "TrueMuraDefect_V1.0.1_20230616", \
                               "TrueMuraDefect_V1.0.2_20240112")
        
        # 背景的类型
        self.back_data_list = ("ideal", "particle", "widthBorder_OLED", \
                               "withBorder_LCD", "withDefect", "withMorie")     
        
        # 数据集的根目录
        self.dataset_path   = "/raid/zhangss/dataset/Detection/Mura/"
        
        # 项目路径
        self.project_path   = "/raid/zhangss/dataset/Detection/Mura_Project/"

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
        cur_src_path = os.path.join(src_path, "annotation")
        files_list   = self.get_files_list(cur_src_path)
        if len(files_list) == 0:
            print("No annotation files in {}".format(cur_src_path))
        else:
            os.system('cp {}/annotation/*.png {}/01_Annotations'.format(src_path, dst_path))

        # 拷贝image文件--------------------------------------------------------------------
        cur_src_path = os.path.join(src_path, "image")
        files_list   = self.get_files_list(cur_src_path)
        if len(files_list) == 0:
            print("No image files in {}".format(cur_src_path))
        else:
            os.system('cp {}/image/*.tif      {}/02_JPEGImages'.format(src_path,  dst_path))

        # 拷贝json文件--------------------------------------------------------------------
        cur_src_path = os.path.join(src_path, "data")
        files_list   = self.get_files_list(cur_src_path)
        if len(files_list) == 0:
            print("No json files in {}".format(cur_src_path))
        else:
            os.system('cp {}/data/*.json      {}/03_Labels/json'.format(src_path, dst_path))
 
    def convert2dataset(self):
        
        # 删除self.project_path目录下的所有文件夹和文件
        os.system('rm -rf {}/*'.format(self.project_path))

        # -----------------模拟数据集-------------------------------------------------------    
        for file_sim in self.sim_data_list:
            cur_file_sim = os.path.join(self.dataset_path, file_sim)
            for file_back in self.back_data_list:
                cur_file_sim_back = os.path.join(cur_file_sim, file_back)     
                    
                # 进行数据集的拷贝
                data_list = self.get_dirs_list(cur_file_sim_back)
                for NAME in data_list:
                    if self.check_str_in_list(NAME, self.comm_list):
                        self.copy_files_2_project(cur_file_sim_back, NAME, "Commons")

                    if self.check_str_in_list(NAME, self.line_list):
                        self.copy_files_2_project(cur_file_sim_back, NAME, "Lines")
                
                    self.copy_files_2_project(cur_file_sim_back, NAME, "Alls") 

                    
        # -----------------真实数据集-------------------------------------------------------
        for file_true in self.true_data_list:
            cur_file_true = os.path.join(self.dataset_path, file_true)   
                
            # 进行数据集的拷贝
            data_list = self.get_dirs_list(cur_file_true)
            for NAME in data_list:
                if self.check_str_in_list(NAME, self.comm_list):
                    self.copy_files_2_project(cur_file_true, NAME, "Commons")

                if self.check_str_in_list(NAME, self.line_list):
                    self.copy_files_2_project(cur_file_true, NAME, "Lines")

                self.copy_files_2_project(cur_file_true, NAME, "Alls") 


if __name__ == "__main__":
    copy2dataset = Copy2Dataset()
    copy2dataset.convert2dataset()
    print("Copy Done!")