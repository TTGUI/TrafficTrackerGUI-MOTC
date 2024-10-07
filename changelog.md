# TTGUI - Traffic Tracker GUI
## Changelog

### v3.11.1a - 2024/10/07
#### Organize
- update .gitignore

### v3.11.1 - 2024/10/07
#### Bug Fixed
- fix View\ui_Step.py : setResultBtnText failed. 

### v3.11.0 - 2024/09/27
#### Improment
- add Model\sort8.py : new tracking logic for tracking7_6.py.
- update Model\tracking7_6.py : use new tracking logic sort8. Now stab video are not necessary.
#### Organize
- update View\main_window.py : new code structure.
- add View\ui_BaseManager.py, ui_Developer.py, ui_DisplayInfo.py, ui_Player.py, ui_Schedule.py, ui_Step.py, ui_setupFont.py : new code structure.
- move Model\sort7.py to abandonedCodes.

### v3.10.9 - 2024/09/24
#### Improment
- update Model\drawIO3.py : add back drawing pedestriantion area.
- update Model\drawIO2.py, drawIO3.py : break function by both 'q' and 'Q' key.
- update logs\logger.py : fix wrong text.
#### Organize
- update cont\controller.py, logs\logger.pt, Model\YOLOv5\detect.py, View\main_window.py : update log format.
- update Model\Nbackground_median.py : update timer.

### v3.10.8 - 2024/09/23
#### Improment
- add Model\tool\temp.ipynb : a test code.
- update Model\tool\listFiles.py : a tool for visualize files tree.

### v3.10.7a - 2024/09/20
#### Organize
- add \Model\Stab_ECC_GPU_source\x64\Release\Stab_ECC_GPU_source.exe : prebuild exe file for git clone.
- update .gitgnore

### v3.10.7 - 2024/09/19
#### Bug Fixed
- fix Model\drawIO2.py, drawIO3.py : read image in BGR mode.

### v3.10.6 - 2024/09/19
#### Bug Fixed
- fix Model\tracking7_6.py : cap not define when undisplay mode.

### v3.10.5b - 2024/09/18
#### Organize
- update View\my_window.py : improve code structure.
- update Model\Kstabilization.py : display frame on GUI.
- update Model\Replay2.py : display frame on GUI.
- update Model\tracking7_6.py : display frame on GUI.
- update Model\Nbackground_median.py : display frame on GUI.
- update Cont\controller.pt : add parameter and argument for display frame call back.

### v3.10.5a - 2024/09/18
#### Organize
- update View\my_window.py : improve code structure.
- add View\ui_setup.py : improve code structure.
- add View\ui_setupButtens.py : improve code structure.
- add View\ui_setupFont.py:  improve code structure.

## Changelog
### v3.10.4a - 2024/09/18
#### Improvements
- update View\my_window.py : content fixed.

## Changelog
### v3.10.4 - 2024/09/16
#### Improvements
- update View\my_window.py : add new TIVP replay UI, add TIV dialog to change TIV setting.


### v3.10.3 - 2024/09/13
#### Improvements
- update Cont\controller.py : add argument to controll Kstabilization.py.
- update Model\Kstabilization.py : add new timer for ETA. add argument to change cpu stab video's layer.
- update Model\Replay2.py : add new timer for ETA.
- update Model\tracking7_6.py : add new timer for ETA.
- update Model\Stab_ECC_GPU_source\Stab_ECC_GPU_source\Stab_ECC_GPU_source.cpp : add new timer for ETA.
- add/update View\WH_dialog.ui, main_window.py, my_window.ui : add edit dialog to change output video's layer.

### v3.10.2a - 2024/09/12
#### Improvements
- update .gitignore: It seems the Visual Studio folder structure differs between Windows 10 and Windows 11, make sure .gitignore works properly on both.

