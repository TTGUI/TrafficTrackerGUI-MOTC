def set_Developer(window, main_window):
    """Bind developer option buttons"""
    window.bar_1.triggered.connect(main_window.runPedestrian)
    window.bar_2.triggered.connect(main_window.changeStabMode)
    window.bar_3.triggered.connect(main_window.changeYoloModel)
    window.bar_4.triggered.connect(main_window.changeTIVPbMode)
    window.Change_Tracking_Setting.triggered.connect(main_window.changeTrackingSet)
    window.Change_Section_Mode.triggered.connect(main_window.changeSectionMode)
    window.Change_Output_WxH.triggered.connect(main_window.changeOutputWH)
    window.TIV_Setting.triggered.connect(main_window.changeTIVsetting)

    """Set text for developer option buttons"""
    window.bar_1.setText('Run Pedestrian Detection')
    window.bar_2.setText('Change Stabilization Mode')
    window.bar_3.setText('Change YOLO Model')
    window.bar_4.setText('Change TIVP Mode')
    window.Change_Tracking_Setting.setText('Change Tracking Settings')
    window.Change_Section_Mode.setText('Change Section Mode')
    if main_window.stabMode == 'CPU':
        window.bar_2.setText("Change Stabilazation Mode | [ CPU ]")
    elif main_window.stabMode == 'GPU':
        window.bar_2.setText("Change Stabilazation Mode | [ GPU ]")

    if main_window.TIVPmode == 1:
        window.bar_4.setText("Change TIVP Mode | [ Video ]")
    elif main_window.TIVPmode == 2:
        window.bar_4.setText("Change TIVP Mode | [ Image ]")
    elif main_window.TIVPmode == 3:
        window.bar_4.setText("Change TIVP Mode | [ Real Time Display ]")

  
def set_Step_Board(window, main_window):
    """Set text for step buttons"""
    # Set drone folder button
    window.DroneFolder_btn.setText('Set Drone Folder')
    window.DroneFolder_btn.clicked.connect(main_window.droneFolder)

    # Open drone folder button
    window.openFolder_btn_2.setText('O\np\ne\nn')
    window.openFolder_btn_2.clicked.connect(main_window.openDroneFolder)

    # Set result folder button
    window.setResultFolder_btn.setText('Set Result Folder\n[./result/]')
    window.setResultFolder_btn.clicked.connect(main_window.setResultFolder)

    # Open result folder button
    window.openFolder_btn.setText('O\np\ne\nn')
    window.openFolder_btn.clicked.connect(main_window.openResultFolder)

    # Step buttons
    window.step0_btn.setText('[STEP 0]\nVideo Cut Set')
    window.step0_btn.clicked.connect(main_window.step0)

    if main_window.stabMode == 'CPU':
        window.step1_btn.setText('[STEP 1] (C)\nStable')
    elif main_window.stabMode == 'GPU':
        window.step1_btn.setText('[STEP 1] (G)\nStable')
    window.step1_btn.clicked.connect(main_window.step1)

    window.step2_btn.setText('[STEP 2]\nYolo')
    window.step2_btn.clicked.connect(main_window.step2)

    window.step3_btn.setText('[STEP 3]\nTracking')
    window.step3_btn.clicked.connect(main_window.step3)

    window.step4_btn.setText('[STEP 4]\nBackground')
    window.step4_btn.clicked.connect(main_window.step4)

    if main_window.section == 'intersection':
        window.step5_btn.setText('[STEP 5] (I)\nDrawIO')
    elif main_window.section == 'roadsection':
        window.step5_btn.setText('[STEP 5] (R)\nDrawIO')
    window.step5_btn.clicked.connect(main_window.step5)

    window.step6_btn.setText('[STEP 6]\nIO Added')
    window.step6_btn.clicked.connect(main_window.step6)

    window.step7_btn.setText('[STEP 7]\nReplay')
    window.step7_btn.clicked.connect(main_window.step7)

    window.TIV_btn.setText("[STEP 8]\nTrackIntegrityVerification")
    window.TIV_btn.clicked.connect(main_window.step8_singleTIV)

    if main_window.TIVPmode == 1:
        window.TIVPrinter_btn.setText('[STEP 9]\nTIV Printer (V)')
    elif main_window.TIVPmode == 2:
        window.TIVPrinter_btn.setText('[STEP 9]\nTIV Printer (I)')
    elif main_window.TIVPmode == 3:
        window.TIVPrinter_btn.setText('[STEP 9]\nTIV Printer (R)')
    window.TIVPrinter_btn.clicked.connect(main_window.step9_TIVPrinter)

    # Show button
    window.show_btn.setText('Show')
    window.show_btn.clicked.connect(main_window.show_btn_act)
    window.show_btn.setToolTip('[S1,3,7] Show process frame or background.')

    # Display ID button
    window.DisplayType_btn.setText('Display ID')
    window.DisplayType_btn.clicked.connect(main_window.DisplayType)
    window.DisplayType_btn.setToolTip('[S7,9] Show tracking ID or not.')

    # Show tracking button
    window.showTracking_btn.setText('Show Tracking')
    window.showTracking_btn.clicked.connect(main_window.showTracking)
    window.showTracking_btn.setToolTip('[S9] Show tracking info or not.')

    # Action name buttons
    window.ActionName_btn.setText('Edit Action Name\n[]')
    window.ActionName_btn.clicked.connect(main_window.changeActionName)

    window.selectName_btn.setText('Select Action Name from File')
    window.selectName_btn.clicked.connect(main_window.selectName)

