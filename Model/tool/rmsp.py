import os

def f1():
    # 取得程式檔案的位置
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # 切換工作目錄至程式檔案的位置
    os.chdir(script_dir)


    # 讀取檔案
    with open("./桃園市高鐵北路一段青心路_D_stab_1080_13145.txt", "r") as file_in:
        lines = file_in.readlines()

    # 刪除空白行
    lines = [line for line in lines if line.strip() != ""]

    # 輸出檔案
    with open("桃園市高鐵北路一段青心路_D_stab_8cls.txt", "w") as file_out:
        file_out.writelines(lines)

def f2():

    # 取得程式檔案的位置
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # 切換工作目錄至程式檔案的位置
    os.chdir(script_dir)

    # 讀取檔案
    with open("./桃園市高鐵北路一段青心路_D_stab_1080_13145.txt", "r") as file_in:
        lines = file_in.readlines()

    # 將空白行替換為行數ID
    lines = [f"{i+1}\n" if line.strip() == "" else line for i, line in enumerate(lines)]

    # 輸出檔案
    with open("桃園市高鐵北路一段青心路_D_stab_8cls.txt", "w") as file_out:
        file_out.writelines(lines)
