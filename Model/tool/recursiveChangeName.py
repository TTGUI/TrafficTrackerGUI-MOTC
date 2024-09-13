import os
import cv2
import numpy as np

# 設定根目錄
root_folder = r'E:\Traffic\Block18'

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
