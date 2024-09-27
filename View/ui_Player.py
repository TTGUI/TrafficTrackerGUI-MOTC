import cv2
import os
import numpy as np
from PySide2 import QtTest
from PySide2.QtCore import Slot
from PySide2.QtGui import QImage, QPixmap
from PySide2.QtWidgets import QApplication, QMessageBox

from logs import logger
from .ui_BaseManager import BaseManager
if not hasattr(QtTest.QTest, 'qWait'):
    @staticmethod
    def qWait(msec):
        import time
        start = time.time()
        QApplication.processEvents()
        while time.time() < start + msec * 0.001:
            QApplication.processEvents()
    QtTest.QTest.qWait = qWait

class PlayerManager(BaseManager):
    """本類別處理 Player 的文字、功能綁定、功能函數"""
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_windowmain_window = main_window
        
        self.initText()     # 初始化按鈕文字
        self.bind_buttons() # 綁定按鈕與槽

    def initText(self):
        self.main_window._window.play_btn.setText('Play')
        self.main_window._window.pause_btn.setText('Pause')
        self.main_window._window.SetStartFrame_btn.setText('Set Start Frame')
        self.main_window._window.SetEndFrame_btn.setText('Set End Frame')
        self.main_window._window.fpsback100_btn.setText('<<<')
        self.main_window._window.fpsback1_btn.setText('<')
        self.main_window._window.fpsnext100_btn.setText('>>>')
        self.main_window._window.fpsnext1_btn.setText('>')
        self.main_window._window.jump_btn.setText('Jump')
        self.main_window._window.jump_btn.setToolTip('In TIVP-R: add `i` before issue ID\nwhich you want to add.\nex: `i999`')
        self.main_window._window.stop_btn.setText('Stop')
    def bind_buttons(self):
        self.main_window._window.play_btn.clicked.connect(self.play)
        self.main_window._window.pause_btn.clicked.connect(self.pause)
        self.main_window._window.SetStartFrame_btn.clicked.connect(self.setStartFrame)
        self.main_window._window.SetEndFrame_btn.clicked.connect(self.setEndFrame)
        self.main_window._window.fpsback100_btn.clicked.connect(self.fpsback100)
        self.main_window._window.fpsback1_btn.clicked.connect(self.fpsback1)
        self.main_window._window.fpsnext100_btn.clicked.connect(self.fpsnext100)
        self.main_window._window.fpsnext1_btn.clicked.connect(self.fpsnext1)
        self.main_window._window.jump_btn.clicked.connect(self.jump)
        self.main_window._window.stop_btn.clicked.connect(self.stop)
        self.main_window._window.timingSlider.sliderMoved.connect(self.video_position)
    Slot()
    def set_video(self, type):
        if type == 1 : # Step 0 Cut Info Player Mode
            self.video_init = True
            self.play_bool = False
            self.main_window.currentVideoIndex = 0
            self.main_window.videolist = os.listdir(self.main_window.droneFolderPath)
            self.main_window.videolist.sort()
            self.main_window.videoLen = len(self.main_window.videolist)
            self.main_window.cutInfoLsit = []
            for i in range( 0 ,self.main_window.videoLen ):
                tempCut = CutInfo()            

                cap = cv2.VideoCapture(os.path.join( os.path.abspath(self.main_window.droneFolderPath), self.main_window.videolist[i]))

                tempCut.setStart(0)
                tempCut.setEnd(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
                cap.release()
                self.main_window.cutInfoLsit.append(tempCut)

            self.displayInfo(2)

            out = ''
            for i in range(0,self.main_window.videoLen) :
                out = out + '[' + str(i+1) +'] '+ self.main_window.videolist[i] + '\n'

            msgBox = QMessageBox()
            msgBox.setWindowTitle("Video Load")
            msgBox.setText(out)
            msgBox.exec()

            self.load()
        elif type == 2 : # Step 9 TIVP Real Time Mode
            self.video_init = True
            self.play_bool = False
            self.cap = cv2.VideoCapture(self.main_window.stab_video)
            print("LOAD : " + str(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))+ ' frames')
            self.allFream = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
    Slot()
    def load(self):
        if self.video_init == False :
            self._window.cutinfo.setText('Error : video are not set yet.')
            return

        self.displayInfo(1)
        self.cap = cv2.VideoCapture(os.path.join( os.path.abspath(self.main_window.droneFolderPath), self.main_window.videolist[self.main_window.currentVideoIndex]))
        print("LOAD : " + str(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))+ ' frames')
        self.allFream = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.video_init = True
    Slot()
    def frameDisplay(self, frame):
        if self.main_window.TIVPmode == 3 and self.main_window.currentStep == 9:
            frame = self.issueFramePrint(frame)

        fps = str(int(self.cap.get(cv2.CAP_PROP_POS_FRAMES) - 1))
        cv2.putText(frame, fps, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 6, cv2.LINE_AA)
        cv2.putText(frame, fps, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3, cv2.LINE_AA)
        self.main_window._window.FPS.setText(fps)
        now_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES) - 1
        self.main_window._window.timingSlider.setValue(int((now_frame / self.allFream) * 100))

        self.qtFrameDisplay(frame)
    Slot()
    def issueFramePrint(self, frame):
        def RTcenter(points):
            ans = []
            
            x = (int(points[0]) + int(points[4]) ) / 2
            y = (int(points[1]) + int(points[5]) ) / 2
            ans.append(int(x))
            ans.append(int(y))
            return ans


        ### Add IO lines ###
        V2 = self.main_window.TIVioLines[0].split(",")
        V3 = self.main_window.TIVioLines[1].split(",")
        typecode = "XABCDEFGHIJKLMNOPQRSTUVW" 

        pts = []
        bordertype = []
        for i in range(0, len(V2)-1):
            bordertype.append(int(V2[i]))
            pts.append((int(V3[2*i]), int(V3[2*i+1])))

        for j in range(-1, len(bordertype)-1):
            if bordertype[j] > 0:
                cv2.line(frame, pts[j], pts[j+1], (0, 255, 0), 3)
                cv2.putText(frame, f"{typecode[abs(int(bordertype[j]))]}I", ((pts[j][0]+pts[j+1][0])//2, (pts[j][1]+pts[j+1][1])//2), cv2.FONT_HERSHEY_SIMPLEX,  0.5, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.putText(frame, f"{typecode[abs(int(bordertype[j]))]}I", ((pts[j][0]+pts[j+1][0])//2, (pts[j][1]+pts[j+1][1])//2), cv2.FONT_HERSHEY_SIMPLEX,  0.5, (0, 255, 0), 1, cv2.LINE_AA)

            elif bordertype[j] < 0:
                cv2.line(frame, pts[j], pts[j+1], (0, 0, 255), 3)    
                cv2.putText(frame, f"{typecode[abs(int(bordertype[j]))]}O", ((pts[j][0]+pts[j+1][0])//2, (pts[j][1]+pts[j+1][1])//2), cv2.FONT_HERSHEY_SIMPLEX,  0.5, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.putText(frame, f"{typecode[abs(int(bordertype[j]))]}O", ((pts[j][0]+pts[j+1][0])//2, (pts[j][1]+pts[j+1][1])//2), cv2.FONT_HERSHEY_SIMPLEX,  0.5, (0, 0, 255), 1, cv2.LINE_AA)

        for j in range(2, len(self.main_window.TIVioLines)):
            V4 = self.main_window.TIVioLines[j].split(",")
            k = 0
            for k in range(0, len(V4)-3, 2):
                cv2.line(frame, (int(V4[k]), int(V4[k+1])), (int(V4[k+2]), int(V4[k+3])), (255, 0, 0), 2)

        ### Add Issue Tracking ###
        findex = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))  # Current frame index

        # Prepare a set of issue IDs from self.TIVIsampleList
        # Assuming that self.TIVIsampleList contains strings where the issue ID is the first element when split by ','
        issue_ids_to_draw = set()
        for issue_str in self.main_window.TIVIsampleList:
            issue_id = int(issue_str.split(',')[0])
            issue_ids_to_draw.add(issue_id)

        # Create an overlay for semi-transparent drawing
        overlay = frame.copy()

        # Initialize alpha to zero
        alpha = 0.0  # Default transparency factor

        # Flag to check if any drawing was performed
        drawing_performed = False

        # Initialize list to store trajectory lines to draw after blending
        trajectory_lines = []

        # Loop through all issues in self.V and only process those in issue_ids_to_draw
        for j in range(len(self.V)):
            linePoints = self.V[j]
            issue_id = int(linePoints[0])

            # Only process issues that are in the TIVP issue list
            if issue_id in issue_ids_to_draw:
                start_frame = int(linePoints[1])  # Start frame of the object
                end_frame = int(linePoints[2])    # End frame of the object

                # Check if the issue is active at the current frame
                if start_frame <= findex <= end_frame:
                    drawing_performed = True  # We will perform drawing

                    # Assign colors and alpha inside the loop
                    if issue_id == int(self.main_window.TIVIsampleList[self.main_window.currentIssueIndex].split(',')[0]):
                        # Current issue - use distinct colors
                        fill_color = (0, 255, 255)    # Cyan
                        box_color = (0, 0, 255)       # Red box
                        center_color = (0, 255, 255)  # Cyan center
                        trajectory_color = (0, 255, 255)  # Cyan for trajectory lines
                        alpha = max(alpha, 0.4)       # Use the maximum alpha value
                    else:
                        # Other issues
                        fill_color = (0, 255, 0)      # Green
                        box_color = (0, 255, 0)       # Green box
                        center_color = (0, 255, 0)    # Green center
                        trajectory_color = (0, 255, 0)    # Green for trajectory lines
                        alpha = max(alpha, 0.2)       # Use the maximum alpha value

                    # Number of frames to process is from start_frame to min(findex, end_frame)
                    frames_to_process = findex - start_frame + 1

                    centers = []
                    corners_list = []
                    temp = []

                    # Extract corner points for the frames up to the current frame
                    for count in range(6, 6 + frames_to_process * 8):
                        temp.append(int(linePoints[count]))
                        if len(temp) == 8:
                            centers.append(RTcenter(temp))
                            corners_list.append(temp.copy())
                            temp = []

                    # Prepare lists for each corner point trajectory
                    corner0_list = []
                    corner1_list = []
                    corner2_list = []
                    corner3_list = []

                    for corners in corners_list:
                        corner0_list.append((corners[0], corners[1]))
                        corner1_list.append((corners[2], corners[3]))
                        corner2_list.append((corners[4], corners[5]))
                        corner3_list.append((corners[6], corners[7]))

                    # Draw filled polygons for the trajectory between frames
                    for i in range(1, len(corners_list)):
                        prev_corners = corners_list[i - 1]
                        curr_corners = corners_list[i]

                        # Create polygons for previous and current positions
                        poly_prev = np.array([
                            [prev_corners[0], prev_corners[1]],
                            [prev_corners[2], prev_corners[3]],
                            [prev_corners[4], prev_corners[5]],
                            [prev_corners[6], prev_corners[7]]
                        ], dtype=np.int32)

                        poly_curr = np.array([
                            [curr_corners[0], curr_corners[1]],
                            [curr_corners[2], curr_corners[3]],
                            [curr_corners[4], curr_corners[5]],
                            [curr_corners[6], curr_corners[7]]
                        ], dtype=np.int32)

                        # Combine polygons to form a quadrilateral between frames
                        combined_poly = np.vstack((poly_prev, poly_curr[::-1]))

                        # Draw the filled polygon on the overlay
                        cv2.fillConvexPoly(overlay, combined_poly, fill_color)

                    # Store the trajectory lines to draw after blending
                    for c_list in [corner0_list, corner1_list, corner2_list, corner3_list]:
                        for i in range(1, len(c_list)):
                            x_prev, y_prev = c_list[i - 1]
                            x_curr, y_curr = c_list[i]
                            # Store the line to draw later
                            trajectory_lines.append(((x_prev, y_prev), (x_curr, y_curr), trajectory_color))

                    # Draw box and center at the start position
                    if len(corners_list) > 0:
                        # Start position
                        start_pts = corners_list[0]
                        start_corners = [
                            (start_pts[0], start_pts[1]),
                            (start_pts[2], start_pts[3]),
                            (start_pts[4], start_pts[5]),
                            (start_pts[6], start_pts[7])
                        ]
                        cv2.polylines(overlay, [np.array(start_corners)], isClosed=True, color=box_color, thickness=2)

                        start_center = centers[0]
                        cv2.circle(overlay, (start_center[0], start_center[1]), 7, center_color, -1)
                        cv2.circle(overlay, (start_center[0], start_center[1]), 11, center_color, 2)

                    # Draw box and center at the current position
                    if len(corners_list) > 0:
                        # Current position
                        end_pts = corners_list[-1]
                        end_corners = [
                            (end_pts[0], end_pts[1]),
                            (end_pts[2], end_pts[3]),
                            (end_pts[4], end_pts[5]),
                            (end_pts[6], end_pts[7])
                        ]
                        cv2.polylines(overlay, [np.array(end_corners)], isClosed=True, color=box_color, thickness=2)

                        end_center = centers[-1]
                        cv2.circle(overlay, (end_center[0], end_center[1]), 7, center_color, -1)
                        cv2.circle(overlay, (end_center[0], end_center[1]), 11, center_color, 2)

        # Blend the overlay with the original frame only if drawing was performed
        if drawing_performed:
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

            # Now draw the trajectory lines directly on the frame after blending
            for line in trajectory_lines:
                pt1, pt2, color = line
                cv2.line(frame, pt1, pt2, color, thickness=2)

        ### Add Tracking lines ###
        colors = [(50,0,255), (50,138,255), (50,255,255), (255,255,235), (50,255,50), (255,235,50), (255,50,235), (255,50,50)]
               
        pos = np.zeros(8, np.int)
        # 0:行人(紅) 1:自行車(橘) 2:機車(黃) 3:小客車(白) 4:貨車(綠) 5:大客車(水藍) 6:聯結車頭(粉紅) 7:聯結車身(藍)
        typecode = "pumctbhg"

        for j in range(0, len(self.V) ):
            if findex >= int(self.V[j][1]) and findex <= int(self.V[j][2]):           
                idx = 6+8*(findex-int(self.V[j][1]))   
                k = 0
                for k in range(0, 8):
                    pos[k] = int(self.V[j][idx+k])
                    
                if pos[0] > 0:    

                    thickness = 2
                    if self.main_window.showTrackingBool:
                        cv2.line(frame, (pos[0], pos[1]), (pos[2], pos[3]), (0, 0, 255), thickness)
                        cv2.line(frame, (pos[2], pos[3]), (pos[4], pos[5]), (255, 0, 0), thickness)
                        # cv2.line(frame, (pos[2], pos[3]), (pos[4], pos[5]), colors[typecode.find(str(self.V[j][5]))], 4)
                        cv2.line(frame, (pos[4], pos[5]), (pos[6], pos[7]), colors[typecode.find(str(self.V[j][5]))], thickness)
                        cv2.line(frame, (pos[6], pos[7]), (pos[0], pos[1]), colors[typecode.find(str(self.V[j][5]))], thickness)       

                    if self.main_window.displayType :
                        cv2.putText(frame, str(self.V[j][0])+", "+self.V[j][3]+">"+self.V[j][4], (int((pos[0]+pos[4])/2)-50, int((pos[1]+pos[5])/2)+10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 3)
                        cv2.putText(frame, str(self.V[j][0])+", "+self.V[j][3]+">"+self.V[j][4], (int((pos[0]+pos[4])/2)-50, int((pos[1]+pos[5])/2)+10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

                    elif len(self.main_window.TIVIsampleList)!=0 and int(self.V[j][0] == self.main_window.TIVIsampleList[self.main_window.currentIssueIndex].split(',')[0]) :
                        cv2.putText(frame, str(self.V[j][0])+", "+self.V[j][3]+">"+self.V[j][4], (int((pos[0]+pos[4])/2)-50, int((pos[1]+pos[5])/2)+10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 3)
                        cv2.putText(frame, str(self.V[j][0])+", "+self.V[j][3]+">"+self.V[j][4], (int((pos[0]+pos[4])/2)-50, int((pos[1]+pos[5])/2)+10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

        if self.main_window.show : # display yolo detect.
            new_colors = [(0,0,255), (0,128,255), (0,255,255), (255,40,255), (0,255,0), (255,100,0), (255,0,100), (100,0,0)] 
            line = self.main_window.currentTIVP8cls[int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1]
            det_list = line.split(" ")
            det_list = det_list[1:] # 移除第一個frame
            while len(det_list) >= 9:  # 當還有足夠的數據進行處理
                cls = int(det_list.pop(0)) # 取得分類
                conf = det_list.pop(0) # 取得信心
                pts = [int(x) for x in det_list[0:8]] # 取得點座標
                det_list = det_list[8:] # 移除已處理數據
                thickness = 2
                # 畫出方框
                cv2.polylines(frame, [np.array([(pts[i], pts[i+1]) for i in range(0,8,2)])], isClosed=True, color=new_colors[cls], thickness=thickness)
                # 將首個框線顏色固定為紅色
                cv2.line(frame, (pts[0], pts[1]), (pts[2], pts[3]), (0, 0, 255), thickness=thickness)
                # 繪製文字
                cv2.putText(frame, typecode[cls], (pts[0], pts[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, new_colors[cls], 2)

        return frame
    Slot()
    def qtFrameDisplay(self, frame):
        # Ensure the frame is in the correct format and contiguous
        show = frame[..., ::-1].copy()  # Convert BGR to RGB and make contiguous

        height, width, channel = show.shape
        bytes_per_line = 3 * width

        # Create QImage from numpy data
        show_image = QImage(show.data, width, height, bytes_per_line, QImage.Format_RGB888)

        # Create QPixmap from QImage
        pixmap = QPixmap.fromImage(show_image)

        # Set scaled contents to True to let QLabel handle scaling
        self.main_window._window.display.setScaledContents(True)
        self.main_window._window.display.setPixmap(pixmap)
    Slot()
    def play(self):       
        self.play_bool = True

        video_FPS = 0
        if self.cap.isOpened() :
            video_FPS = int(self.cap.get(cv2.CAP_PROP_FPS))

        # print(video_FPS)
        while self.cap.isOpened() and self.play_bool:
            
            self.capReadRet, self.capFrame = self.cap.read()
            if not self.capReadRet :
                break
            nowFream = self.cap.get(cv2.CAP_PROP_POS_FRAMES) - 1
            # print(nowFream)
            tempFrame = self.capFrame.copy()
            self.frameDisplay(tempFrame)

            QtTest.QTest.qWait(video_FPS)
    Slot()
    def pause(self):
        self.play_bool = False
    Slot()
    def setStartFrame(self):
        self.main_window.currentStartID = self.main_window.currentVideoIndex
        # set start frame.
        self.setKey()
        self.main_window.cutInfoLsit[self.main_window.currentVideoIndex].setStart(self.cap.get(cv2.CAP_PROP_POS_FRAMES) - 1)
        if self.main_window.cutInfoLsit[self.main_window.currentVideoIndex].getEnd() == -1 :
            self.resetSetEndFrame(self.main_window.currentVideoIndex)
        # before check.
        for i in range(0,self.main_window.currentVideoIndex) :
            self.ignoreVideo(i)
        # after start check.

        for i in range(self.main_window.currentVideoIndex + 1 ,self.main_window.currentEndID) :
            self.resetSetKeyFrame(i)
            self.resetSetStartFrame(i)
            self.resetSetEndFrame(i)

        self.displayInfo(1)
        self.save()
    Slot()
    def setEndFrame(self):
        self.main_window.currentEndID = self.main_window.currentVideoIndex
        # set end frame.
        if self.main_window.cutInfoLsit[self.main_window.currentVideoIndex].getStart() == -1 :
            self.main_window.cutInfoLsit[self.main_window.currentVideoIndex].setStart(0)
        self.main_window.cutInfoLsit[self.main_window.currentVideoIndex].setEnd(self.cap.get(cv2.CAP_PROP_POS_FRAMES) - 1)
        # before check.
        for i in range(self.main_window.currentStartID + 1 , self.main_window.currentVideoIndex) :
            self.resetSetStartFrame(i)
            self.resetSetEndFrame(i)
        # after end frame, ignore Videos.
        for i in range(self.main_window.currentVideoIndex + 1 ,len(self.main_window.cutInfoLsit)) :
            self.ignoreVideo(i)

        
        self.displayInfo(1)
        self.save()
    Slot()
    def setKey(self):
        self.main_window.cutInfoLsit[self.main_window.currentVideoIndex].setKey(self.cap.get(cv2.CAP_PROP_POS_FRAMES) - 1)
        for i in range(0,len(self.main_window.cutInfoLsit)) :
            if i != self.main_window.currentVideoIndex :
                self.main_window.cutInfoLsit[i].setKey(-1)
        self.displayInfo(1)
    Slot()
    def resetSetKeyFrame(self,index):
        self.main_window.cutInfoLsit[index].setKey(-1)
        self.displayInfo(1)
    Slot()
    def resetSetStartFrame(self, index):
        self.main_window.cutInfoLsit[index].setStart(0)
        self.displayInfo(1)
    Slot()
    def resetSetEndFrame(self, index):
        cap = cv2.VideoCapture(os.path.join( os.path.abspath(self.droneFolderPath), self.main_window.videolist[index]))
        self.main_window.cutInfoLsit[index].setEnd(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        self.displayInfo(1)
    Slot()
    def ignoreVideo(self, index):
        self.main_window.cutInfoLsit[index].setKey(-1)
        self.main_window.cutInfoLsit[index].setStart(-1)
        self.main_window.cutInfoLsit[index].setEnd(-1)
        self.displayInfo(1)
    Slot()
    def fpsback100(self) :
        if self.main_window.scheduleType == 'off' :
            self.play_bool = False
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.cap.get(cv2.CAP_PROP_POS_FRAMES) - 101 )
        if self.cap.isOpened() :
            ret, self.capFrame = self.cap.read()
            if ret:                
                tempFrame = self.capFrame.copy()
                self.frameDisplay(tempFrame)
    Slot()
    def fpsback1(self) :
        if self.main_window.scheduleType == 'off' :
            self.play_bool = False
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.cap.get(cv2.CAP_PROP_POS_FRAMES) - 2 )
        if self.cap.isOpened() :
            ret, self.capFrame = self.cap.read()
            if ret:                
                tempFrame = self.capFrame.copy()
                self.frameDisplay(tempFrame)
    Slot()
    def fpsnext100(self) :
        if self.main_window.scheduleType == 'off' :
            self.play_bool = False
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.cap.get(cv2.CAP_PROP_POS_FRAMES) + 99 )
        if self.cap.isOpened() :
            ret, self.capFrame = self.cap.read()
            if ret:                
                tempFrame = self.capFrame.copy()
                self.frameDisplay(tempFrame)
    Slot()
    def fpsnext1(self) :
        if self.main_window.scheduleType == 'off' :
            self.play_bool = False
        if self.cap.isOpened() :
            ret, self.capFrame = self.cap.read()
            if ret:                
                tempFrame = self.capFrame.copy()
                self.frameDisplay(tempFrame)
    Slot()
    def jump(self) :
        self.play_bool = False
        jumpframe = 0
        if self.main_window.TIVPmode == 3 and self.main_window._window.FPS.text()[0] == 'i':
            # 添加手動設定目標track id進 issue list
            print(f"Add Tracking ID [{self.main_window._window.FPS.text()[1:]}] to TIVP Issue list.")
            
            temp = ""
            for i in range(0, len(self.V)):
                if self.V[i][0] == self.main_window._window.FPS.text()[1:]:
                    for m in range(0,6) :
                        temp += self.V[i][m] + ","
                    jumpframe = int(self.V[i][1])
            if temp == "" :
                print(f"Error >> Tracking ID invalid : {self.main_window._window.FPS.text()[1:]}")
            else :
                self.main_window.TIVIsampleList.append(temp)
                self.currentIssueIndex = len(self.main_window.TIVIsampleList) - 1
                self.displayInfo(4)

        else :
            jumpframe = int(self.main_window._window.FPS.text())
            if jumpframe > self.cap.get(cv2.CAP_PROP_FRAME_COUNT) :
                jumpframe = self.cap.get(cv2.CAP_PROP_FRAME_COUNT) -1

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, jumpframe)
        if self.cap.isOpened() :
            ret, self.capFrame = self.cap.read()
            if ret:                
                tempFrame = self.capFrame.copy()
                self.frameDisplay(tempFrame)
    Slot()
    def save(self):
        if self.cuttingWarning() == False :
            f = open(self.main_window.cutinfo_txt, 'w')
            
            for i in range(0,self.main_window.videoLen) :
                out = ''
                out = out + str(self.main_window.cutInfoLsit[i].getKey()) + '\t'
                out = out + str(self.main_window.cutInfoLsit[i].getStart()) + '\t'
                out = out + str(self.main_window.cutInfoLsit[i].getEnd()) + '\n'
                f.write(out)

            f.close()
            logger.info("[Step 0] ->> Cuttting Set file Save :" + self.main_window.cutinfo_txt)
    Slot()
    def stop(self):
        self.play_bool = False
        if self.main_window.scheduleType == 'run':
            self.cap.release()

            self.main_window.currentScheduleIndex = self.main_window.currentScheduleIndex + 1
            self.displayInfo(3)
            self.main_window.ScheduleManager.StartSchedule()
        else :
            self.cap.release()
            print("stop")
    Slot()
    def video_position(self, video_position):
        fream = int((self.allFream/100)*video_position)     
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, fream)
        if self.cap.isOpened() :
            ret, frame = self.cap.read()

            fps = str(self.cap.get(cv2.CAP_PROP_POS_FRAMES) - 1)
            cv2.putText(frame, fps, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3, cv2.LINE_AA)
            self.main_window._window.FPS.setText(fps)
            self.frameDisplay(frame)
    def cuttingWarning(self):
        err = False
        keyCount = 0 
        for i in range(0,len(self.main_window.cutInfoLsit)) :
            if self.main_window.cutInfoLsit[i].getKey() != -1 :
                keyCount = keyCount + 1
            if self.main_window.cutInfoLsit[i].getStart() >= self.main_window.cutInfoLsit[i].getEnd() and self.main_window.cutInfoLsit[i].getEnd() != -1 and self.main_window.cutInfoLsit[i].getStart() != -1:
                msgBox = QMessageBox()
                msgBox.setWindowTitle("Warning : Video Number : [" + str(i+1) + "]")
                msgBox.setText("Fream cutting fail.\nStart Frame must be early then End Frame.")
                msgBox.exec()
                err = True          
            
        if keyCount > 1 :
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Warning")
            msgBox.setText("KeyFream only can set one.\n" + "You have set" + str(keyCount) + 'KeyFream.')            
            msgBox.exec()
            err = True

        if keyCount < 1 :
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Warning")
            msgBox.setText("No KeyFream Setting. You must set one KeyFream.")
            msgBox.exec()
            err = True

        return err

class CutInfo() :
    def __init__(self):
        self.key = -1
        self.start = -1
        self.end = -1

    def setKey(self, key) :        
        self.key = int(key)
    
    def setStart(self, start) :
        self.start = int(start)
    
    def setEnd(self,end):
        self.end = int(end)

    def getKey(self):
        return self.key
    
    def getStart(self):
        return self.start

    def getEnd(self):
        return self.end




