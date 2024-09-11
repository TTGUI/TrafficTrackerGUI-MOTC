import cv2
import numpy as np
import os

# 設定根目錄
root_folder = r'E:\Traffic\Block18'

# 儲存符合條件的影片檔案路徑
stab_files = []
processed_files = []

# 遍歷根目錄底下的所有檔案
for foldername, subfolders, filenames in os.walk(root_folder):
    for filename in filenames:
        if filename.endswith('_stab.avi'):
            stab_path = os.path.join(foldername, filename)
            stab_files.append(stab_path)

# 列印所有符合條件的影片名稱並附加序號
print("找到以下符合條件的影片:")
for idx, file in enumerate(stab_files):
    print(f"{idx + 1}: {file}")

total_videos = len(stab_files)

# 處理每一個符合條件的影片
for video_idx, stab_path in enumerate(stab_files):
    # 設定輸出檔案名稱
    output_path = stab_path.replace('_stab.avi', '_stab_reshape.avi')

    # 開啟影片
    cap = cv2.VideoCapture(stab_path)
    if not cap.isOpened():
        print(f"Error: 無法開啟影片檔案 {stab_path}")
        continue

    # 取得影片的寬度和高度
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # 初始化處理過的影片幀大小
    frame2 = np.zeros((1920, 1920, 3), dtype=np.uint8)

    # 設置影片輸出
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, 10, (1920, 1920))

    print(f"\n開始處理影片 {video_idx + 1}/{total_videos}: {stab_path}")

    frame_idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # 處理影片幀（例如，根據需要的裁剪或轉換）
        frame2[0:960, :, :] = frame[500:500+960, 300:300+1920, :]
        frame2[960:1920, :, :] = frame[500:500+960, 1920:1920+1920, :]

        # 寫入處理後的幀到新影片
        out.write(frame2)

        # 更新進度
        frame_idx += 1
        print(f"處理進度: {frame_idx}/{total_frames} 幀", end='\r')

    # 釋放資源
    cap.release()
    out.release()

    print(f"\n成功處理影片: {output_path}")
    processed_files.append(output_path)

# 完成後關閉所有 OpenCV 視窗
cv2.destroyAllWindows()

# 總結
print("\n所有影片處理完畢！")
print("成功處理的影片清單:")
for idx, file in enumerate(processed_files):
    print(f"{idx + 1}: {file}")
