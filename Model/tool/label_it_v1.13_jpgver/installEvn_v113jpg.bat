@echo off

rem create virtual environment
echo ====================================================
echo ============ Create virtual environment ============
echo ====================================================
python -m venv labeltool-v113-env
call labeltool-v113-env\Scripts\activate
python -m pip install --upgrade pip
python -m pip install --upgrade setuptools

rem install python package depencies
echo ====================================================
echo ========= Install python package depencies =========
echo ====================================================

pip install PyForms-GUI
pip install PyOpenGL-accelerate

call labeltool-v113-env\Scripts\deactivate

echo ====================================================
echo The installation is finished!!

pause