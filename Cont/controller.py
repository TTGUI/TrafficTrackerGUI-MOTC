from logs import logger
from View import viewer
import time
from config import conf

class Controller() :

    def __init__(self):
        self.currentViewer = viewer.mainWindowStart()



def con_step1(stab_input,stab_output,show,cut_txt,StabMode) :
    output_height = conf.getOutput_height()
    output_width = conf.getOutput_width()
    start = time.time()
    if StabMode == 'GPU':
        from Model import Kstabilization_GPU
        Kstabilization_GPU.stab_main(stab_input,stab_output,show,cut_txt, output_height, output_width)
    elif StabMode == 'CPU':
        from Model import Kstabilization_T0N
        Kstabilization_T0N.stab_main(stab_input,stab_output,show,cut_txt)

    end = time.time()

    if StabMode == 'GPU':
        logger.info( "[Step 1] (G) ->> ALL step1 Cost time : " + str(end-start)  )
        print("[SEPT1 (G) Done.]")
    elif StabMode == 'CPU':
        logger.info( "[Step 1] (C) ->> ALL step1 Cost time : " + str(end-start)  )
        print("[SEPT1 (C) Done.]")
  
def con_step2(stab_video, yolo_txt, yolo_model) :
    from Model.YOLOv4 import detect
    start = time.time()
    logger.info( f"[yolo_model <{yolo_model}>]" )
    detect.obb_object_detect(stab_video,yolo_txt, yolo_model)

    end = time.time()
    logger.info( "[Step 2] ->> Cost time : " + str(end-start)  )
    print("[SEPT2 Done.]")

def con_step3(stab_video,yolo_txt,tracking_csv,show, trk1_set, trk2_set) :
    from Model import tracking7_6      # New version
    start = time.time()

    tracking7_6.main(stab_video,yolo_txt,tracking_csv,show, trk1_set, trk2_set)     # New version
    end = time.time()
    logger.info( "[Step 3] ->> Cost time : " + str(end-start)  )
    print("[SEPT3 Done.]")

def con_step4(stab_video,background_img) :
    from Model import Nbackground_median
    start = time.time()

    Nbackground_median.Backgroung_main(stab_video,background_img)

    end = time.time()
    logger.info( "[Step 4] ->> Cost time : " + str(end-start)  )
    print("[SEPT4 Done.]")

def con_step5(IOtxt,background) :
    if conf.getSection_mode() == "intersection":
        from Model import drawIO2
        current = drawIO2.Draw(IOtxt,background)
    elif conf.getSection_mode() == "roadsection":
        from Model import drawIO3
        current = drawIO3.Draw(IOtxt,background)

    start = time.time()
    current.main()
    end = time.time()
    logger.info( "[Step 5] ->> Cost time : " + str(end-start)  )
    print("[SEPT5 Done.]")

    del current

def con_step6(gateLineIO_txt, tracking_csv, gate_tracking_csv) :
    start = time.time()
    if conf.getSection_mode() == "intersection":
        from Model import IOadded2    
        IOadded2.IOadded_main(gateLineIO_txt, tracking_csv, gate_tracking_csv)
    elif conf.getSection_mode() == "roadsection":
        from Model import IOadded3 
        IOadded3.IOadded_main(gateLineIO_txt, tracking_csv, gate_tracking_csv)
    end = time.time()
        
    logger.info( "[Step 6] ->> Cost time : " + str(end-start)  )
    print("[SEPT6 Done.]")

def con_step7(stab_video, result_video, gate_tracking_csv, gateLineIO_txt, displayType, show) :
    # from Model import QReplay
    from Model import Replay2
    start = time.time()

    Replay2.Replay_main(stab_video, result_video, gate_tracking_csv, gateLineIO_txt, displayType, show)

    end = time.time()
    logger.info( "[Step 7] ->> Cost time : " + str(end-start)  )
    print("[SEPT7 Done.]")

def con_DO1(originDataList, resultPath, cutinfo_txt, actionName) :
    # PedestrianDataMaker
    from Model import PedestrianDataMaker
    PedestrianDataMaker.pedestrian_main(originDataList, resultPath, cutinfo_txt, actionName)
    print("[PedestrianDataMaker Done.]")

def con_TIVT(gateCsvPath, singelTIVpath):
    from Model.tool import TrackIntegrityVerificationTool
    
    cuurentTIVT = TrackIntegrityVerificationTool.TIVT()
    ans =  cuurentTIVT.trackIntegrity(gateCsvPath, singelTIVpath)
    print("[TIVT Done.]")
    return ans

def con_TIVP(TIV_path, IO_path, stab_video, result_path, actionName, gate_csv, bkg):
    from Model.tool import TIVPrinter

    currentTIVP = TIVPrinter.TIVP()
    currentTIVP.printer(TIV_path, IO_path, stab_video, result_path, actionName, gate_csv, bkg)





