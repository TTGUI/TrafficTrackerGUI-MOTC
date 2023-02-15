read -p "What is your CUDA version (10.2/11.1)? " cuda_version

# avoid pip install lap error
sudo apt-get install -y python3-dev

sudo apt-get install -y python3-venv

#################
#  if gui can not open
`
qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.
`
sudo apt-get install -y libxcb-xinerama0
################

# create virtual environment
python3 -m venv traffictrackergui-env
# activate virtual environment
source traffictrackergui-env/bin/activate
python -m pip install --upgrade pip
python -m pip install --upgrade setuptools

if [ "$cuda_version" = "10.2" ] ; then
    pip install -r requirements_cuda10.2.txt
fi

if [ "$cuda_version" = "11.1" ] ; then
    pip install -r requirements_cuda11.1.txt
fi

# install mish-cuda
cd ./Model/YOLOv4/mish-cuda-linux
python setup.py -v install

# build box_utils
cd ../utils_pkg/box_utils_linux
python setup_linux.py build_ext --inplace

# build Rotated_IoU
cd ../Rotated_IoU/cuda_op
python setup.py -v install

cd ../../../../..
python change_data_path.py

echo "The installation is finished!!"
