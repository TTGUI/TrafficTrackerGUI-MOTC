import os

def clean_directory(base_dir, base_extension="png"):
    # 建立一個集合來儲存基準檔名
    base_files = set()

    # 歷遍資料夾，將所有基準副檔名的檔案儲存到集合中（不包括副檔名）
    for file_name in os.listdir(base_dir):
        if file_name.endswith(f".{base_extension}"):
            base_name = os.path.splitext(file_name)[0]
            base_files.add(base_name)

    # 再次歷遍資料夾，檢查其他檔案是否存在基準檔案中
    for file_name in os.listdir(base_dir):
        file_path = os.path.join(base_dir, file_name)
        # 跳過資料夾
        if os.path.isdir(file_path):
            continue
        
        # 取得檔名不含副檔名的部分
        base_name = os.path.splitext(file_name)[0]
        
        # 如果檔案的基準名稱不在集合中，刪除該檔案
        if base_name not in base_files:
            os.remove(file_path)
            print(f"刪除檔案: {file_path}")

# 使用範例
directory_path = r"D:\segment-anything-2\notebooks\videos\IMG_0028_A"  # 設定資料夾路徑
clean_directory(directory_path, base_extension="png")
