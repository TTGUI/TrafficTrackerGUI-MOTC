input_file_path = '國道3號忠和交流道_300米_20240521_162413_C架次_reshape_8cls.txt'
output_file_path = '國道3號忠和交流道_300米_20240521_162413_C架次_8cls.txt'

# 讀取並處理每行數據
with open(input_file_path, 'r') as infile, open(output_file_path, 'w') as outfile:
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
            
            # Tw = Bw = 1920, Bh: no use                                                                                                                                                                    #5452x3056
            # Tx, Ty, Th = 600, 800, 960 # Top road region
            # Bx, By = 1960, 800 # Bottom road region

            Tx, Ty, Th = 300, 500, 960 # Top road region
            Bx, By = 1960, 500 # Bottom road region

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
