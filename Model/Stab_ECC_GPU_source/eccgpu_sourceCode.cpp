/*
* This sample demonstrates the use of the function
* findTransformECC that implements the image alignment ECC algorithm
*
*
* The demo loads an image (defaults to fruits.jpg) and it artificially creates
* a template image based on the given motion type. When two images are given,
* the first image is the input image and the second one defines the template image.
* In the latter case, you can also parse the warp's initialization.
*
* Input and output warp files consist of the raw warp (transform) elements
*
* Authors: G. Evangelidis, INRIA, Grenoble, France
*          M. Asbach, Fraunhofer IAIS, St. Augustin, Germany
*/

#include "ecc_cuda.h"


#include <opencv2/opencv.hpp>
#include <opencv2/core.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>

#include <opencv2/imgcodecs.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/video.hpp>
#include <opencv2/imgproc.hpp> 
#include <opencv2/core/utility.hpp>

#include <stdio.h>
#include <string>

#include <time.h>
#include <iostream>
#include <fstream>

#include <ctime>



using namespace cv;
using namespace std;


const std::string keys =
"{@inputVideoFolderPath    |./demo | input video folder path }"
"{@outputVideoName |output.avi| output video name }"
"{@cutinfoFile |cut.txt| cutinfo file name }"
"{n numOfIter    | 50            | ECC's iterations }"
"{e epsilon      | 0.0001        | ECC's convergence epsilon }"
"{v verbose      | 1             | display current process frame }"
"{l log      | 1             | output log information file }"
"{h output_height | 1080 | ECC and output video height}"
"{w output_width | 1920 | ECC and output video width}"
;


struct cutinfo
{
	int key = -1;
	int start = -1;
	int end = -1;
};


