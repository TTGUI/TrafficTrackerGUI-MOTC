read -p "Install cuda and cudnn [y/n]? " cuda_cudnn_flag
read -p "Choose CUDA version (10.2/11.1)? " cuda_version

if [ "$cuda_cudnn_flag" = "y" ] ; then
    if [ "$cuda_version" = "10.2" ] ; then
	# install cuda 10.2 with deb
	cd cuda_deb/10.2
	#wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-ubuntu1804.pin
	sudo cp cuda-ubuntu1804.pin /etc/apt/preferences.d/cuda-repository-pin-600
	#wget https://developer.download.nvidia.com/compute/cuda/10.2/Prod/local_installers/cuda-repo-ubuntu1804-10-2-local-10.2.89-440.33.01_1.0-1_amd64.deb
	sudo dpkg -i cuda-repo-ubuntu1804-10-2-local-10.2.89-440.33.01_1.0-1_amd64.deb
	sudo apt-key add /var/cuda-repo-10-2-local-10.2.89-440.33.01/7fa2af80.pub
	sudo apt-get update
	sudo apt-get -y install cuda

	sudo dpkg -i cuda-repo-ubuntu1804-10-2-local_10.2.1-1_amd64.deb
	sudo apt-get update
	sudo apt-get -y install cuda

	sudo dpkg -i cuda-repo-ubuntu1804-10-2-local_10.2.2-1_amd64.deb
	sudo apt-get update
	sudo apt-get -y install cuda

	echo -e "\n# Setup CUDA 10.2 .deb environment path" | tee -a ~/.bashrc
	echo "export PATH=/usr/local/cuda-10.2/bin:/usr/local/cuda-10.2/NsightCompute-2019.1\${PATH:+:\${PATH}}" | tee -a ~/.bashrc
	source ~/.bashrc
	cd ../..

	# install cudnn
	sudo dpkg -i ./cudnn_deb/cuda10.2_cudnn8.2.1/libcudnn8_8.2.1.32-1+cuda10.2_amd64.deb
	sudo dpkg -i ./cudnn_deb/cuda10.2_cudnn8.2.1/libcudnn8-dev_8.2.1.32-1+cuda10.2_amd64.deb
	sudo dpkg -i ./cudnn_deb/cuda10.2_cudnn8.2.1/libcudnn8-samples_8.2.1.32-1+cuda10.2_amd64.deb

	echo "CUDA10.2 and CuDNN8.2.1 installation is finished!!"
    fi

    if [ "$cuda_version" = "11.1" ] ; then
	# install cuda 11.1 with deb

	# pre install
	# apt-get install linux-headers-$(uname -r)
	# apt -y autoremove

	# install cuda 11.1
	cd cuda_deb/11.1
	# wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-ubuntu1804.pin
	sudo cp cuda-ubuntu1804.pin /etc/apt/preferences.d/cuda-repository-pin-600
	# wget https://developer.download.nvidia.com/compute/cuda/11.1.0/local_installers/cuda-repo-ubuntu1804-11-1-local_11.1.0-455.23.05-1_amd64.deb
	sudo dpkg -i cuda-repo-ubuntu1804-11-1-local_11.1.0-455.23.05-1_amd64.deb
	sudo apt-key add /var/cuda-repo-ubuntu1804-11-1-local/7fa2af80.pub
	sudo apt-get update
	sudo apt-get -y install cuda
	echo -e "\n# Setup CUDA 11.1 .deb environment path" | tee -a ~/.bashrc
	echo "export PATH=/usr/local/cuda-11.1/bin\${PATH:+:\${PATH}}" | tee -a ~/.bashrc
	source ~/.bashrc
	cd ../..

	# install cudnn
	sudo dpkg -i ./cudnn_deb/libcudnn8_8.0.4.30-1+cuda11.1_amd64.deb
	sudo dpkg -i ./cudnn_deb/libcudnn8-dev_8.0.4.30-1+cuda11.1_amd64.deb
	sudo dpkg -i ./cudnn_deb/libcudnn8-samples_8.0.4.30-1+cuda11.1_amd64.deb
	
	echo "CUDA11.1 and CuDNN8.0.4 installation is finished!!"
    fi

    echo "The computer will reboot in 3 seconds..."
    sleep 3s
    reboot
fi