### v3.10.2 - 2024/09/12
#### Improvements
- add start_gui_anacondaEnv.bat : add new start bat when environment build by anaconda. Need to change path for environment and ttgui codes.
- Model\Kstabilization_T0N.py : close all frame window when process end.
#### Organize
- relocate Model\Stab_ECC_GPU_source
- rebuild Model\YOLOv4\data\classes_vehicle8cls.txt : file missing some reason, recovered.
#### Document
- update README.md
- update doc\GPU_ECC_install_introduction.docx : verify the process on windows11 RTX4060 cuda11.1 .
- update doc\TrafficTrackerGUI_introduction.docx 

### v3.10.1 (2024/09/12)
#### Improvements
- add Model\tool\recursiveChangeName.py

### v3.10.0 (2024/09/11)
#### Improvements
- add Model\drawIO3.py, IOadded3.py : New traffic section process, roadsection.
- update config\conf.py, config.txt : add section mode info.
- update View\main_windwo.py, my_window.ui : add change section mode.
- update Cont\controller.py : add diffrent section activate function.

### v3.9.5 (2024/08/20)
#### Bud Fixed
- fix Model\IOadded2.py : tracking AIBO failing when only have 2 intersection line.
- fix Model\Nbackground_median.py : background image generating fail sometime.

#### Improvements
- update config\conf.py : add output video layout format.

### v3.9.4 (2024/07/31)
#### Improvements
- update Model\Nbackground_median.py : change video read frame logic from one by one to skip frame.

### v3.9.3 (2024/07/16)
#### Improvements
- update Model\Kstabilization_GPU.py, Model\Stab_ECC_GPU_source\eccgpu_sourceCode.cpp : add ECC and Output Video size optional parameter (use same parameter).
- add Model\tool\videoResize.py : resize video to 1920x1080.
- add Model\tool\div2.py : change gate.csv coordinate from 3840x2160 to 1920x1080.
- add Model\tool\reshapevideo_2rows.py : reshape video to 1920x1920.
- add Model\tool\Relocation_single_2rows.py : relocate csv coordinate from 1920x1920 to 3840x2160

### v3.9.2 (2024/06/07)
#### Document
- update about [_gate.csv format](doc\TrafficTrackerGUI_introduction.docx)
#### Improvements
- update Model/tracking7_6.py
#### Organize
- move/add tracking7_4, tracking7_5 to [abandonedcodes](abandonedcodes).

### v3.9.1b (2023/09/13)
#### Improvements
- Model/tool/scvParser.py : add more log print.

### v3.9.1a (2023/09/05)
#### Improvements
- add Model/tool/ECC_Rater.py : return two images similarity score.
- add Model/tool/ECC_RaterScript.py

