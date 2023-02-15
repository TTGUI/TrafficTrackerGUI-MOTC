@echo off
set /p var="What is your CUDA version (10.2/11.1)? ":


rem create virtual environment
echo ====================================================
echo ============ Create virtual environment ============
echo ====================================================
python -m venv traffictrackergui-env
call traffictrackergui-env/Scripts/activate
python -m pip install --upgrade pip
python -m pip install --upgrade setuptools

rem install python package depencies
echo ====================================================
echo ========= Install python package depencies =========
echo ====================================================

if %var% == 10.2 goto cuda_10_2
if %var% == 11.1 goto cuda_11_1

:cuda_10_2
pip install -r requirements_cuda10.2.txt
goto yolov4_preprocess

:cuda_11_1
pip install -r requirements_cuda11.1.txt
goto yolov4_preprocess


:yolov4_preprocess
rem install mish-cuda
echo ====================================================
echo ================ Install mish-cuda =================
echo ====================================================
cd ./Model/YOLOv4/mish-cuda-windows
python setup.py -v build install

rem build box_utils
echo ====================================================
echo ================= Build box_utils ==================
echo ====================================================
cd ../utils_pkg/box_utils_win
python setup_win.py -v build_ext --inplace

rem build Rotated_IoU
echo ====================================================
echo ================ Build Rotated_IoU =================
echo ====================================================
cd ../Rotated_IoU/cuda_op
python setup.py -v install

cd ../../../../..

python change_data_path.py
call traffictrackergui-env/Scripts/deactivate

echo ====================================================
echo The installation is finished!!

pause