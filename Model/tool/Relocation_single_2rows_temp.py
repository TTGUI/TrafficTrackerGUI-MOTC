import os

# 設定根目錄
root_folder = r'E:\Traffic\Block18'

# 儲存符合條件的文件檔案路徑
input_files = []
processed_files = []

# 更換檔名
for foldername, subfolders, filenames in os.walk(root_folder):
    for filename in filenames:
        if filename.endswith('_8cls.txt'):
            # 取得原始檔案的完整路徑
            old_file_path = os.path.join(foldername, filename)
            
            # 新檔案名稱
            new_filename = filename.replace('_8cls.txt', '_reshape_8cls.txt')
            
            # 取得新的檔案完整路徑
            new_file_path = os.path.join(foldername, new_filename)
            
            # 進行檔案改名
            os.rename(old_file_path, new_file_path)
            
            print(f"檔案已更名: {old_file_path} -> {new_file_path}")

# 遍歷根目錄底下的所有檔案
for foldername, subfolders, filenames in os.walk(root_folder):
    for filename in filenames:
        if filename.endswith('_reshape_8cls.txt'):
            input_path = os.path.join(foldername, filename)
            input_files.append(input_path)

# 列印所有符合條件的文件名稱並附加序號
print("找到以下符合條件的文件:")
for idx, file in enumerate(input_files):
    print(f"{idx + 1}: {file}")

total_files = len(input_files)

# 處理每一個符合條件的文件
for file_idx, input_file_path in enumerate(input_files):
    # 設定輸出檔案名稱
    output_file_path = input_file_path.replace('_reshape_8cls.txt', '_8cls.txt')

    print(f"\n開始處理文件 {file_idx + 1}/{total_files}: {input_file_path}")

    # 讀取並處理每行數據
    with open(input_file_path, 'r') as infile, open(output_file_path, 'w') as outfile:
        total_lines = sum(1 for line in infile)
        infile.seek(0)  # 重置檔案讀取位置
        line_idx = 0

        for line in infile:
            fields = line.split()

            # 檢查行的欄位數量，確保至少有2個欄位以後的數據
            if len(fields) < 11:
                outfile.write(line)
                continue

            # 遍歷每組資料並進行處理
            data_start_index = 1  
            while data_start_index + 9 < len(fields):
                f1, f2 = int(fields[data_start_index]), float(fields[data_start_index + 1])
                x1, y1 = int(fields[data_start_index + 2]), int(fields[data_start_index + 3])
                x2, y2 = int(fields[data_start_index + 4]), int(fields[data_start_index + 5])
                x3, y3 = int(fields[data_start_index + 6]), int(fields[data_start_index + 7])
                x4, y4 = int(fields[data_start_index + 8]), int(fields[data_start_index + 9])

                # 設定座標變換參數
                Tx, Ty, Th = 300, 500, 960  # Top road region
                Bx, By = 1920, 500  # Bottom road region

                if y1 < Th:
                    x1 += Tx
                    x2 += Tx
                    x3 += Tx
                    x4 += Tx
                    y1 += Ty
                    y2 += Ty
                    y3 += Ty
                    y4 += Ty
                else:
                    x1 += Bx
                    x2 += Bx
                    x3 += Bx
                    x4 += Bx
                    y1 += By - Th
                    y2 += By - Th
                    y3 += By - Th
                    y4 += By - Th               

                # 更新行的數據
                fields[data_start_index:data_start_index + 10] = [f1, f2, x1, y1, x2, y2, x3, y3, x4, y4]
                
                # 移動到下一組資料
                data_start_index += 10

            # 將更新後的行寫入輸出文件
            outfile.write(' '.join(map(str, fields)) + '\n')
            
            # 更新進度
            line_idx += 1
            print(f"處理進度: {line_idx}/{total_lines} 行", end='\r')

    print(f"\n成功處理文件: {output_file_path}")
    processed_files.append(output_file_path)

# 總結
print("\n所有文件處理完畢！")
print("成功處理的文件清單:")
for idx, file in enumerate(processed_files):
    print(f"{idx + 1}: {file}")