### v3.9.1 (2023/08/28)
#### Improvements
- Model/Stab_ECC_GPU_source/eccgpu_sourceCode.cpp : Avoid different FPS of the input video causing the output video to be different from the real speed.
- Model/Kstabilization_GPU.py : make the GPU_ECC.exe directly link to Model\Stab_ECC_GPU_source where the exe file compiled.
#### Document
- update [GPU_ECC_install_introduction.docx](./doc/GPU_ECC_install_introduction.docx)/[Google線上文件](https://docs.google.com/document/d/1x2xtYWFi6JJ_wzsxm2_RiXn20cEqbD33gZbXYUxyU5Q/edit?usp=sharing)

### v3.9.0 (2023/08/28)
#### Improvements
- modify Kstabilization_T0N.py by `YCkao5888` : Avoid different FPS of the input video causing the output video to be different from the real speed.
- add csvParserScript.py : csvParser's batch script.
#### Bug Fixed
- Model/tool/label_it_v1.13_jpgver : fix the output coordinate typo.

### v3.8.5 (2023/08/17)
#### Improvements
- add padding program for filename bugly request(no chinese, no dot.).

### v3.8.4 (2023/08/16)
#### Organize
- add label tool `label_it_v1.13_jpgver` in Model/tool.

### v3.8.3 (2023/08/10)
#### Improvements
- main_windows.py : keep running in TIVP-R when there is no TIV issue.
- csvParser.py : more modulable for another python file calling.
#### Bug fixed
- controller.py : [issue#22] fix Step7 wrong import path.

### v3.8.2 (2023/08/01)
#### New Features
- main_window.py : add Icon.

### v3.8.1 (2023/07/28)
#### Organize
- main_window.py : fix some 'TIV' typed wrongly to 'TVI'.

### v3.8.0 (2023/07/28)
#### New Features
- main_window.py : add display yolo detect result in TVIP-RealTime mode.
- main_window.py : add butten extra status prompt.
- main_window.py : add ToolTip in some multifunctional butten.

#### Improvements
- main_window.py : add log when step start in schedule.

### v3.7.5 (2023/07/25)
#### Improvements
- update Tracking code : to tracking7_4.py
- update SORT code : update sort7.py

### v3.7.4 (2023/07/24)
#### Improvements
- main_window.py : use native dialog.
#### Bug fixed
- main_window.py : fix the bug [issue#15] Step0 reset start ignore range. 

### v3.7.3 (2023/07/24)
#### Improvements
- update Tracking code : to tracking7_3.py

### v3.7.2a (2023/07/21)
#### Temporary storage
- Temporary storage for [issue#15]

### v3.7.2b (2023/07/21)
#### Improvements
- update Tracking code : to tracking7_2.py
- update SORT code : to sort7.py
- update install requirements : to requirements_cuda10.2.txt, requirements_cuda11.1.txt

### v3.7.1 (2023/07/20)
#### Improvements
- Model\YOLOv4\utils_pkg\remove_duplicate_box.py : info output add.
- Model\YOLOv4\utils_pkg\datasets.py : info log simplified.
- Model\YOLOv4\detect.py : info log simplified.

### v3.7.0 (2023/07/18)
#### New Features
- add Model\YOLOv4\utils_pkg\remove_duplicate_box.py : remove duplicate detect 8cls.
- update Model\YOLOv4\utils_pkg\Rotated_IoU\ : new codes added, and move old codes to abandonedCodes.

### v3.6.2 (2023/07/17)
#### Improvements
- main_window.py : schedule save as UTF-8, and readable UTF-8 and Big-5.

#### Bug fixed
- main_window.py : fix the bug [issue#14] can not play in schedule run step0 second time.

### v3.6.1 (2023/07/14)
#### Improvements
- Model\GPU_Stab_source\ : add stab GPU source code.

### v3.6.0 (2023/07/14)
#### New Features
- main_window.py : Step Precursor Check.

#### Improvements
- logger.py : add PID in each log.
- logger.py : improvement log format.
- Model\YOLOv4\utils_pkg\datasets.py : make the log short.
- Model\YOLOv4\detect.py : make the log in same line.

### v3.5.4 (2023/07/12)
#### Bug fixed
- main_window.py : fix the bug that in Step9 select other TIV.csv can't read file successfully.

### v3.5.3 (2023/07/12)
#### Improvements
- main_window.py : open the result and drone folder for linux.
- README.md : update.

### v3.5.2 (2023/07/12)
#### Improvements
- main_window.py : add next 1 frame and back 1 frame button.

### v3.5.1 (2023/07/12)
#### Improvements
- main_window.py : [Issue #9] add butten to open the result and drone folder.
- main_window.py : improve the UI layout.

### v3.5.0 (2023/07/11)
#### Improvements
- main_window.py : In the paused frame playing, 'Hide ID' and 'Display ID' will take effect immediately.
- main_window.py : Reorganize the code.

#### New Features
- main_window.py : Saving the user orderd TIV issue to file.

### v3.4.1 (2023/07/06)

#### Bug fixed
- fix issue #4 #5 : In schedule run mode, Step0 can't use player function.

#### Improvements
- TIV Printer(RealTime) : Now the ID can be displayed while using the jump feature at the same time.

### v3.4.0 (2023/06/30)

#### Improvements
- requirements_cuda10.2.txt : change opencv version from 4.1.0.25 to 4.7.0.72.
- requirements_cuda10.2.txt : remove following python packages which are no more used due to tracking code change.
    --lap==0.4.0
    --scikit-image==0.17.2
    --scikit-learn==0.21.0
    --pandas==1.1.5
    --numba==0.53.1
- tracking6.py : fix math.dist() invalid on python3.6.7 .

#### organize
- organize abandoned Codes again.

### v3.3.1 (2023/06/28)

#### Improvements
- TIVPrint.py, main_window.py : add IO ID on screen.
- csvParser.py : improve console display.

### v3.3.0 (2023/06/28)

#### New Features
- new tracking method : tracking6.py
- add tracking trackers setting GUI.

#### Improvements
- more readable file : config.txt
- fix the GUI main window layout to fit the dynamic screen size.

### v3.2.5 (2023/05/22)

#### New Features
- add /Model/tools/csvParser.py : support to operate csv file.

#### Bug fixed
- main_window.py : remove a bug about Replay2.py display ID.
- main_window.py : Step0 frameplay and schedule mode frameplay bug fixed, was used to TIVissueMode.

#### Document
- /doc/簡易TrafficTrackerGUI操作說明.mp4

### v3.2.4 (2023/4/21)

#### Improvements
- main_window.py : keep playing when fpsback or fpsnext in TVI realtime display mode.

#### Bug fixed
- TIVPinter.py : There is a bug in the TIV CSV sorting function - it is not sorting based on integers but rather on strings.

### v3.2.3 - TIV2.3 (2023/4/12)

#### Improvements
- main_window.py : support real time display TIV Printer.
- main_window.py : Support viewing the specified number track.
- main_window.py : improvement video display logic.
- Replay2.py : improvement ID display style.

#### Document
- TrafficTrackerGUI_introduction.docx : update v3.2.3.

### v3.2.2 - TIV2.2 (2023/4/11)

#### Improvements
- main_window.py : add choice function to select output video or image.

#### Document
- TrafficTrackerGUI_introduction_3.2.2.docx : update.

### v3.2.1 - TIV2.1 (2023/3/28)

#### Improvements
- TIVPrinter.py : Type2, output video.

### v3.2.0 - TIV2 (2023/3/27)

#### Improvements
- Add TIVPrinter.py

### TIV1.1 (2023/3/27)

#### Improvements
- TrackIntegrityVerificationTool.py : Add add same IO car and motor data in each TIV.csv

### v3.1.0 (2023/3/23)

#### Improvements
- Add TrackIntegrityVerificationTool.py

#### Bug Fixes (2023/3/20)
- Fix main_windows.py : setResultFolder cancel inital bug.

### v3.0.5 (2023/3/20)

#### Warning ignore
- Add DeprecationWarning ignore in traffictrackergui-env\Lib\site-packages\sklearn\utils\linear_assignment_.py 

### v3.0.4 (2023/3/20)
#### Bug Fixes
- Fixed sort.py : Fixed tracking id doesn't initialized when running continuously.

### v3.0.3a (2023/3/16)

#### organize 
- remove OdrawIO.py : move to abandonedCodes.
- remove PIOadded.py : move to abandonedCodes.
- remove QReplay.py : move to abandonedCodes.

### v3.0.3 (2023/3/15)
#### Bug Fixes
- hotfix2 main_windows.py : Fixed yolomodelName change cancel bug.
- hotfix main_windows.py : Fixed a bug about yolomodelName.
- Fixed Replay2.py : Fixed a old Bug about result video IDinfo display.

### v3.0.2 (2023/3/14)
#### Improvements
- improved main_window.py : Support to select yolo model, and remeber the select next time.
- improved mainwindows.py : information display.
- improved conf.py : IO logic.

### v3.0.1 (2022/9/21)
#### Improvements
- improved main_window.py : selectName logic.

### v3.0.0 (2022/9/16)

#### New Features
- Schedule Mode Added.
- Support GPU for Stabilization.

### v2.2.0 (2022/4/25)

#### New Features
- New Function "PedestrianDataMaker" : Support to make Pedestrian Data Image for training.

### v2.1.0 (2022/1/7)

#### New Features
- Replay2/main_windows : Support to display or hide ID information in result video.

### v2.0.0 (2022/1/7)

#### New Features
- Support auto install for windows/Linux
- Support traing on windows/Linux

#### Bug Fixes
- Kstabilization : fix the zero frame bug
- main_windows : fix cv.waitKey() error on Linux (Play video problem)

### v1.10.1 (2021/11/15)

#### Improvements
- improved GUI step logic.


### v1.9.1 (2021/11/04)

#### Improvements
- Step7 : change to show the targets ID number on screen.

### v1.9.0 (2021/10/06)

#### Improvements
- Step0 : Select a directory but also be able to view the files and folders.
- Step0 : Change butten name.
- Step0 : When set the StartFrame, set the KeyFrame also, and then save cutinfo file.
- Step0 : Change butten layout.

### v1.8.2 (2021/09/16)

#### Bug Fixes
- main_windows.py : Fix the problem DrawIO.py can not read chinese path and file name.

### v1.8.1 (2021/09/09)

#### Improvements
- Step 1 : log information edit.
- Step 0 : cutting info setting : fpsback and fpsnext jump 1 frame to 100 frame.

### v1.8.0 (2021/09/06)

#### New Features
- Add "Set Drone Folder" for start in Step1.

### v1.7.0 (2021/09/02)

#### New Features
- Add fps_Back, fps_next, fps_jump to setting video player statu.

### v1.6.7 (2021/09/01)

#### Improvements
- main_window.py : video player FPS autoset

### v1.6.6 (2021/08/31)

#### Improvements
- UI Layout change

### v1.6.5 (2021/08/27)

#### Bug Fixes
- Fix main_window.py bool video_init Logic

### v1.6.4 (2021/08/27)

#### Bug Fixes
- Fix Replay2.py Warning 

#### Improvements
- Improve Replay2.py information display type
- Mtracking_all.py trackNumber set

### v1.6.3 (2021/08/26)

#### Bug Fixes
- Fix Bug of main_window.py : STEP0 and STEP1 path setting problem.

### v1.6.2 (2021/08/26)

#### Bug Fixes
- Fix Bug of model_1.py : if folder ./data/ not exist, make folder.
- Fix Bug of model_1.py : if folder ./result/ not exist, make folder.

### v1.6.1 (2021/08/26)

#### Bug Fixes
- Fix Bug of logger.py : if folder ./logs/logs_tutorial/ not exist, make folder.

### v1.6.0 (2021/08/26)

#### New Features
- Add Result Folder Setting
- Add Action Name select from file

#### Bug Fixes
- Fix Bug of Nbackground_median.py : file name only can use English problem.

### v1.5.0 (2021/08/26)

#### New Features
- New version of drawIO.py

#### Improvements
- Remove old data and code files

### v1.4.0 (2021/08/25)

#### New Features
- Add File Path Setting GUI
- Add Action Naem Edit

#### Improvements
- Models : change the path setting logic (from config to main_windows)

### v1.3.1 (2021/08/24)

#### Bug Fixes
- KeyFream and CuttingFream Setting Warning Logic

### v1.3.0 (2021/08/24)

#### New Features
- Add VideoPlayer based on CV2
- Add VideoPlayer Function : Load, Play, Pause, Stop, Slider, Show
- Add KeyFream and CuttingFream Setting based on VideoPlayer 

#### Improvements
- stabilization : Automatic Cutting Set Loading.  

### v1.2.0 (2021/08/20)

#### Improvements
- New Version of IOadded.py and Replay.py

### v1.1.0 (2021/08/17)

#### New Features
- Stabilization Cutting Function
- Stabilization Key Fream Setting Function

#### Improvements
- Stabilization Resize Logic
- Stabilization Running Precess Display

### v1.0.0 (2021/08/11)

#### New Features
- Support GUI