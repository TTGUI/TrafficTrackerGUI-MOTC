import csv

# 定義讀取和寫入的檔案名稱
input_file = r'E:\Traffic\Block17\桃園市\1130705_桃園市中壢區中華路一段成功路口_120M\D架次\空拍影片\HD(穩像影片)\桃園市中壢區中華路一段成功路口D_gate.csv'
output_file = r'E:\Traffic\Block17\桃園市\1130705_桃園市中壢區中華路一段成功路口_120M\D架次\空拍影片\HD(穩像影片)\桃園市中壢區中華路一段成功路口D_gateHD.csv'

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