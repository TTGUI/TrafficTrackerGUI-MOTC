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

string formatTime(double seconds)
{
    int h = int(seconds / 3600);
    int m = int((seconds - h * 3600) / 60);
    int s = int(seconds - h * 3600 - m * 60);
    char buffer[9];
    snprintf(buffer, sizeof(buffer), "%02d:%02d:%02d", h, m, s);
    return string(buffer);
}

void printProgressBar(int current, int total, double elapsed_seconds, double remaining_seconds, int barWidth = 50)
{
    double percentage = double(current) / total;
    std::cout << "\r[";
    int pos = int(barWidth * percentage);
    for (int i = 0; i < barWidth; ++i) {
        if (i < pos) std::cout << "=";
        else if (i == pos) std::cout << ">";
        else std::cout << " ";
    }
    std::cout << "] " << int(percentage * 100.0) << "% ";
    std::cout << current << "/" << total << " ";
    std::cout << "Elapsed: " << formatTime(elapsed_seconds) << " ";
    std::cout << "Remaining: " << formatTime(remaining_seconds);
    std::cout.flush();
}

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
        // Read cutinfo
        cutinfo tempInfo;
        while (!myfile.eof())
        {
            count = count + 1;
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
    string videoDir = parser.get<string>(0);  // Input video folder path
    string videoDirCAP = videoDir + "/*.MP4";
    string videoDirLOWER = videoDir + "/*.mp4"; // Lowercase
    string outputVideoName = parser.get<string>(1); // Output video name
    int width = parser.get<int>("w");
    int height = parser.get<int>("h");
    cout << "<< ECC_GPU output layout : width:" << width << ", height:" << height << endl;
    Size outputSize = Size(width, height); // Output video size
    double outputFPS = 9.99; // Output video FPS
    int outputFourcc = VideoWriter::fourcc('X', 'V', 'I', 'D'); // Output video codec
    vector<String> videoListCAP; // Video file paths
    vector<String> videoListLOWER; // Video file paths
    glob(videoDirCAP, videoListCAP, false); // Get file paths
    glob(videoDirLOWER, videoListLOWER, false); // Lowercase
    double start_time = 0; // ECC start time
    double ecd_time = 0; // ECC end time

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
    {   // Error if both uppercase and lowercase extensions are detected
        cout << "<< Error : Also detect upper and lower case file extensions, please unify the format. >>" << endl;
        return 0;
    }

    if (videoListLOWER.size() != 0)
    { // Use videoListCAP to store paths
        videoListCAP.clear();
        for (int i = 0; i < videoListLOWER.size(); i++)
            videoListCAP.push_back(videoListLOWER[i]);
    }

    int allFrameCounter = 0;

    VideoCapture cap;
    double inputFPS = 0.0; // Input video FPS
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
        Mat template_image; // Key frame
        writer.open(outputVideoName, outputFourcc, outputFPS, outputSize, true);

        Mat warp_matrix = Mat::eye(3, 3, CV_32F); // Transformation matrix for ECC
        int warp_mode = MOTION_HOMOGRAPHY;

        int number_of_iterations = parser.get<int>("n");
        double termination_eps = parser.get<double>("e");;
        int gaussian_size = 5;

        int frame_step = int(inputFPS / outputFPS);

        for (int i = 0; i < videoListCAP.size(); i++)
        {
            Mat frame;

            while (cutinfoList[i].key == -1 && cutinfoList[i].start == -1 && cutinfoList[i].end == -1)
            { // Skip videos not to be processed
                cout << "[SKIP] > " << videoListCAP[i] << endl;
                if (i < videoListCAP.size())
                    i++;
                else
                    break;
            }

            if (i == videoListCAP.size())
                break;

            cout << "[PROCESS " << i + 1 << " ] > " << videoListCAP[i] << endl;
            cap.open(videoListCAP[i]);
            if (!cap.isOpened())
            {
                cout << "cv2 videoCapture can not open this file : " << videoListCAP[i] << endl;
                break;
            }

            if (cutinfoList[i].key != -1)
            {   // Read and record template_image
                cap.set(CAP_PROP_POS_FRAMES, (cutinfoList[i].key)); // Set to key frame
                cap.read(frame);
                resize(frame, frame, outputSize, 0, 0, INTER_CUBIC);
                cvtColor(frame, frame, COLOR_BGR2GRAY);
                template_image = frame;
                cout << "Read key frame : " << cutinfoList[i].key << endl;
                start_time = clock();
            }

            cap.set(CAP_PROP_POS_FRAMES, (cutinfoList[i].start)); // Set to start frame

            int frames_in_video = cutinfoList[i].end - cutinfoList[i].start + 1;
            int total_frames_in_video = (frames_in_video + frame_step - 1) / frame_step;
            int frames_processed = 0;
            clock_t video_start_time = clock();

            while (cap.read(frame) && cap.get(CAP_PROP_POS_FRAMES) != cutinfoList[i].end + 1)
            {
                if (allFrameCounter % frame_step == 0)
                {
                    resize(frame, frame, outputSize, 0, 0, INTER_CUBIC);
                    Mat frame_gray;
                    cvtColor(frame, frame_gray, COLOR_BGR2GRAY);

                    double cc = findTransformECCGpu(template_image, frame_gray, warp_matrix, warp_mode,
                        TermCriteria(TermCriteria::COUNT + TermCriteria::EPS,
                            number_of_iterations, termination_eps), gaussian_size);

                    warpPerspective(frame, frame, warp_matrix, frame.size(), INTER_CUBIC + WARP_INVERSE_MAP);
                    writer.write(frame);

                    frames_processed++;

                    double percentage = double(frames_processed) / total_frames_in_video;
                    double elapsed_seconds = double(clock() - video_start_time) / CLOCKS_PER_SEC;
                    double estimated_total_time = elapsed_seconds / percentage;
                    double remaining_seconds = estimated_total_time - elapsed_seconds;

                    // Update progress bar
                    printProgressBar(frames_processed, total_frames_in_video, elapsed_seconds, remaining_seconds);

                    if (verbose == 1)
                    {
                        imshow("frame", frame);
                        waitKey(1);
                    }
                }
                else
                {
                    // Skipped frame
                }
                allFrameCounter++;
            }
            std::cout << std::endl; // Move to next line after progress bar
            cout << "Finished processing video " << i + 1 << "/" << videoListCAP.size() << endl;
        }
        cap.release();
        writer.release();
        ecd_time = clock();
        cout << "\n[STEP 1] : cost time : " << (ecd_time - start_time) / CLOCKS_PER_SEC << endl;

        if (log == 1)
        {
            if (outFile.is_open())
                outFile << "[STEP 1] : cost time : " << (ecd_time - start_time) / CLOCKS_PER_SEC << endl;
            else
                cout << "log file opened fail." << endl;
        }
    }

    outFile.close();
}
