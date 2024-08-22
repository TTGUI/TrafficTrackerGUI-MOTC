import cv2
import os

# 設定影像資料夾路徑
image_folder = r'C:\Users\Lab602_assistant\AppData\Roaming\PotPlayerMini64\Capture'
# 設定輸出影片檔案名稱
video_name = r'E:\data\temp\output_video_stab.avi'
# 設定影格率（每秒顯示的影像數）
frame_rate = 30

# 讀取所有影像檔案名稱
images = [img for img in os.listdir(image_folder) if img.endswith((".png", ".jpg", ".jpeg"))]
# 對影像檔案名稱進行排序（假設影像檔名具有順序）
images.sort()

# 確保資料夾中有影像
if not images:
    raise ValueError("No images found in the provided folder.")

# 讀取第一張影像來獲取影像的尺寸
frame = cv2.imread(os.path.join(image_folder, images[0]))
height, width, layers = frame.shape

# 設定影片編碼器和輸出影片物件
fourcc = cv2.VideoWriter_fourcc(*'XVID')
video = cv2.VideoWriter(video_name, fourcc, frame_rate, (width, height))

# 將每一張影像加入影片中
for image in images:
    img_path = os.path.join(image_folder, image)
    frame = cv2.imread(img_path)
    video.write(frame)

# 釋放影片物件
video.release()
print(f"影片已成功輸出為 {video_name}")
