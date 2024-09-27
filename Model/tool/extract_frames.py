import cv2
import os

def extract_and_crop_frames(video_path, start_frame, end_frame, crop_start=None, crop_end=None):
    # 開啟影片檔案
    cap = cv2.VideoCapture(video_path)

    # 確認影片是否成功開啟
    if not cap.isOpened():
        print("無法開啟影片檔案")
        return

    # 建立儲存影格的資料夾
    output_dir = os.path.join(os.path.dirname(video_path), os.path.splitext(os.path.split(video_path)[1])[0])
    os.makedirs(output_dir, exist_ok=True)

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"影片總共有 {frame_count} 個 frame")

    # 檢查 end_frame 是否超出範圍
    end_frame = min(end_frame, frame_count)

    # 設定起始 frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    # 開始擷取影格
    frame_idx = start_frame
    save_idx = 0

    while frame_idx <= end_frame:
        ret, frame = cap.read()

        if not ret:
            break

        # 每隔 30 個 frame 儲存一張
        if (frame_idx - start_frame) % 4 == 0:
            # 進行裁切
            if crop_end != None and crop_start != None:
                x_start, y_start = crop_start
                x_end, y_end = crop_end
                cropped_frame = frame[y_start:y_end, x_start:x_end]
            else:
                cropped_frame = frame
            output_path = os.path.join(output_dir, f"{save_idx:04d}.jpg")
            cv2.imwrite(output_path, cropped_frame)
            print(f"儲存裁切後的 frame {frame_idx} 至 {output_path}")
            save_idx += 1

        frame_idx += 1

    # 釋放資源
    cap.release()
    print("完成擷取、裁切並儲存影格")

# 使用範例
video_path = r"D:\20240920_video\IMG_0028.MOV"

start_frame = 12868  # 開始 frame
end_frame = 13005    # 結束 frame

# crop_start = (160, 260)     # 裁切起始座標 (x_start, y_start)
# crop_end = (980, 1230)       # 裁切結束座標 (x_end, y_end)

# extract_and_crop_frames(video_path, start_frame, end_frame, crop_start, crop_end)

extract_and_crop_frames(video_path, start_frame, end_frame)
