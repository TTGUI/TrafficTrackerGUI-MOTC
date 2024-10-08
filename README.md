# Traffic Tracker GUI - MOTC
## Introduction
### 該程式提供使用者將原始空拍影片處理，並輸出車輛、行人軌跡追蹤檔與影像。該程式提供以下功能：
1. 空拍影像時間軸切割設定
2. 空拍影像穩定化
3. Yolo車輛與行人偵測
4. 偵測結果軌跡追蹤
5. 無車輛街道背景圖生成
6. 街道出入口設定
7. 軌跡添加街道出入口資訊
8. 軌跡繪製結果影片
9. 軌跡完整度驗證
10. 軌跡驗證輸出(影片/圖片/實時撥放)
11. 批次排程功能

## Installation
### 安裝與使用說明文件位於[doc](./doc)資料夾中
- 詳細安裝流程請參考[TrafficTrackerGUI_introduction.docx](./doc/TrafficTrackerGUI_introduction.docx)/[Google線上文件](https://docs.google.com/document/d/1_0h-pkgsuWSCED1gfbsh3dF7N0c0qbjx/edit?usp=sharing&ouid=100398044648873202865&rtpof=true&sd=true)
- 穩定影像步驟預設內建CPU版本，欲安裝GPU版本請參考[GPU_ECC安裝教學](./doc/GPU_ECC_install_introduction.docx)/[Google線上文件](https://docs.google.com/document/d/1x2xtYWFi6JJ_wzsxm2_RiXn20cEqbD33gZbXYUxyU5Q/edit?usp=sharing)。
### YOLO模型
- 由於模型檔案大小無法上傳至GitHub，請[下載](https://mega.nz/folder/cT9lnJID#2L2coFONYwYCCajv0wA5aA)後放置於[weights](.\Model\YOLOv4\weights)

## Usage
- 點擊[start_gui.bat](./start_gui.bat)開啟GUI程式。
- 詳細操作流程請參考[TrafficTrackerGUI_introduction.docx](./doc/TrafficTrackerGUI_introduction.docx)。
- 簡易操作流程請參考[操作影片](./doc/簡易TrafficTrackerGUI操作說明.mp4)。

## Contributing
- 完成所有GUI介面與各步驟單元功能整合。

## License
- [GPLv2](https://choosealicense.com/licenses/gpl-2.0/)

## Contact
- dongzhu@cycu.org.tw

## Acknowledgements
- 特別感謝`lucas`在各項步驟單元的開發與調試上的協助。
- 特別感謝`jacklin`在Yolo方面上的開發與OpenCV上的協助。