int main(const int argc, const char* argv[])
{



	cout << "<< ECC_GPU.exe Running... >>" << endl;
	CommandLineParser parser(argc, argv, keys);

	vector <cutinfo> cutinfoList;
	string cutFileName = parser.get<string>(2);

	ifstream myfile(cutFileName);
	string outFileName = "./logs/logs_tutorial/ECC_GPU_log.txt";
	ofstream outFile(outFileName);

	int data;
	int count = 0;
	if (myfile.is_open()) {
		// 讀取cutinfo
		cutinfo tempInfo;
		while (!myfile.eof())
		{
			count= count+1;
			myfile >> data;
			if (count == 1)
			{
				tempInfo.key = data;
			}

			else if (count == 2)
			{
				tempInfo.start = data;
			}

			else if (count == 3)
			{
				tempInfo.end = data;
				cutinfoList.push_back(tempInfo);
				count = 0;
			}

		}

	}
	else {
		cout << "Unable to open file : " << cutFileName << endl;
	}
	myfile.close();
	for (int i = 0; i < cutinfoList.size(); i++)
	{
		cout << "[" << i + 1 << "]\tK : " << cutinfoList[i].key << "\tS : " << cutinfoList[i].start << "\tE : " << cutinfoList[i].end << endl;
	}



	int verbose = parser.get<int>("v");
	int log = parser.get<int>("l");
	string videoDir = parser.get<string>(0);  // 空拍影片資料夾 根據UNIX風格路徑模式
	string videoDirCAP = videoDir + "/*.MP4"; 
	string videoDirLOWER = videoDir + "/*.mp4"; // 小寫
	string outputVideoName = parser.get<string>(1); // 輸出影片名稱
	int width = parser.get<int>("w");
	int height = parser.get<int>("h");
	Size outputSize = Size(width, height); // 輸出影片長寬
	double outputFPS = 9.99; // 輸出影片FPS
	int outputFourcc = VideoWriter::fourcc('X', 'V', 'I', 'D'); // 輸出影片編碼
	vector<String> videoListCAP; // 空拍影片路徑清單
	vector<String> videoListLOWER; // 空拍影片路徑清單
	glob(videoDirCAP, videoListCAP, false); // 取得資料夾下檔案路徑
	glob(videoDirLOWER, videoListLOWER, false); // 小寫
	double start_time = 0; // 開始ECC時間
	double ecd_time = 0; // 結束ECC時間



	if (log == 1)
	{
		if (outFile.is_open())
		{
			outFile << "[STEP 1] : input path : " << videoDir << endl;
			outFile << "[STEP 1] : output video : " << outputVideoName << endl;
		}
		else
		{
			cout << "log file opened fail." << endl;
		}
	}

	if (videoListCAP.size() != 0 && videoListLOWER.size() != 0)
	{	// 同時有大小寫副檔名時報錯
		cout << "<< Error : Also detect upper and lower case file extensions, please unify the format. >>" << endl;
		return 0;
	}
	
	if (videoListLOWER.size() != 0)
	{ // 將資料統一使用videoListCAP來存儲
		videoListCAP.clear();
		for (int i = 0; i < videoListLOWER.size(); i++)
			videoListCAP.push_back(videoListLOWER[i]);
		
	}

	int allFrameCounter = 0;

	// ofstream outPrint("GPU_PRINT.txt");

	VideoCapture cap;
	double inputFPS = 0.0; // 輸入影片FPS
	cap.open(videoListCAP[0]);
	if (!cap.isOpened())
	{
		cout << "cv2 videoCapture can not open this file : " << videoListCAP[0] << endl;
		return 0;
	}
	else
	{
		inputFPS = cap.get(CAP_PROP_FPS);
	}

	if (videoListCAP.size() != 0)
	{
		VideoCapture cap;
		VideoWriter writer;
		Mat template_image; // KEY frame 靜止畫面的標準
		writer.open(outputVideoName, outputFourcc, outputFPS, outputSize, true);

		Mat warp_matrix = Mat::eye(3, 3, CV_32F); // ECC用轉換矩陣，每次迭代使用
		int warp_mode = MOTION_HOMOGRAPHY;
		
		int number_of_iterations = parser.get<int>("n");
		double termination_eps = parser.get<double>("e");;
		int gaussian_size = 5;

		for (int i = 0; i < videoListCAP.size(); i++)
		{
			Mat frame;
			
			
			while  (cutinfoList[i].key == -1 && cutinfoList[i].start == -1 && cutinfoList[i].end == -1)
			{ // 遇到不處理影片
				cout << "[SKIP] > " << videoListCAP[i] << endl;
				if (i < videoListCAP.size())
					i++;
				else
					break;
			}

			if (i == videoListCAP.size())
				break;

			cout << "[PROCESS " << i+1 << " ] > " << videoListCAP[i] << endl;
			cap.open(videoListCAP[i]);
			if (!cap.isOpened())
			{
				cout << "cv2 videoCapture can not open this file : " << videoListCAP[i] << endl;
				break;
			}

			if (cutinfoList[i].key != -1)
			{	// 讀取並記錄template_image
				cap.set(CAP_PROP_POS_FRAMES, (cutinfoList[i].key)); // 將讀取位置設定為 key frame
				cap.read(frame);
				resize(frame, frame, outputSize, 0, 0, INTER_CUBIC);
				cvtColor(frame, frame, COLOR_BGR2GRAY);
				template_image = frame;
				cout << "Read key frame : " << cutinfoList[i].key  << endl;
				start_time = clock();
			}
		
			cap.set(CAP_PROP_POS_FRAMES, (cutinfoList[i].start)); // 將讀取位置設定為 start frame
			
			while (cap.read(frame) && cap.get(CAP_PROP_POS_FRAMES) != cutinfoList[i].end + 1)
			{
				
				if (allFrameCounter % int( inputFPS / outputFPS ) == 0)
				{
					resize(frame, frame, outputSize, 0, 0, INTER_CUBIC);

					
					Mat frame_gray;
					cvtColor(frame, frame_gray, COLOR_BGR2GRAY);
					
					double cc = findTransformECCGpu(template_image, frame_gray, warp_matrix, warp_mode,
						TermCriteria(TermCriteria::COUNT + TermCriteria::EPS,
							number_of_iterations, termination_eps), gaussian_size);
					cout << "\rECC Frame : " << cap.get(CAP_PROP_POS_FRAMES) << "\t cc : " << cc;
					// cout << cap.get(CAP_PROP_POS_FRAMES) << endl;
					// outPrint << cap.get(CAP_PROP_POS_FRAMES) << endl;
					warpPerspective(frame, frame, warp_matrix, frame.size(), INTER_CUBIC + WARP_INVERSE_MAP);
					writer.write(frame);
					if(verbose == 1)
					{
						imshow("frame", frame);
						waitKey(1);
					}

				}
				else
				{
					// outPrint << "\t" << cap.get(CAP_PROP_POS_FRAMES) << endl;
					// cout << "\t" << cap.get(CAP_PROP_POS_FRAMES) << endl;
				}

				
				/*
				if (allFrameCounter % 3 == 0)
				{


					cout << cap.get(CAP_PROP_POS_FRAMES) << endl;
					outPrint << cap.get(CAP_PROP_POS_FRAMES) << endl;
					writer.write(frame);


				}
				else
				{
					outPrint << "\t" << cap.get(CAP_PROP_POS_FRAMES) << endl;
					cout << "\t" << cap.get(CAP_PROP_POS_FRAMES) << endl;
				}
				*/

				allFrameCounter++;
			}
			
			cout << endl;
		}
		cap.release();
		writer.release();
		ecd_time = clock();
		cout << "\n[STEP 1] : cost time : " << (ecd_time - start_time) / CLOCKS_PER_SEC << endl;

		if (log == 1)
		{
			if (outFile.is_open())			
				outFile << "[STEP 1] : cost time : " << (ecd_time - start_time)/ CLOCKS_PER_SEC << endl;
			else			
				cout << "log file opened fail." << endl;			
		}		
	}

	outFile.close();
}


