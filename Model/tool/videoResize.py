import cv2
import time

# 讀取原始影片
input_video_path = r'E:\Traffic\Block17\桃園市\1130705_桃園市中壢區中華路一段成功路口_120M\D架次\空拍影片\HD(穩像影片)\桃園市中壢區中華路一段成功路口D_stab.avi'
output_video_path = r'E:\Traffic\Block17\桃園市\1130705_桃園市中壢區中華路一段成功路口_120M\D架次\空拍影片\HD(穩像影片)\桃園市中壢區中華路一段成功路口D_stabHD.avi'

# 打開原始影片
cap = cv2.VideoCapture(input_video_path)

# 獲取影片的 FPS（幀率）和幀數
fps = cap.get(cv2.CAP_PROP_FPS)
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# 定義影片的解碼器和輸出影片參數
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_video_path, fourcc, fps, (1920, 1080))

# 逐幀處理影片
st = time.time()
for _ in range(frame_count):
    print(f"{_}/{frame_count}", end="\r")
    ret, frame = cap.read()
    if not ret:
        break
    
    # 調整幀大小為1920x1080
    resized_frame = cv2.resize(frame, (1920, 1080))
    
    # 將處理後的幀寫入輸出影片
    out.write(resized_frame)

# 釋放資源
cap.release()
out.release()

print(f"影片轉換完成！ cost:{round(time.time()-st, 3)}")
