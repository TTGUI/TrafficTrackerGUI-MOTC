import os
import cv2
import numpy as np
import csv
def div2(root_folder):
    # 設定根目錄


    # 設定處理檔案的ID計數
    id = 1

    # 處理每個符合條件的檔案
    for foldername, subfolders, filenames in os.walk(root_folder):
        for _, filename in enumerate(filenames):
            if filename.endswith('.csv'):
                # 取得原始檔案的完整路徑，處理中文路徑
                input_file = os.path.join(foldername, filename)
                input_file = os.path.normpath(input_file)
                print(id, "處理檔案:", input_file)
                id += 1

                # 新檔案名稱
                new_filename = filename.replace('.csv', '_div2.csv')
                output_file = os.path.join(foldername, new_filename)
                output_file = os.path.normpath(output_file)

                # 打開輸入檔案進行讀取
                with open(input_file, newline='', encoding='utf-8') as csvfile:
                    csvreader = csv.reader(csvfile)
                    
                    # 打開輸出檔案進行寫入
                    with open(output_file, 'w', newline='', encoding='utf-8') as csvoutfile:
                        csvwriter = csv.writer(csvoutfile)
                        
                        # 逐行讀取輸入檔案
                        for row in csvreader:
                            # 處理第7筆以後的資料
                            for i in range(6, len(row)):
                                try:
                                    # 將資料轉換為整數並除二
                                    row[i] = int(int(row[i]) / 2)
                                except ValueError:
                                    # 如果轉換失敗，保持原樣
                                    pass
                            
                            # 將處理後的資料寫入輸出檔案
                            csvwriter.writerow(row)

                print(f"處理完成，結果已寫入 {output_file}")

    print("所有處理完成。")

def resizeVideo(root_folder):
    # 設定根目錄


    # 設定處理檔案的ID計數
    id = 1

    # 處理每個符合條件的檔案
    for foldername, subfolders, filenames in os.walk(root_folder):
        for _, filename in enumerate(filenames):
            if filename.endswith('_background.jpg'):
                # 取得原始檔案的完整路徑，處理中文路徑
                input_file = os.path.join(foldername, filename)
                input_file = os.path.normpath(input_file)
                print(id, "處理檔案:", input_file)
                id += 1

                # 新檔案名稱
                new_filename = filename.replace('_background.jpg', '_div2_background.jpg')
                output_file = os.path.join(foldername, new_filename)
                output_file = os.path.normpath(output_file)

                # 使用 OpenCV 讀取影像，解決中文路徑問題
                image = cv2.imdecode(np.fromfile(input_file, dtype=np.uint8), cv2.IMREAD_UNCHANGED)

                # 確認影像是否成功讀取
                if image is not None:
                    # 獲取影像的尺寸
                    height, width = image.shape[:2]

                    # 將長寬除以二來縮小影像
                    new_width = width // 2
                    new_height = height // 2

                    # 使用 OpenCV 的 resize 函數來縮小影像
                    resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

                    # 將縮小後的影像寫入新的檔案，解決中文路徑問題
                    # 使用 np.fromfile 和 imdecode 讀取中文路徑的文件，並用 imencode 寫入
                    cv2.imencode('.jpg', resized_image)[1].tofile(output_file)

                    print(f"處理完成，結果已寫入 {output_file}")
                else:
                    print(f"無法讀取影像 {input_file}")

    print("所有處理完成。")

def process_rename(folder_path):
    # 遞迴遍歷所有子資料夾
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if "_div2" in file:  # 檢查檔案名稱中是否包含 "IO"
                file_path = os.path.join(root, file)
                new_filename = file.replace('_div2', '')
                new_path = os.path.join(root, new_filename)
                os.rename(file_path, new_path)
                print(f"已處理檔案: {new_path}")

root_folder = r'C:\Users\user\Documents\GitHub\TrafficTrackerGUI-MOTC\result\MOTC_roadsection_113_result'
process_rename(root_folder)