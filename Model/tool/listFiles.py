import os

def list_files_and_dirs(path="."):
    """
    列出給定目錄下的所有子目錄以及相對應子目錄下的檔案
    """
    def display_directory(root, files, dirs, prefix=''):
        if root != path:
            print(f'{prefix}├─ [目錄] {os.path.basename(root)}/')
            prefix += "│   "

        for i, f in enumerate(files):
            char = '├' if i != len(files) - 1 or dirs else '└'
            print(f'{prefix}{char}─ [檔案] {f}')

        for i, d in enumerate(dirs):
            new_root = os.path.join(root, d)
            new_dirs = [sub_dir for sub_dir in os.listdir(new_root) if os.path.isdir(os.path.join(new_root, sub_dir))]
            new_files = [sub_file for sub_file in os.listdir(new_root) if os.path.isfile(os.path.join(new_root, sub_file))]
            
            if i == len(dirs) - 1:
                new_prefix = prefix + '    '
            else:
                new_prefix = prefix + '│   '
            display_directory(new_root, new_files, new_dirs, new_prefix)

    root, dirs, files = next(os.walk(path))
    display_directory(root, files, dirs)

if __name__ == "__main__":
    path = input("請輸入要查詢的目錄路徑: ")
    if os.path.exists(path):
        list_files_and_dirs(path)
    else:
        print("錯誤: 指定的路徑不存在!")
