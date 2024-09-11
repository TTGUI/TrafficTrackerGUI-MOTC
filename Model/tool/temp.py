# 設定根目錄
root_folder = r'E:\Traffic\Block18'

# 儲存符合條件的文件檔案路徑
input_files = []
processed_files = []
import os

# 更換檔名
for foldername, subfolders, filenames in os.walk(root_folder):
    for filename in filenames:
        if filename.endswith('_OR_stab_reshape.avi'):
            # 取得原始檔案的完整路徑
            old_file_path = os.path.join(foldername, filename)
            
            # 新檔案名稱
            new_filename = filename.replace('_OR_stab_reshape.avi', '_stab.avi')
            
            # 取得新的檔案完整路徑
            new_file_path = os.path.join(foldername, new_filename)
            
            # 進行檔案改名
            os.rename(old_file_path, new_file_path)
            
            print(f"檔案已更名: {old_file_path} -> {new_file_path}")