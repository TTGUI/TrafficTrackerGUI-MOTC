import PySide2
import numpy as np
from PySide2 import QtCore
from PySide2.QtCore import QFile, QProcess, QTimer
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QFont, QImage, QPixmap, QColor, QPalette, QIcon
from PySide2.QtWidgets import QFileDialog, QMessageBox, QDialog
from Model.tool import TrackIntegrityVerificationTool
from pathlib import Path

# https://github.com/vispy/vispy/blob/main/vispy/app/backends/_pyside2.py
from PySide2 import QtTest
if not hasattr(QtTest.QTest, 'qWait'):
    @staticmethod
    def qWait(msec):
        import time
        start = time.time()
        PySide2.QtWidgets.QApplication.processEvents()
        while time.time() < start + msec * 0.001:
            PySide2.QtWidgets.QApplication.processEvents()
    QtTest.QTest.qWait = qWait

from logs import logger
from config import conf
from Cont import controller
from pathlib import Path

import cv2
import os

from .ui_setup import load_ui
from .ui_setupFont import set_window_title, set_font, reset_ui_labels
from .ui_setupButtons import setup_all_buttons

# WARNING : def_setResultFolder() have a potentiality error for path setting when code running on LunixOS

class MainWindow(object):

    def __init__(self, parent=None):
        """Main window, holding all user interface including.
        Args:
          parent: parent class of main window
        Returns:
          None
        Raises:
          None
        """
        # Main Setting
        self.actionName = "inital_action_name"
        self.resultPath = "./result/"

        # Deveploer Bar
        self.stabMode = conf.getStabMode() # 'CPU' 'GPU'
        self.yoloModel = conf.getYoloModel() #  20211109172733_last_200_1920.pt / ect.
        self.TIVPmode = conf.getTIVPMode() # <1> <2>

        # schedule
        self.scheduleType = 'off' # 'off' 'edit' 'run'
        self.currentScheduleIndex = 0
        self.ScheduleList = []
        self.scheduleLoadPath = ""
        self.scheduleSavePath = ""
        self.scheduleName = "Default"
        self.scheduleTIVFolderPath = ""
        self.scheduleTIVFile = ""

        # player
        self.play_bool = False
        self.currentStep = -1
        self.page = 0
        self.pageLen = 10

        # Prepare
        self.video_init = False
        self.droneFolderPath = "./data"
        self.cutinfo_txt = self.resultPath + self.actionName + "_cutInfo.txt"
        self.currentStartID = -1
        self.currentEndID = -1

        # Kstabilization
        self.stab_input = self.droneFolderPath
        self.stab_output = self.resultPath + self.actionName + "_stab.mp4"
        self.show = True
        

        # Mtracking 
        self.stab_video = self.stab_output
        self.yolo_txt = self.resultPath+ self.actionName +"_stab_8cls.txt"
        self.tracking_csv = self.resultPath + self.actionName + ".csv"

        # NBackground
        self.background_img = self.resultPath+ self.actionName +"_background.jpg" # English Path only....

        # OdrawIO & PIOadded
        self.section = conf.getSection_mode()
        self.gateLineIO_txt = self.resultPath + self.actionName + "_IO.txt"
        self.gate_tracking_csv = self.resultPath + self.actionName + "_gate.csv"

        # QReplay
        self.result_video = self.resultPath + self.actionName + "_result.avi"
        self.displayType = True


        # TIV
        self.singelTIVpath = self.resultPath + self.actionName + "_TIV.csv"
        self.showTrackingBool = True

        # UI
        self._window = None
        self.setup_ui()

        """
        YOU ALOS NEED TO MODIFY FUNCTION 'changeActionName'
        """

    @property
    def window(self):
        """The main window object"""
        return self._window

    def setup_ui(self):
        self._window = load_ui(self._window)
        self.set_font()
        setup_all_buttons(self._window, self)

    def set_font(self):
        """Set window title, icon, and fonts"""
        set_window_title(self._window, conf, self.stabMode, self.yoloModel, self.section)
        set_font(self._window)
        reset_ui_labels(self._window)




    def set_video(self, type):
        if type == 1 : # Step 0 Cut Info Player Mode
            self.video_init = True
            self.play_bool = False
            self.currentVideoIndex = 0
            self.videolist = os.listdir(self.droneFolderPath)
            self.videolist.sort()
            self.videoLen = len(self.videolist)
            self.cutInfoLsit = []
            for i in range( 0 ,self.videoLen ):
                tempCut = CutInfo()            

                cap = cv2.VideoCapture(os.path.join( os.path.abspath(self.droneFolderPath), self.videolist[i]))

                tempCut.setStart(0)
                tempCut.setEnd(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
                cap.release()
                self.cutInfoLsit.append(tempCut)

            self.displayInfo(2)

            out = ''
            for i in range(0,self.videoLen) :
                out = out + '[' + str(i+1) +'] '+ self.videolist[i] + '\n'

            msgBox = QMessageBox()
            msgBox.setWindowTitle("Video Load")
            msgBox.setText(out)
            msgBox.exec()

            self.load()
        elif type == 2 : # Step 9 TIVP Real Time Mode
            self.video_init = True
            self.play_bool = False
            self.cap = cv2.VideoCapture(self.stab_video)
            print("LOAD : " + str(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))+ ' frames')
            self.allFream = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))


    #### Developer Options ################################################################
    @QtCore.Slot()
    def changeStabMode(self):
        if self.stabMode == 'CPU':
            self.stabMode = 'GPU'
            conf.setStabMode('GPU')
            self._window.bar_2.setText("Change Stabilazation Mode | [ GPU ]")
            self._window.step1_btn.setText('[STEP 1] (G)\nStable')
        elif self.stabMode == 'GPU':
            self.stabMode = 'CPU'
            conf.setStabMode('CPU')
            self._window.bar_2.setText("Change Stabilazation Mode | [ CPU ]")
            self._window.step1_btn.setText('[STEP 1] (C)\nStable')
        self._window.title.setText(str(conf.RTVersion()) + " | " + self.stabMode + " | " + self.yoloModel + " | " + self.section)
    
    @QtCore.Slot()
    def changeYoloModel(self):
        actName = QFileDialog.getOpenFileName(self._window, 'Select file to set Yolo Model.', "./Model/YOLOv4/weights")

        tempName = actName[0].split('/')

        if tempName[-1] != '':
        
            print(tempName[-1])
            self.yoloModel = tempName[-1]
            self._window.title.setText(str(conf.RTVersion()) + " | " + self.stabMode + " | " + self.yoloModel + " | " + self.section)
            conf.setYoloModel(self.yoloModel)
        else :
            print("[CANCEL] YoloModel change cancel.")

    @QtCore.Slot()
    def changeTIVPbMode(self):
        if self.TIVPmode == 1:
            self.TIVPmode = 2
            conf.setTIVPMode(2)
            self._window.bar_4.setText("Change TIVP Mode | [ Image ]")
            self._window.TIVPrinter_btn.setText('[STEP 9]\nTIV Printer (I)')
        elif self.TIVPmode == 2:
            self.TIVPmode = 3
            conf.setTIVPMode(3)
            self._window.bar_4.setText("Change TIVP Mode | [ Real Time Display ]")
            self._window.TIVPrinter_btn.setText('[STEP 9]\nTIV Printer (R)')
        elif self.TIVPmode == 3:
            self.TIVPmode = 1
            conf.setTIVPMode(1)
            self._window.bar_4.setText("Change TIVP Mode | [ Video ]")
            self._window.TIVPrinter_btn.setText('[STEP 9]\nTIV Printer (V)')
        self.renewScheduleBoard()
    def changeTrackingSet(self):
        self.CTS_dialog = QDialog()
        ui_file_name = './View/CTS_dialog.ui'
        file = QFile(ui_file_name)
        loader = QUiLoader()
        self.CTS_dialog = loader.load(file)
        file.close()
        self.CTS_dialog.setWindowTitle('change Tracking Setting')
        self.CTS_dialog.CTS_trackingSetText.setText('Enter tracking setting : max_age, min_hits, iou_threshold')
        self.CTS_dialog.CTS_label_Trk1.setText(f'大車 (汽車,卡車,公車) Set\nDefault : (10, 2, 0.05)\nCurrent : {conf.getTrk1_Set()}')
        self.CTS_dialog.CTS_label_Trk2.setText(f'小車 (人,機車,自行車) Set\nDefault : (10, 2, 0.1)\nCurrent : {conf.getTrk2_Set()}')
        self.CTS_dialog.CTS_trackingSetText2.setText('Ex : max_age=10, min_hits=2, iou_threshold=0.01, type `10,2,0.01`.')
        self.CTS_dialog.CTS_submitButton.setText('Submit')
        self.CTS_dialog.CTS_submitButton.clicked.connect(self.submitTrackingSet)

        self.CTS_dialog.show()

    def submitTrackingSet(self):
        if self.CTS_dialog.CTS_Edit_1.text() != '':
            trk1 = self.CTS_dialog.CTS_Edit_1.text()
            print("Trackers1 Set Changed : ",trk1.replace(" ", ""))
            conf.setTrk1_Set(trk1)

        if self.CTS_dialog.CTS_Edit_2.text() != '':
            trk2 = self.CTS_dialog.CTS_Edit_2.text()        
            conf.setTrk2_Set(trk2)
            print("Trackers2 Set Changed : ",trk2.replace(" ", ""))

        self.CTS_dialog.close()

    def changeSectionMode(self):
        if self.section == "intersection":
            self.section = "roadsection"
            conf.setSection_mode(self.section)
        elif self.section == "roadsection":
            self.section = "intersection"
            conf.setSection_mode(self.section)
        self._window.title.setText(str(conf.RTVersion()) + " | " + self.stabMode + " | " + self.yoloModel + " | " + self.section)
        if self.section == 'intersection':
            self._window.step5_btn.setText('[STEP 5] (I)\nDrawIO')
        elif self.section == 'roadsection':
            self._window.step5_btn.setText('[STEP 5] (R)\nDrawIO')

    def changeOutputWH(self):
        self.WH_dialog = QDialog()
        ui_file_name = './View/WH_dialog.ui'
        file = QFile(ui_file_name)
        loader = QUiLoader()
        self.WH_dialog = loader.load(file)
        file.close()
        self.WH_dialog.setWindowTitle('Change output video width & height')
        self.WH_dialog.WH_Height.setText(f'{conf.getOutput_height()}')
        self.WH_dialog.WH_Width.setText(f'{conf.getOutput_width()}')
        self.WH_dialog.WH_ok_btn.clicked.connect(self.setOutputWH)
        self.WH_dialog.show()

    def setOutputWH(self):
        if self.WH_dialog.WH_HeightEdit.text() != '':
            height = self.WH_dialog.WH_HeightEdit.text()
            conf.setOutput_height(height)
            print(f"output height change to : {height}")
        if self.WH_dialog.WH_WidthEdit.text() != '':
            width = self.WH_dialog.WH_WidthEdit.text()
            conf.setOutput_width(width) 
            print(f"output width change to : {width}")
        self.WH_dialog.WH_Height.setText(f'{conf.getOutput_height()}')
        self.WH_dialog.WH_Width.setText(f'{conf.getOutput_width()}')

    def changeTIVsetting(self):        
        self.TIV_dialog = QDialog()
        ui_file_name = './View/TIV_dialog.ui'
        file = QFile(ui_file_name)
        loader = QUiLoader()
        self.TIV_dialog = loader.load(file)
        file.close()
        self.TIV_dialog.setWindowTitle('Change TIV Setting')
        self.TIV_dialog.TIV_IingoreFrames.setText(f'{conf.getTIV_ignoreFrame()}')
        self.TIV_dialog.TIV_ExtendPrintFrame.setText(f'{conf.getTIVP_ExtendPrintFrame()}')
        self.TIV_dialog.TIV_ok_btn.clicked.connect(self.setTIVSetting)
        self.TIV_dialog.show()

    def setTIVSetting(self):
        if self.TIV_dialog.TIV_IingoreFramesEdit.text() != '':
            Iingore = self.TIV_dialog.TIV_IingoreFramesEdit.text()
            conf.setTIV_ignoreFrame(Iingore)
            print(f"TIV Iingore Frames change to : {Iingore}")
        if self.TIV_dialog.TIV_ExtendPrintFrameEdit.text() != '':
            ExtendPrintFrame = self.TIV_dialog.TIV_ExtendPrintFrameEdit.text()
            conf.setTIVP_ExtendPrintFrame(ExtendPrintFrame) 
            print(f"output width change to : {ExtendPrintFrame}")
        self.TIV_dialog.TIV_IingoreFrames.setText(f'{conf.getTIV_ignoreFrame()}')
        self.TIV_dialog.TIV_ExtendPrintFrame.setText(f'{conf.getTIVP_ExtendPrintFrame()}')


    #### Player Board ################################################################

    @QtCore.Slot()
    def frameDisplay(self, frame) :

        if self.TIVPmode == 3 and self.currentStep == 9 :
            frame = self.issueFramePrint(frame)

        fps = str(self.cap.get(cv2.CAP_PROP_POS_FRAMES) - 1)
        cv2.putText(frame, fps, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 6, cv2.LINE_AA)
        cv2.putText(frame, fps, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3, cv2.LINE_AA)
        self._window.FPS.setText(fps[:-2])
        nowFream = self.cap.get(cv2.CAP_PROP_POS_FRAMES) - 1
        self._window.timingSlider.setValue(int((nowFream/self.allFream)*100))
        frame = cv2.resize(frame, (1440, 810))
        show = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        showImage = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
        self._window.display.setScaledContents(True) # 自適應邊框  
        self._window.display.setPixmap(QPixmap.fromImage(showImage))

    def issueFramePrint(self, frame):
        def RTcenter(points):
            ans = []
            
            x = (int(points[0]) + int(points[4]) ) / 2
            y = (int(points[1]) + int(points[5]) ) / 2
            ans.append(int(x))
            ans.append(int(y))
            return ans


        ### Add IO lines ###
        V2 = self.TIVioLines[0].split(",")
        V3 = self.TIVioLines[1].split(",")
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

        for j in range(2, len(self.TIVioLines)):
            V4 = self.TIVioLines[j].split(",")
            k = 0
            for k in range(0, len(V4)-3, 2):
                cv2.line(frame, (int(V4[k]), int(V4[k+1])), (int(V4[k+2]), int(V4[k+3])), (255, 0, 0), 2)

        ### Add Issue Tracking ###



        findex = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))  # Current frame index

        # Prepare a set of issue IDs from self.TIVIsampleList
        # Assuming that self.TIVIsampleList contains strings where the issue ID is the first element when split by ','
        issue_ids_to_draw = set()
        for issue_str in self.TIVIsampleList:
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
                    if issue_id == int(self.TIVIsampleList[self.currentIssueIndex].split(',')[0]):
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
                    if self.showTrackingBool:
                        cv2.line(frame, (pos[0], pos[1]), (pos[2], pos[3]), (0, 0, 255), thickness)
                        cv2.line(frame, (pos[2], pos[3]), (pos[4], pos[5]), (255, 0, 0), thickness)
                        # cv2.line(frame, (pos[2], pos[3]), (pos[4], pos[5]), colors[typecode.find(str(self.V[j][5]))], 4)
                        cv2.line(frame, (pos[4], pos[5]), (pos[6], pos[7]), colors[typecode.find(str(self.V[j][5]))], thickness)
                        cv2.line(frame, (pos[6], pos[7]), (pos[0], pos[1]), colors[typecode.find(str(self.V[j][5]))], thickness)       

                    if self.displayType :
                        cv2.putText(frame, str(self.V[j][0])+", "+self.V[j][3]+">"+self.V[j][4], (int((pos[0]+pos[4])/2)-50, int((pos[1]+pos[5])/2)+10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 3)
                        cv2.putText(frame, str(self.V[j][0])+", "+self.V[j][3]+">"+self.V[j][4], (int((pos[0]+pos[4])/2)-50, int((pos[1]+pos[5])/2)+10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

                    elif len(self.TIVIsampleList)!=0 and int(self.V[j][0] == self.TIVIsampleList[self.currentIssueIndex].split(',')[0]) :
                        cv2.putText(frame, str(self.V[j][0])+", "+self.V[j][3]+">"+self.V[j][4], (int((pos[0]+pos[4])/2)-50, int((pos[1]+pos[5])/2)+10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 3)
                        cv2.putText(frame, str(self.V[j][0])+", "+self.V[j][3]+">"+self.V[j][4], (int((pos[0]+pos[4])/2)-50, int((pos[1]+pos[5])/2)+10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

        if self.show : # display yolo detect.
            new_colors = [(0,0,255), (0,128,255), (0,255,255), (255,40,255), (0,255,0), (255,100,0), (255,0,100), (100,0,0)] 
            line = self.currentTIVP8cls[int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1]
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

    @QtCore.Slot()
    def load(self):
        if self.video_init == False :
            self._window.cutinfo.setText('Error : video are not set yet.')
            return

        self.displayInfo(1)
        self.cap = cv2.VideoCapture(os.path.join( os.path.abspath(self.droneFolderPath), self.videolist[self.currentVideoIndex]))
        print("LOAD : " + str(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))+ ' frames')
        self.allFream = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.video_init = True

    @QtCore.Slot()
    def play(self):       
        self.play_bool = True

        video_FPS = 0
        if self.cap.isOpened() :
            video_FPS = int(self.cap.get(cv2.CAP_PROP_FPS))

        # print(video_FPS)
        while self.cap.isOpened() and self.play_bool:
            
            ret, self.capFrame = self.cap.read()
            if not ret :
                break
            nowFream = self.cap.get(cv2.CAP_PROP_POS_FRAMES) - 1
            # print(nowFream)
            tempFrame = self.capFrame.copy()
            self.frameDisplay(tempFrame)

            QtTest.QTest.qWait(video_FPS)
         

    @QtCore.Slot()
    def pause(self):
        self.play_bool = False

    @QtCore.Slot()
    def stop(self):
        self.play_bool = False
        if self.scheduleType == 'run':
            self.cap.release()

            self.currentScheduleIndex = self.currentScheduleIndex + 1
            self.displayInfo(3)
            self.StartSchedule()
            
            # cv2.destroyAllWindows()
                
        else :

            self.cap.release()
            cv2.destroyAllWindows()
            print("stop")

    @QtCore.Slot()
    def fpsback100(self) :
        if self.scheduleType == 'off' :
            self.play_bool = False
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.cap.get(cv2.CAP_PROP_POS_FRAMES) - 101 )
        if self.cap.isOpened() :
            ret, self.capFrame = self.cap.read()
            if ret:                
                tempFrame = self.capFrame.copy()
                self.frameDisplay(tempFrame)

    @QtCore.Slot()
    def fpsnext100(self) :
        if self.scheduleType == 'off' :
            self.play_bool = False
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.cap.get(cv2.CAP_PROP_POS_FRAMES) + 99 )
        if self.cap.isOpened() :
            ret, self.capFrame = self.cap.read()
            if ret:                
                tempFrame = self.capFrame.copy()
                self.frameDisplay(tempFrame)

    @QtCore.Slot()
    def fpsback1(self) :
        if self.scheduleType == 'off' :
            self.play_bool = False
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.cap.get(cv2.CAP_PROP_POS_FRAMES) - 2 )
        if self.cap.isOpened() :
            ret, self.capFrame = self.cap.read()
            if ret:                
                tempFrame = self.capFrame.copy()
                self.frameDisplay(tempFrame)
    
    @QtCore.Slot()
    def fpsnext1(self) :
        if self.scheduleType == 'off' :
            self.play_bool = False
        if self.cap.isOpened() :
            ret, self.capFrame = self.cap.read()
            if ret:                
                tempFrame = self.capFrame.copy()
                self.frameDisplay(tempFrame)

    @QtCore.Slot()
    def jump(self) :
        self.play_bool = False
        jumpframe = 0
        if self.TIVPmode == 3 and self._window.FPS.text()[0] == 'i':
            # 添加手動設定目標track id進 issue list
            print(f"Add Tracking ID [{self._window.FPS.text()[1:]}] to TIVP Issue list.")
            
            temp = ""
            for i in range(0, len(self.V)):
                if self.V[i][0] == self._window.FPS.text()[1:]:
                    for m in range(0,6) :
                        temp += self.V[i][m] + ","
                    jumpframe = int(self.V[i][1])
            if temp == "" :
                print(f"Error >> Tracking ID invalid : {self._window.FPS.text()[1:]}")
            else :
                self.TIVIsampleList.append(temp)
                self.currentIssueIndex = len(self.TIVIsampleList) - 1
                self.displayInfo(4)

        else :
            jumpframe = int(self._window.FPS.text())
            if jumpframe > self.cap.get(cv2.CAP_PROP_FRAME_COUNT) :
                jumpframe = self.cap.get(cv2.CAP_PROP_FRAME_COUNT) -1

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, jumpframe)
        if self.cap.isOpened() :
            ret, self.capFrame = self.cap.read()
            if ret:                
                tempFrame = self.capFrame.copy()
                self.frameDisplay(tempFrame)

    @QtCore.Slot()
    def video_position(self, video_position):
        fream = int((self.allFream/100)*video_position)     
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, fream)
        if self.cap.isOpened() :
            ret, frame = self.cap.read()

            fps = str(self.cap.get(cv2.CAP_PROP_POS_FRAMES) - 1)
            cv2.putText(frame, fps, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3, cv2.LINE_AA)
            self._window.FPS.setText(fps)
            self.frameDisplay(frame)

    @QtCore.Slot()
    def setKey(self):
        self.cutInfoLsit[self.currentVideoIndex].setKey(self.cap.get(cv2.CAP_PROP_POS_FRAMES) - 1)
        for i in range(0,len(self.cutInfoLsit)) :
            if i != self.currentVideoIndex :
                self.cutInfoLsit[i].setKey(-1)


        self.displayInfo(1)

    @QtCore.Slot()
    def setStartFrame(self):
        self.currentStartID = self.currentVideoIndex
        # set start frame.
        self.setKey()
        self.cutInfoLsit[self.currentVideoIndex].setStart(self.cap.get(cv2.CAP_PROP_POS_FRAMES) - 1)
        if self.cutInfoLsit[self.currentVideoIndex].getEnd() == -1 :
            self.resetSetEndFrame(self.currentVideoIndex)
        # before check.
        for i in range(0,self.currentVideoIndex) :
            self.ignoreVideo(i)
        # after start check.

        for i in range(self.currentVideoIndex + 1 ,self.currentEndID) :
            print(f"reset{i}")
            self.resetSetKeyFrame(i)
            self.resetSetStartFrame(i)
            self.resetSetEndFrame(i)

        self.displayInfo(1)
        
        self.save()


    @QtCore.Slot()
    def setEndFrame(self):
        self.currentEndID = self.currentVideoIndex
        # set end frame.
        if self.cutInfoLsit[self.currentVideoIndex].getStart() == -1 :
            self.cutInfoLsit[self.currentVideoIndex].setStart(0)
        self.cutInfoLsit[self.currentVideoIndex].setEnd(self.cap.get(cv2.CAP_PROP_POS_FRAMES) - 1)
        # before check.
        for i in range(self.currentStartID + 1 , self.currentVideoIndex) :
            self.resetSetStartFrame(i)
            self.resetSetEndFrame(i)
        # after end frame, ignore Videos.
        for i in range(self.currentVideoIndex + 1 ,len(self.cutInfoLsit)) :
            self.ignoreVideo(i)

        
        self.displayInfo(1)
        self.save()

    @QtCore.Slot()
    def resetSetKeyFrame(self,index):
        self.cutInfoLsit[index].setKey(-1)
        self.displayInfo(1)

    @QtCore.Slot()
    def resetSetStartFrame(self, index):
        self.cutInfoLsit[index].setStart(0)
        self.displayInfo(1)

    @QtCore.Slot()
    def resetSetEndFrame(self, index):
        cap = cv2.VideoCapture(os.path.join( os.path.abspath(self.droneFolderPath), self.videolist[index]))
        self.cutInfoLsit[index].setEnd(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        self.displayInfo(1)

    @QtCore.Slot()
    def ignoreVideo(self, index):
        self.cutInfoLsit[index].setKey(-1)
        self.cutInfoLsit[index].setStart(-1)
        self.cutInfoLsit[index].setEnd(-1)
        self.displayInfo(1)

    def cuttingWarning(self):
        err = False
        keyCount = 0 
        for i in range(0,len(self.cutInfoLsit)) :
            if self.cutInfoLsit[i].getKey() != -1 :
                keyCount = keyCount + 1
            if self.cutInfoLsit[i].getStart() >= self.cutInfoLsit[i].getEnd() and self.cutInfoLsit[i].getEnd() != -1 and self.cutInfoLsit[i].getStart() != -1:
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


    #### Step Board ################################################################
    @QtCore.Slot()
    def setActionNameBtnText(self):
        out = ""
        counter = 0
        for i in range(0,len(self.actionName)):
            out = out + self.actionName[i]
            counter = counter + 1
            if counter == 23 :
                out = out + '\n'
                counter = 0

        self._window.ActionName_btn.setText("Edit Action Name\n[" + out + ']')

    @QtCore.Slot()
    def changeActionName(self) : # user odering actionName.

        self.actionName = self._window.ActionName_edit.text()

        self.cutinfo_txt = self.resultPath + self.actionName + "_cutInfo.txt"
        self.stab_input = self.droneFolderPath
        self.stab_output = self.resultPath + self.actionName + "_stab.avi"
        self.stab_video = self.stab_output
        self.yolo_txt = self.resultPath+ self.actionName +"_stab_8cls.txt"
        self.tracking_csv = self.resultPath + self.actionName + ".csv"
        self.gateLineIO_txt = self.resultPath + self.actionName + "_IO.txt"
        self.gate_tracking_csv = self.resultPath + self.actionName + "_gate.csv"
        self.result_video = self.resultPath + self.actionName + "_result.avi"
        self.background_img = self.resultPath+ self.actionName +"_background.jpg"
        self.singelTIVpath = self.resultPath + self.actionName + "_TIV.csv"

        self.setActionNameBtnText()

        logger.info(f"[ChangeActionName] ->> <{self.actionName}>")

    def flashActionName(self) : # program change actionName itself.
        self.cutinfo_txt = self.resultPath + self.actionName + "_cutInfo.txt"
        self.stab_input = self.droneFolderPath
        self.stab_output = self.resultPath + self.actionName + "_stab.avi"
        self.stab_video = self.stab_output
        self.yolo_txt = self.resultPath+ self.actionName +"_stab_8cls.txt"
        self.tracking_csv = self.resultPath + self.actionName + ".csv"
        self.gateLineIO_txt = self.resultPath + self.actionName + "_IO.txt"
        self.gate_tracking_csv = self.resultPath + self.actionName + "_gate.csv"
        self.result_video = self.resultPath + self.actionName + "_result.avi"
        self.background_img = self.resultPath+ self.actionName +"_background.jpg"
        self.singelTIVpath = self.resultPath + self.actionName + "_TIV.csv"
        
        self.setActionNameBtnText()
        self.setDroneFolderBtnText()
        self.setResultFolderBtnText()
   
    def selectName(self):
        actName = QFileDialog.getOpenFileName(self._window, 'Select file to set Action Name', self.resultPath)

        tempName = actName[0]
        if tempName == "" :
            print("[CANCEL] Select Action Name Cancel.")
        else :
            tempName = self.RT_actionNameWhitoutBackword(tempName)

            self._window.ActionName_edit.setText(os.path.basename(tempName))
            self.changeActionName()

    def RT_actionNameWhitoutBackword(self, inputAname) :
        tempName = inputAname
        backword = ["_gate.csv", "_TIV.csv", ".csv", "_background.jpg", "_cutInfo.txt", "_IO.txt", "_result.avi", "_result.mp4", "_stab.avi", "_stab.mp4", "_stab_8cls.txt" ]
        for i in range(0,len(backword)):
            backLen = -len(backword[i])
            if tempName[backLen:] == backword[i] :
                tempName = tempName[0:backLen]
        return tempName     

    @QtCore.Slot()
    def save(self):
        if self.cuttingWarning() == False :
            f = open(self.cutinfo_txt, 'w')
            
            for i in range(0,self.videoLen) :
                out = ''
                out = out + str(self.cutInfoLsit[i].getKey()) + '\t'
                out = out + str(self.cutInfoLsit[i].getStart()) + '\t'
                out = out + str(self.cutInfoLsit[i].getEnd()) + '\n'
                f.write(out)

            f.close()
            logger.info("[Step 0] ->> Cuttting Set file Save :" + self.cutinfo_txt)
            # self._window.cutinfo.setText("coutinfo save as\n" + self.cutinfo_txt)

    @QtCore.Slot()
    def show_btn_act(self):
        if self.scheduleType == 'off' and self.TIVPmode == 3 and self.currentStep == 9 : # TIVP real time mode edit by user.
            self._window.show_btn.setToolTip('[S9] Show yolo detect.')
        else:
            self._window.show_btn.setToolTip('[S1,3,7] Show process frame or background.')


        if self.show:
            self.show = False
            if self.scheduleType == 'off' and self.TIVPmode == 3 and self.currentStep == 9 : # TIVP real time mode edit by user.
                self._window.show_btn.setText('Hide Yolo detact.')
            else:
                self._window.show_btn.setText('BackGround')

        else :
            self.show = True
            if self.scheduleType == 'off' and self.TIVPmode == 3 and self.currentStep == 9 : # TIVP real time mode edit by user.
                self._window.show_btn.setText('Display Yolo detact.')
            else:
                self._window.show_btn.setText('Show')
        if self.scheduleType == 'off' and self.TIVPmode == 3 and self.currentStep == 9 and self.cap.isOpened() :
            tempFrame = self.capFrame.copy()
            self.frameDisplay(tempFrame)
    @QtCore.Slot()
    def DisplayType(self) :

        if self.displayType:
            self.displayType = False
            self._window.DisplayType_btn.setText('Hide ID')

        else :
            self.displayType = True
            self._window.DisplayType_btn.setText('Display ID')
        if self.scheduleType == 'off' and self.TIVPmode == 3 and self.currentStep == 9 and self.cap.isOpened() :
            tempFrame = self.capFrame.copy()
            self.frameDisplay(tempFrame)

    @QtCore.Slot()
    def showTracking(self):
        if self.showTrackingBool :
            self.showTrackingBool = False
            self._window.showTracking_btn.setText('Hide Tracking')

        else :
            self.showTrackingBool = True
            self._window.showTracking_btn.setText('Show Tracking')
        if self.scheduleType == 'off' and self.TIVPmode == 3 and self.currentStep == 9 and self.cap.isOpened() :
            tempFrame = self.capFrame.copy()
            self.frameDisplay(tempFrame)

    @QtCore.Slot()
    def droneFolder(self):
        folderpath = QFileDialog.getExistingDirectory(self._window, 'Select Folder of Drone Video', self.resultPath)
        if folderpath == "" :
            print("[CANCEL] Set Drone Folder Cancel.")
        else :
            flist = os.listdir(folderpath)
            if len(flist) == 0:
                print("<< Warinig : Your Drone Folder Has NO VIDEOS.")
            else:
                self.actionName = flist[0]
                self._window.ActionName_edit.setText(self.actionName)

            self.droneFolderPath = folderpath
            self.setDroneFolderBtnText()
            logger.info(f"[Set droneFolder] ->> {self.droneFolderPath}")
            self.changeActionName()

    def setDroneFolderBtnText(self):
        out = ""
        counter = 0
        for i in range(0,len(self.droneFolderPath)):
            out = out + self.droneFolderPath[i]
            counter = counter + 1
            if counter == 40 :
                out = out + '\n'
                counter = 0

        self._window.DroneFolder_btn.setText('Set Drone Folder\n['+ out +']')

    def openDroneFolder(self):
        if os.path.isdir(self.droneFolderPath) :
            if os.name == 'nt' :
                QProcess.startDetached('explorer', [os.path.normpath(self.droneFolderPath)])
            else :
                subprocess.call(['xdg-open', os.path.normpath(self.droneFolderPath)])
        else :
            print("<< Warinig : Your Result Folder is not exist.")

    @QtCore.Slot()
    def setResultFolder(self):
        temp = QFileDialog.getExistingDirectory(self._window, 'Select Folder to Result.', self.resultPath) + '/' # Warning : the path setting maybe can not runnung on Lunix OS
      
        if temp == "/" :
            print("[CANCEL] Set Result Folder Cancel.")
            
        else :
            self.resultPath = temp
            self.setResultFolderBtnText()
            logger.info(f"[Set resultFolder] ->> {self.resultPath}")
            self.changeActionName()

    def setResultFolderBtnText(self):
        out = ""
        counter = 0
        for i in range(0,len(self.resultPath)):
            out = out + self.resultPath[i]
            counter = counter + 1
            if counter == 40 :
                out = out + '\n'
                counter = 0

        self._window.setResultFolder_btn.setText('Set Result Folder\n['+ out +']')

    def openResultFolder(self):
        if os.path.isdir(self.resultPath) :
            if os.name == 'nt' :
                QProcess.startDetached('explorer', [os.path.normpath(self.resultPath)])
            else:
                subprocess.call(['xdg-open', os.path.normpath(self.resultPath)])
        else :
            print("<< Warinig : Your Result Folder is not exist.")

    def changeStep(self, sp):
        self.currentStep = sp
        self.renewScheduleBoard()

    @QtCore.Slot()
    def step0(self):
        self.changeStep(0)
        if self.scheduleType == 'edit' :
            print("Current Schedule Item Step >> 0 ")            
            self.AddScheudle()
        else :
            if self.scheduleType == 'off':
                print("[STEP 0]")
            if self.precursorCheck():
                
                self.currentEndID = -1
                self.currentStartID = len(os.listdir(self.droneFolderPath))

                self.set_video(1)
                self.play()
        
    @QtCore.Slot()
    def step1(self):
        self.changeStep(1)
        if self.scheduleType == 'edit' :
            print("Current Schedule Item Step >> 1 ")            
            self.AddScheudle()
        else :
            if self.scheduleType == 'off':
                print("[STEP 1]")
            if self.precursorCheck():
                controller.con_step1(self.stab_input, self.stab_output, self.show, self.cutinfo_txt, self.stabMode)
               
    @QtCore.Slot()
    def step2(self): # Yolo
        self.changeStep(2)
        if self.scheduleType == 'edit' :
            print("Current Schedule Item Step >> 2 ")            
            self.AddScheudle()
        else :
            if self.scheduleType == 'off':
                print("[STEP 2]")
            if self.precursorCheck():
                controller.con_step2(self.stab_video, self.yolo_txt, self.yoloModel )

    @QtCore.Slot()
    def step3(self): # Tracking
        self.changeStep(3)
        if self.scheduleType == 'edit' :
            print("Current Schedule Item Step >> 3 ")
            self.AddScheudle()
        else :
            if self.scheduleType == 'off':
                print("[STEP 3]")
            if self.precursorCheck():
                controller.con_step3(self.stab_video,self.yolo_txt,self.tracking_csv,self.show, conf.getTrk1_Set(), conf.getTrk2_Set())

    @QtCore.Slot()
    def step4(self): # BackGround
        self.changeStep(4)
        if self.scheduleType == 'edit' :
            print("Current Schedule Item Step >> 4 ")            
            self.AddScheudle()
        else :
            if self.scheduleType == 'off':
                print("[STEP 4]")
            if self.precursorCheck():
                controller.con_step4(self.stab_video,self.background_img)
            
    @QtCore.Slot()
    def step5(self): # DrawIO
        self.changeStep(5)
        if self.scheduleType == 'edit' :
            print("Current Schedule Item Step >> 5 ")            
            self.AddScheudle()
        else :  
            if self.scheduleType == 'off':
                print("[STEP 5]")
            if self.precursorCheck():
                controller.con_step5(self.gateLineIO_txt,self.background_img)

    @QtCore.Slot()
    def step6(self): # IO added
        self.changeStep(6)
        if self.scheduleType == 'edit' :
            print("Current Schedule Item Step >> 6 ")            
            self.AddScheudle()
        else :
            if self.scheduleType == 'off':
                print("[STEP 6]")
            if self.precursorCheck():    
                controller.con_step6(self.gateLineIO_txt, self.tracking_csv, self.gate_tracking_csv)

    @QtCore.Slot()
    def step7(self): # Replay
        self.changeStep(7)
        if self.scheduleType == 'edit' :
            print("Current Schedule Item Step >> 7 ")            
            self.AddScheudle()
        else :
            if self.scheduleType == 'off':
                print("[STEP 7]")
            if self.precursorCheck():
                controller.con_step7(self.stab_video, self.result_video, self.gate_tracking_csv, self.gateLineIO_txt, self.displayType, self.show)

    @QtCore.Slot()
    def step8_singleTIV(self):
        self.changeStep(8)
        if self.scheduleType == 'edit' :
            print("Current Schedule Item Step >> TIV ")            
            self.AddScheudle()
        else :
            if self.scheduleType == 'off':
                print("[STEP 8 - TIV]")
            if self.precursorCheck():
                return controller.con_TIVT(self.gate_tracking_csv, self.singelTIVpath)

    @QtCore.Slot()  
    def step9_TIVPrinter(self):
        self.changeStep(9)
        if self.scheduleType == 'edit' :
            print("Current Schedule Item Step >> TIVPrinter ")
            self.AddScheudle()
        else :
            if self.scheduleType == 'off':
                print("[STEP 9 - TIVP]")
            if self.TIVPmode == 3 :
                if self.precursorCheck():
                    def read_file(file_name):
                        with open(file_name, 'r') as f:
                            lines = f.readlines()
                        return lines
                    
                    self.currentTIVP8cls = read_file(self.yolo_txt)
                    self.TIVfileLoad()
            else :
                if self.precursorCheck():
                    controller.con_TIVP(self.singelTIVpath, self.gateLineIO_txt, self.stab_video, self.resultPath, self.actionName, self.gate_tracking_csv, self.background_img )  
    
    def TIVfileLoad(self):
        self.show = False
        if self.scheduleType == 'off' and self.TIVPmode == 3 and self.currentStep == 9 : # TIVP real time mode edit by user.
            self._window.show_btn.setToolTip('[S9] Show yolo detect.')
        else:
            self._window.show_btn.setToolTip('[S1,3,7] Show process frame or background.')
        self._window.show_btn.setText('Hide Yolo detact.')
        self.set_video(2) # Step 9 TIVP Real Time Mode
        self.currentIssueIndex = 0
        f = open(self.singelTIVpath, 'r', encoding='utf-8')
        tivLines = f.readlines()
        f.close()

        self.TIVIsampleList = []
        index = 0 
        while index < len(tivLines) and tivLines[index] != "SameIOCar\n" :
            index += 1

        index += 1
        while index < len(tivLines) and tivLines[index] != "SameIOMotor\n" :
            self.TIVIsampleList.append(tivLines[index])
            index += 1

        index += 1
        while index < len(tivLines) and tivLines[index] != "UserOrder\n" :
            self.TIVIsampleList.append(tivLines[index])
            index += 1

        index += 1
        while index < len(tivLines) :
            self.TIVIsampleList.append(tivLines[index])
            index += 1

        fio = open(self.gateLineIO_txt, 'r')
        self.TIVioLines = fio.readlines()
        fio.close()

        fp = open(self.gate_tracking_csv, "r") 
        
        lines = fp.readlines()
        fp.close()
        self.V = []
        for j in range(0, len(lines)):
            self.V.append([])
            T = lines[j].split(",")
            for k in range(0, len(T)):
                self.V[j].append(T[k])

        self.displayInfo(4)

    @QtCore.Slot()
    def runPedestrian(self):

        print("PedestrianDataMaker")
        controller.con_DO1(self.droneFolderPath, self.resultPath, self.cutinfo_txt, self.actionName)


    def precursorCheck(self):
        step = -1
        
        if self.currentStep == 9 :
            if self.TIVPmode == 3 :
                step = 10
            else :
                step = self.currentStep
        elif self.currentStep == 3 :
            if self.show == False :
                step = 11
            else:
                step = self.currentStep
        else:
            step = self.currentStep

        paths = self.pathsExistCheck(self.RT_stepPrecursors(step))


        if len(paths) != 0 :
            msgBox = QMessageBox()
            msgBox.setWindowTitle(f"Step Presursor Warning : [Step {self.currentStep}]")
            text = f"Precursors not found : [Step {self.currentStep}][ACN:{self.actionName}]\n"
            for i in range(0, len(paths)) :
                text += f"{i+1}. <{paths[i]}> doesn't exist.\n"
            msgBox.setText(text)
            logger.warning(text)
            if self.scheduleType == 'run' :
                QTimer.singleShot(5000, msgBox.accept) 
            msgBox.exec()
            return False
        else :
            return True
        

    def RT_stepPrecursors(self, step):
        precursor = [
            self.droneFolderPath,   # 0
            self.cutinfo_txt,       # 1
            self.stab_input,        # 2
            self.stab_output,       # 3
            self.stab_video,        # 4
            self.yolo_txt,          # 5
            self.tracking_csv,      # 6
            self.background_img,    # 7
            self.gateLineIO_txt,    # 8
            self.gate_tracking_csv, # 9
            self.result_video,      # 10
            self.displayType,       # 11
            self.singelTIVpath,     # 12
            Path("./Model/YOLOv4/weights") / self.yoloModel          # 13
        ]
        stepNeeds = [
            [0, ],                  #0 Step 0
            [2, 1],                 #1 Step 1
            [4, 13],                #2 Step 2
            [4, 5],                 #3 Step 3
            [4],                    #4 Step 4
            [7],                    #5 Step 5
            [8, 6],                 #6 Step 6
            [4, 9, 8],              #7 Step 7
            [9],                    #8 Step 8
            [12, 8, 4, 9, 7],       #9 Step 9   (Video or Image mode)
            [12, 9, 8, 4, 5],          #10 Step 9  (RealTime mode)
            [5],                    #11 Step 3  (No show mode)
        ]

        ans = []
        for i in range(0, len(stepNeeds[step])):
            ans.append(precursor[stepNeeds[step][i]])
        
        return ans
    
    def pathsExistCheck(self, pathList):
        errList = []
        for i in range(0, len(pathList)):
            if os.path.exists(pathList[i]) == False:
                errList.append(pathList[i])
        
        return errList


    #### Schedule Board ################################################################

    @QtCore.Slot()
    def displayInfo(self,type):

        if type == 1 : # display Step 0 CutInfo
            out = '\tCutInfo  ( ' + str(self.currentVideoIndex + 1) + ' / ' + str(self.videoLen) + ' )\n'
            for i in range(0,self.videoLen) :
                if i == self.currentVideoIndex :
                    out = out + "=>"
                else :
                    out = out + "    "
                out = out + "[" + str(i+1) + ']'
                out = out + str(self.cutInfoLsit[i].getKey()) + '\t'
                out = out + str(self.cutInfoLsit[i].getStart()) + '\t'
                out = out + str(self.cutInfoLsit[i].getEnd())
                out = out + '\n'
            
            self._window.cutinfo.setText(out)
        elif type == 2 : # display Step 0 Video List
            out = 'Video List :\n'
            for i in range(0,self.videoLen) :
                out = out + '[' + str(i+1) +'] '+ self.videolist[i] + '\n'            
            self._window.cutinfo.setText(out)
        elif type == 3: # display Schedule Lsit

            self.page = int (self.currentScheduleIndex /self.pageLen)
            pageStart = self.page * self.pageLen

            if (self.page+1)*self.pageLen > len(self.ScheduleList) :
                pageEnd = len(self.ScheduleList) 
            else:
                pageEnd = (self.page+1)*self.pageLen

            out = '\t'+ self.scheduleName +' Schedule  (' + str(self.page+1) + '/' +  str(int((len(self.ScheduleList)-1) / self.pageLen ) +1 ) + ')\n'

            for i in range(pageStart, pageEnd) :
                if i == self.currentScheduleIndex :
                    out = out + "=>"
                else:
                    out = out + "     "
                out = out + str(i+1) + ' <' + str(self.ScheduleList[i].step) + '> '
                out = out + self.ScheduleList[i].getShortActionName() + '\n'

            self._window.cutinfo.setText(out)
        elif type == 4 : # display TIVP Issue List
            self.page = int (self.currentIssueIndex / self.pageLen)
            pageStart = self.page * self.pageLen
            if (self.page+1)*self.pageLen > len(self.TIVIsampleList) :
                pageEnd = len(self.TIVIsampleList) 
            else:
                pageEnd = (self.page+1)*self.pageLen

            out = '\t' +' TIVP Issue  (' + str(self.page+1) + '/' +  str(int((len(self.TIVIsampleList)-1) / self.pageLen ) +1 ) + ')\n'

            for i in range(pageStart, pageEnd) :
                temp = self.TIVIsampleList[i].split(',')
                if i == self.currentIssueIndex :
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, int(int(temp[1]) ))
                    out = out + "=>"
                else:
                    out = out + "    "

                out += f"{i+1} [{temp[0]}] <{temp[5]}> {temp[3]}{temp[4]} {temp[1]}-{temp[2]} \n" 
            self._window.cutinfo.setText(out)

    @QtCore.Slot()
    def back(self):
        if self.scheduleType == 'edit' : # 在Schedule 編輯模式
            if self.currentScheduleIndex > 0 :
                self.currentScheduleIndex = self.currentScheduleIndex - 1
                
                self.displayInfo(3)
        elif self.currentStep == 9 and self.TIVPmode == 3 : # 在TIVP Realtime 模式
            if self.currentIssueIndex > 0 :
                self.currentIssueIndex -= 1
                self.displayInfo(4)  
        elif self.currentVideoIndex > 0 : # 在Step 0 模式
            self.currentVideoIndex = self.currentVideoIndex - 1
            self.displayInfo(2) 
            self.load()

    @QtCore.Slot()
    def next(self):

        if self.scheduleType == 'edit' : # 在Schedule 編輯模式
            if self.currentScheduleIndex < len(self.ScheduleList) - 1 :
                self.currentScheduleIndex = self.currentScheduleIndex + 1
                
                self.displayInfo(3)
        elif self.currentStep == 9 and self.TIVPmode == 3 : # 在TIVP Realtime 模式
            if self.currentIssueIndex < len(self.TIVIsampleList) - 1:
                self.currentIssueIndex += 1
                self.displayInfo(4)
        elif self.currentVideoIndex < self.videoLen - 1 : # 在Step 0 模式
            self.currentVideoIndex = self.currentVideoIndex + 1
            self.displayInfo(2) 
            self.load()

    @QtCore.Slot()
    def forwardPage(self):
        if self.scheduleType == 'edit' : # 在Schedule 編輯模式
            if self.page > 0:
                self.page = self.page -1
                self.currentScheduleIndex = self.page * self.pageLen
            elif self.page == 0 :
                self.currentScheduleIndex = 0
            self.displayInfo(3)
        elif self.currentStep == 9 and self.TIVPmode == 3 : # 在TIVP Realtime 模式
            if self.page > 0:
                self.page = self.page -1
                self.currentIssueIndex = self.page * self.pageLen
            elif self.page == 0 :
                self.currentIssueIndex = 0
            self.displayInfo(4)
        else: # 在Step 0 模式
            if self.page > 0:
                self.page = self.page -1
                self.currentVideoIndex = self.page * self.pageLen
            elif self.page == 0 :
                self.currentVideoIndex = 0
            self.displayInfo(2)

    @QtCore.Slot()
    def nextPage(self):
        if self.scheduleType  == 'edit' :
            if self.page < int((len(self.ScheduleList)-1) / self.pageLen ):
                self.page = self.page + 1
                self.currentScheduleIndex = self.page * self.pageLen
            self.displayInfo(3)
        elif self.currentStep == 9 and self.TIVPmode == 3 : # 在TIVP Realtime 模式          

            if self.page < int((len(self.TIVIsampleList)-1) / self.pageLen ):
                self.page = self.page + 1
                self.currentIssueIndex = self.page * self.pageLen
            self.displayInfo(4)
        else: # 在Step 0 模式
            if self.page < int((self.videoLen-1) / self.pageLen ):
                self.page = self.page + 1
                self.currentVideoIndex = self.page * self.pageLen
            self.displayInfo(2)
        
    @QtCore.Slot()
    def ScheduleMode(self):
        if self.scheduleType == 'edit' :
            self.scheduleType = 'off'
            self._window.ScheduleMode_btn.setText('Schedule Mode <OFF>')
            self.set_button_text_color(self._window.ScheduleMode_btn, "block")

        else:
            self.scheduleType = 'edit'
            self._window.ScheduleMode_btn.setText('Schedule Mode <EDIT>')
            self.set_button_text_color(self._window.ScheduleMode_btn, "blue")
        self.renewScheduleBoard()

    @QtCore.Slot()
    def StartSchedule(self):

        self.scheduleType = 'run'
        self._window.ScheduleMode_btn.setText('Schedule Mode <RUN>')
        cuurentTIVT = TrackIntegrityVerificationTool.TIVT()
        ScheduTIVList = []
        ScheduTIVList.append(cuurentTIVT.retTitle())
        logger.info(f"[Start Schedule][{self.scheduleName}]")

        for i in range(self.currentScheduleIndex ,len(self.ScheduleList)):
            self.currentScheduleIndex = i
            self.displayInfo(3)
            sch = '=====================================\n[Schedule ' + str(i+1) +' / ' + str(len(self.ScheduleList))+' ]'
            self.displayType = self.ScheduleList[i].DisplayID
            self.show = self.ScheduleList[i].Show
            
            self.actionName = self.ScheduleList[i].actionName
            self.resultPath = self.ScheduleList[i].resultPath
            self.droneFolderPath = self.ScheduleList[i].droneFolderPath
            self.flashActionName()

            if self.ScheduleList[i].step == 0:
                logger.info(sch + " - [STEP 0]")
                self.step0()
                return
            elif self.ScheduleList[i].step == 1:
                logger.info(sch + " - [STEP 1]")
                self.step1()
            elif self.ScheduleList[i].step == 2:
                logger.info(sch + " - [STEP 2]")
                self.step2()
            elif self.ScheduleList[i].step == 3:
                logger.info(sch + " - [STEP 3]")
                self.step3()                
            elif self.ScheduleList[i].step == 4:
                logger.info(sch + " - [STEP 4]")
                self.step4()                
            elif self.ScheduleList[i].step == 5:
                logger.info(sch + " - [STEP 5]")
                self.step5()
            elif self.ScheduleList[i].step == 6:
                logger.info(sch + " - [STEP 6]")
                self.step6()
            elif self.ScheduleList[i].step == 7:
                logger.info(sch + " - [STEP 7]")
                self.step7()
            elif self.ScheduleList[i].step == 8:
                logger.info(sch + " - [STEP 8 - TIV]")
                self.step8_singleTIV()
            elif self.ScheduleList[i].step == 9:
                logger.info(sch + " - [STEP 9 - TIVP]")
                self.step9_TIVPrinter()
        
        if self.scheduleTIVFolderPath == "" :
            self.scheduleTIVFile = "./result/" + "/" + self.scheduleName + "_TIV.csv"
        else :
            self.scheduleTIVFile = self.scheduleTIVFolderPath + "/" + self.scheduleName + "_TIV.csv"

        base, extension = os.path.splitext(self.scheduleTIVFile)
        k = 0
        while os.path.exists(self.scheduleTIVFile):
            k += 1
            self.scheduleTIVFile = f"{base}_{k}{extension}"

        fp = open( self.scheduleTIVFile, "w")

        for i in range (0,len(ScheduTIVList)):
            fp.write(ScheduTIVList[i])
            fp.write("\n")
        fp.close()

        print ("ALL Schedule Done.")

        self.scheduleType = 'off'
        self._window.ScheduleMode_btn.setText('Schedule Mode <OFF>')

    @QtCore.Slot()
    def AddScheudle(self):
        tempItem = ScheduleItem()
        tempItem.DisplayID = self.displayType 
        tempItem.Show = self.show         
        tempItem.actionName = self.actionName
        tempItem.resultPath = self.resultPath
        tempItem.droneFolderPath = self.droneFolderPath
        tempItem.step = self.currentStep
        self.ScheduleList.insert(self.currentScheduleIndex +1, tempItem)
        if len(self.ScheduleList) == 1 :
            self.currentScheduleIndex = 0
        else :
            self.currentScheduleIndex = self.currentScheduleIndex +1

        self.displayInfo(3)
        
        
        print("AddSchedule "+ str(self.currentScheduleIndex+1) +" : [Step "+str(tempItem.step) + "] - [" + tempItem.actionName +"]")
    
    @QtCore.Slot()
    def GetSchedule(self):
        self.loadCurrentScheduleItem()

    @QtCore.Slot()
    def SetSchedule(self):
        tempItem = ScheduleItem()
        tempItem.DisplayID = self.displayType 
        tempItem.Show = self.show 
        
        tempItem.actionName = self.actionName
        tempItem.resultPath = self.resultPath
        tempItem.droneFolderPath = self.droneFolderPath
        tempItem.step = self.currentStep
        self.ScheduleList[self.currentScheduleIndex] = tempItem
        self.displayInfo(3)
        
    @QtCore.Slot()
    def DeleteSchedule(self):
        if self.scheduleType == 'off' and self.TIVPmode == 3 : # TIVP real time mode edit by user.
            if len(self.TIVIsampleList) > 0 :
                self.TIVIsampleList.pop(self.currentIssueIndex)
                if self.currentIssueIndex > 0:
                    self.currentIssueIndex = self.currentIssueIndex -1
                self.displayInfo(4)
        else :                                                 # Schedule edit mode.
            if len(self.ScheduleList) > 0 :
                self.ScheduleList.pop(self.currentScheduleIndex)
                if self.currentScheduleIndex > 0:
                    self.currentScheduleIndex = self.currentScheduleIndex -1
                self.displayInfo(3)

    @QtCore.Slot()
    def loadSchedule(self):
        if self.scheduleType == 'off' and self.TIVPmode == 3 and self.currentStep == 9:     # Load TIVP Issue
            self.loadTIVIssue()
        else:                                                                               # Normal Schedule Load
            self.scheduleLoadPath, filetype = QFileDialog.getOpenFileName(self._window,"Select Schedule File.", self.resultPath)
            
            if not self.scheduleLoadPath :
                print ("[Cancel] Schedule Load Cancel.")
            else:
                print ("Load Schedule File : " + self.scheduleLoadPath)
                self.scheduleName = self.scheduleLoadPath.split("/")[-1][:-13]
                self.scheduleTIVFolderPath = os.path.dirname(self.scheduleLoadPath)

                self.readScheduleFile()
                self.scheduleType = 'edit'
                self.set_button_text_color(self._window.ScheduleMode_btn, "blue")
                self._window.ScheduleMode_btn.setText('Schedule Mode <EDIT>')
                self.loadCurrentScheduleItem()
                self.displayInfo(3)
                self.renewScheduleBoard()

    def loadCurrentScheduleItem(self):
        self.actionName = self.ScheduleList[self.currentScheduleIndex].actionName
        self.resultPath = self.ScheduleList[self.currentScheduleIndex].resultPath
        self.droneFolderPath = self.ScheduleList[self.currentScheduleIndex].droneFolderPath
        self.show = self.ScheduleList[self.currentScheduleIndex].Show
        self.displayType = self.ScheduleList[self.currentScheduleIndex].DisplayID

        if self.show:
            self._window.show_btn.setText('Show')
        else :
            self._window.show_btn.setText('BackGround')
        if self.displayType:
            self._window.DisplayType_btn.setText('Display ID')
        else :
            self._window.DisplayType_btn.setText('Hide ID')

        self.flashActionName()

    @QtCore.Slot()
    def saveSchedule(self):
        if self.scheduleType == 'off' and self.TIVPmode == 3 and self.currentStep == 9:     # Save TIVP Issue
            self.saveTIVIssue()
        else:                                                                               # Normal Schedule Save
            filetype = ("_Schedule.txt")
            temp = QFileDialog.getSaveFileName(self._window,"Save Schedule File.", "", filetype)
            if temp[0] != "":
                self.scheduleSavePath = temp[0] + temp[1]
                self.scheduleName = temp[0].split("/")[-1]
                self.writeScheduleFile()
                print ("Save Schedule File : " + self.scheduleSavePath)
                self.scheduleTIVFolderPath = os.path.dirname(self.scheduleSavePath)
                self.displayInfo(3)
            else :
                print ("[Cancel] Schedule Save Cancel.")

    def readScheduleFile(self):
        def encodeFile():
            encodings = ['utf-8', 'cp950']
            for e in encodings:
                try:
                    with open(self.scheduleLoadPath, 'r', encoding=e) as f:
                        return f.readlines()
                except UnicodeDecodeError:
                    pass
            print(f'Could not read {self.scheduleLoadPath} with any encoding.')
            return None
        # f = open(self.scheduleLoadPath, 'r', encoding='utf-8')
        lineData = encodeFile()
        self.ScheduleList = []

        for i in range(0, len(lineData)) :
            tempSchedule = ScheduleItem()
            counter = 0
            tempIndex = ""

            for c in range(0,len(lineData[i])):
                char = lineData[i][c]
                if char == '\t' or char == '\n':
                    if counter == 0 : # Step
                        tempSchedule.step = int(tempIndex)
                    elif counter == 1 : # Display Boolen
                        if tempIndex == '1':
                            tempSchedule.DisplayID = True
                        else :
                            tempSchedule.DisplayID = False
                    elif counter == 2 : # Show Boolen
                        if tempIndex == '1':
                            tempSchedule.Show = True
                        else :
                            tempSchedule.Show = False
                    elif counter == 3 : # actionName
                        tempSchedule.actionName = tempIndex
                    elif counter == 4 : # resultPath
                        tempSchedule.resultPath = tempIndex
                    elif counter == 5 : # droneFolderPath
                        tempSchedule.droneFolderPath = tempIndex
                             
                    counter = counter + 1
                    tempIndex = ""
                else:
                    tempIndex = tempIndex + char

            self.ScheduleList.append(tempSchedule)

    def set_button_text_color(self, button, color):
        palette = button.palette()
        palette.setColor(QPalette.ButtonText, QColor(color))
        button.setPalette(palette)

        
    def writeScheduleFile(self):
        for i in range(0, len(self.ScheduleList)):
            f = open(self.scheduleSavePath, 'w', encoding='utf-8')

            for i in range(0,len(self.ScheduleList)) :
                if self.ScheduleList[i].DisplayID:
                    display = 1
                else:
                    display = 0

                if self.ScheduleList[i].Show:
                    show = 1
                else :
                    show = 0

                out = ''
                out = out + str(self.ScheduleList[i].step) + '\t'
                out = out + str(display) + '\t'
                out = out + str(show) + '\t'
                out = out + self.ScheduleList[i].actionName + '\t'
                out = out + self.ScheduleList[i].resultPath + '\t'
                out = out + self.ScheduleList[i].droneFolderPath + '\n'
                
                f.write(out)
            f.close()

    def renewScheduleBoard(self):
        if self.scheduleType == 'off' and self.TIVPmode == 3 and self.currentStep == 9 : # TIVP real time mode edit by user.
            self._window.DeleteSchedule_btn.setText('Delete TIV Issue')
            self._window.LoadScheduleFile_btn.setText('Load TIV File')
            self._window.SaveScheduleFile_btn.setText('Save TIV File')
            chColor2 = "blue"

        else :
            self._window.DeleteSchedule_btn.setText('Delete Schedule')
            self._window.LoadScheduleFile_btn.setText('Load Schedule File')
            self._window.SaveScheduleFile_btn.setText('Save Schedule File')
            chColor2 = "black"

        self.set_button_text_color(self._window.SaveScheduleFile_btn, chColor2)
        self.set_button_text_color(self._window.LoadScheduleFile_btn, chColor2)
        self.set_button_text_color(self._window.DeleteSchedule_btn, chColor2)
        self.set_button_text_color(self._window.show_btn, chColor2)
        self.set_button_text_color(self._window.DisplayType_btn, chColor2)
        self.set_button_text_color(self._window.showTracking_btn, chColor2)

        if self.scheduleType == 'edit':
            chColor = "blue"
        else:
            chColor = "black"
        self.set_button_text_color(self._window.step0_btn, chColor)
        self.set_button_text_color(self._window.step1_btn , chColor)
        self.set_button_text_color(self._window.step2_btn , chColor)
        self.set_button_text_color(self._window.step3_btn , chColor)
        self.set_button_text_color(self._window.step4_btn , chColor)
        self.set_button_text_color(self._window.step5_btn , chColor)
        self.set_button_text_color(self._window.step6_btn , chColor)
        self.set_button_text_color(self._window.step7_btn , chColor)
        self.set_button_text_color(self._window.TIV_btn , chColor)
        self.set_button_text_color(self._window.TIVPrinter_btn , chColor)

    def loadTIVIssue(self):
        self.singelTIVpath, filetype = QFileDialog.getOpenFileName(self._window,"Select TIV.csv.", self.resultPath )
        tempStr = self.singelTIVpath
        if not self.singelTIVpath :
            print ("[Cancel] TIV Load Cancel.")
        else:
            print ("Load TIV File : " + self.singelTIVpath)        
            
            self.renewScheduleBoard()
            self.resultPath = os.path.dirname(self.singelTIVpath) + '/'
            self.selectName()            # 設定AC name，抓取print資料，但會刷掉指定的TIV.csv
            self.singelTIVpath = tempStr # 因此重新設定指定的TIV.csv
            self.TIVfileLoad()           # 再Loda TIV
            self.displayInfo(4)

    def saveTIVIssue(self):
        filetype = ("_TIV.csv")
        temp = QFileDialog.getSaveFileName(self._window,"Save TIV File.", "", filetype)
        if temp[0] != "":
            outputTIV = temp[0] + temp[1]

            r = open(self.singelTIVpath, 'r')
            ORtiv = r.readlines()
            r.close()
            f = open(outputTIV, 'w')
            f.write(ORtiv[0])
            f.write(ORtiv[1])
            

            index = 0
            SameIOCarID = []
            SameIOMotorID = []
            while index < len(ORtiv) and ORtiv[index] != "SameIOCar\n" :
                index += 1

            index += 1
            while index < len(ORtiv) and ORtiv[index] != "SameIOMotor\n" :
                SameIOCarID.append(ORtiv[index].split(',')[0])
                index += 1

            index += 1
            while index < len(ORtiv) :
                SameIOMotorID.append(ORtiv[index].split(',')[0])
                index += 1


            f.write("SameIOCar\n")
            for i in range(0, len(self.TIVIsampleList)):
                if (self.TIVIsampleList[i].split(',')[0] in SameIOCarID) :
                    out = self.TIVIsampleList[i]
                    f.write(out)
            f.write("SameIOMotor\n")
            for i in range(0, len(self.TIVIsampleList)):
                if (self.TIVIsampleList[i].split(',')[0] in SameIOMotorID) :
                    out = self.TIVIsampleList[i]
                    f.write(out)
            f.write("UserOrder\n")
            for i in range(0, len(self.TIVIsampleList)):
                if (self.TIVIsampleList[i].split(',')[0] not in SameIOCarID) and (self.TIVIsampleList[i].split(',')[0] not in SameIOMotorID) :
                    out = self.TIVIsampleList[i]
                    f.write(out)
                    f.write("\n")

            f.close()
            print ("Save TIV File : " + outputTIV)
            self.displayInfo(4)
        else :
            print ("[Cancel] TIV Save Cancel.")




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

class ScheduleItem():
    def __init__(self):
        self.step = -1
        self.DisplayID = False
        self.Show = False
        
        self.actionName = ""
        self.resultPath = ""
        self.droneFolderPath = ""


    def setActionName(self, newName):
        self.actionName = newName
    
    def setResultPath(self, newPath):
        self.resultPath = newPath
    
    def setdroneFolderPath(self, newOrgin):
        self.droneFolderPath = newOrgin
    
    def getShortActionName(self):
        out = ""
        if len(self.actionName) > 12:
            out =self.actionName[0:12]+'...'+self.actionName[-4:]
        else:
            out = self.actionName
        return out


