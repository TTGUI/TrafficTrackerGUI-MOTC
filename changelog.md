## Changelog

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

#### Bug Fixes

- None

#### Improvements

- stabilization : Automatic Cutting Set Loading.  


### v1.2.0 (2021/08/20)

#### New Features

- None

#### Bug Fixes

- None

#### Improvements

- New Version of IOadded.py and Replay.py

### v1.1.0 (2021/08/17)

#### New Features

- Stabilization Cutting Function
- Stabilization Key Fream Setting Function

#### Bug Fixes

- None

#### Improvements

- Stabilization Resize Logic
- Stabilization Running Precess Display

### v1.0.0 (2021/08/11)

#### New Features

- Support GUI

#### Bug Fixes

- None

#### Improvements

- None