def set_Schedule(window, main_window):
    """Set text and connect signals for schedule buttons"""
    window.ScheduleMode_btn.setText('Schedule Mode <OFF>')
    window.ScheduleMode_btn.clicked.connect(main_window.ScheduleMode)

    window.StartSchedule_btn.setText('Start Schedule')
    window.StartSchedule_btn.clicked.connect(main_window.StartSchedule)

    window.GetSchedule_btn.setText('Get Schedule')
    window.GetSchedule_btn.clicked.connect(main_window.GetSchedule)
    window.GetSchedule_btn.setToolTip('Load current schedule item\nto workspace setting.')

    window.SetSchedule_btn.setText('Set Schedule')
    window.SetSchedule_btn.clicked.connect(main_window.SetSchedule)
    window.SetSchedule_btn.setToolTip('Replace current schedule item\nwith workspace setting.')

    window.DeleteSchedule_btn.setText('Delete Schedule')
    window.DeleteSchedule_btn.clicked.connect(main_window.DeleteSchedule)
    window.DeleteSchedule_btn.setToolTip('Delete current schedule item.')

    window.LoadScheduleFile_btn.setText('Load Schedule File')
    window.LoadScheduleFile_btn.clicked.connect(main_window.loadSchedule)

    window.SaveScheduleFile_btn.setText('Save Schedule File')
    window.SaveScheduleFile_btn.clicked.connect(main_window.saveSchedule)

    window.ForwardPage_btn.setText('<<== Page')
    window.ForwardPage_btn.clicked.connect(main_window.forwardPage)

    window.NextPage_btn.setText('Page ==>>')
    window.NextPage_btn.clicked.connect(main_window.nextPage)

def set_Player(window, main_window):
    """Set text and connect signals for player buttons"""
    window.pause_btn.setText('Pause')
    window.pause_btn.clicked.connect(main_window.pause)

    window.play_btn.setText('Play')
    window.play_btn.clicked.connect(main_window.play)

    window.stop_btn.setText('Stop')
    window.stop_btn.clicked.connect(main_window.stop)

    window.fpsback100_btn.setText('<<<')
    window.fpsback100_btn.clicked.connect(main_window.fpsback100)

    window.fpsnext100_btn.setText('>>>')
    window.fpsnext100_btn.clicked.connect(main_window.fpsnext100)

    window.fpsback1_btn.setText('<')
    window.fpsback1_btn.clicked.connect(main_window.fpsback1)

    window.fpsnext1_btn.setText('>')
    window.fpsnext1_btn.clicked.connect(main_window.fpsnext1)

    window.jump_btn.setText('Jump')
    window.jump_btn.clicked.connect(main_window.jump)
    window.jump_btn.setToolTip('In TIVP-R: add `i` before issue ID\nwhich you want to add.\nex: `i999`')

    window.timingSlider.sliderMoved.connect(main_window.video_position)

    window.Back_btn.setText('▲ Back')
    window.Back_btn.clicked.connect(main_window.back)

    window.Next_btn.setText('▼ Next')
    window.Next_btn.clicked.connect(main_window.next)

    window.SetStartFrame_btn.setText('Set Start Frame')
    window.SetStartFrame_btn.clicked.connect(main_window.setStartFrame)

    window.SetEndFrame_btn.setText('Set End Frame')
    window.SetEndFrame_btn.clicked.connect(main_window.setEndFrame)

def setup_all_buttons(window, main_window):
    """Call all text and binding functions"""
    set_Developer(window, main_window)
    set_Step_Board(window, main_window)
    set_Schedule(window, main_window)
    set_Player(window, main_window)


