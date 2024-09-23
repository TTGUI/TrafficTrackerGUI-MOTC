import os
import sys
import itertools

# 定義 ANSI 顏色代碼
RESET = '\033[0m'
BOLD = '\033[1m'
BLACK = '\033[30m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
WHITE = '\033[37m'
BRIGHT_BLACK = '\033[90m'
BRIGHT_RED = '\033[91m'
BRIGHT_GREEN = '\033[92m'
BRIGHT_YELLOW = '\033[93m'
BRIGHT_BLUE = '\033[94m'
BRIGHT_MAGENTA = '\033[95m'
BRIGHT_CYAN = '\033[96m'
BRIGHT_WHITE = '\033[97m'

# Windows 平台支援 ANSI 顏色
if sys.platform.startswith('win'):
    import colorama
    colorama.init()

# 預定義的檔案副檔名與對應的顏色
predefined_colors = {
    '.py': YELLOW,
    '.txt': GREEN,
    '.jpg': MAGENTA,
    '.jpeg': BLUE,
    '.png': BRIGHT_RED,
    '.csv': CYAN,
    
    '.mp4': BLACK,
    '.avi': RED,
}

# 動態顏色列表，用於未預定義的檔案副檔名
dynamic_colors = [
    BRIGHT_RED,
    BRIGHT_GREEN,
    BRIGHT_YELLOW,
    BRIGHT_MAGENTA,
    BRIGHT_CYAN,
    BRIGHT_WHITE,        
    WHITE,
    BLACK,
    BRIGHT_BLACK,
]

# 創建一個顏色循環迭代器
color_cycle = itertools.cycle(dynamic_colors)

# 存儲動態分配的副檔名與顏色的映射關係
dynamic_extension_colors = {}

def get_color(entry_path):
    """
    根據檔案類型返回對應的顏色代碼。
    """
    if os.path.isdir(entry_path):
        return BOLD + BLUE  # 藍色加粗表示目錄
    else:
        _, ext = os.path.splitext(entry_path)
        ext = ext.lower()
        if ext in predefined_colors:
            return predefined_colors[ext]
        else:
            if ext not in dynamic_extension_colors:
                # 為新的副檔名分配一個顏色
                dynamic_extension_colors[ext] = next(color_cycle)
            return dynamic_extension_colors[ext]

def tree(dir_path, prefix=''):
    """
    列出指定目錄下的所有子目錄和檔案，並以樹狀結構顯示。
    根據不同檔案類型以不同顏色顯示，目錄名稱後面加上反斜線 '\'
    """
    entries = os.listdir(dir_path)
    entries.sort()
    entries_count = len(entries)
    for index, entry in enumerate(entries):
        entry_path = os.path.join(dir_path, entry)
        connector = '└── ' if index == entries_count - 1 else '├── '
        color = get_color(entry_path)
        if os.path.isdir(entry_path):
            print(prefix + connector + color + entry + '\\' + RESET)
            extension = '    ' if index == entries_count - 1 else '│   '
            tree(entry_path, prefix + extension)
        else:
            print(prefix + connector + color + entry + RESET)

if __name__ == "__main__":
        dir_path = input("請輸入要查詢的目錄路徑: ")
        if os.path.exists(dir_path):
            print(dir_path)
            tree(dir_path)
        else:
            print("錯誤: 指定的路徑不存在!")
