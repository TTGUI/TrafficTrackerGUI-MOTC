@echo off
REM 使用anaconda創建環境時呼叫方式
echo Activating Conda environment...

REM 初始化 Conda（這一步用來啟動 conda 命令）
CALL "C:\ProgramData\anaconda3\Scripts\activate.bat"
IF ERRORLEVEL 1 (
    echo Failed to activate base conda environment.
    pause
    exit /b
)

REM 啟動 Conda 環境
CALL conda activate C:\Users\Rontgen-W11-NB\.conda\envs\ttgui-env
IF ERRORLEVEL 1 (
    echo Failed to activate ttgui-env environment.
    pause
    exit /b
)

REM 切換到 Python 檔案所在目錄
cd /d D:\TrafficTrackerGUI-MOTC
IF ERRORLEVEL 1 (
    echo Failed to change directory.
    pause
    exit /b
)

REM 執行 Python 檔案
python GUI.py
IF ERRORLEVEL 1 (
    echo Failed to run GUI.py.
    pause
    exit /b
)

REM 保持命令提示字元窗口打開
pause
