from logs import logger
from View import viewer
import time
from config import conf

class Controller() :

    def __init__(self):
        self.currentViewer = viewer.mainWindowStart()

def con_step1(stab_input, stab_output, show, cut_txt, StabMode, display_callBack) :
    output_height = conf.getOutput_height()
    output_width = conf.getOutput_width()
    start = time.time()
    logger.info(f"==================[Step 1] ({StabMode}) Start.==================")
    if StabMode == 'GPU':
        from Model import Kstabilization_GPU        
        Kstabilization_GPU.stab_main(stab_input,stab_output,show,cut_txt, output_height, output_width)
    elif StabMode == 'CPU':
        from Model import Kstabilization_T0N
        Kstabilization_T0N.stab_main(stab_input,stab_output,show,cut_txt, output_height, output_width, display_callBack)

    end = time.time()
    logger.info(f"[Step 1] ({StabMode}) Done.->> ALL step1 Cost time : " + str(round(end-start, 3)) + " s"  )
    logger.info(f"[Step 1] ({StabMode}) ->> Output : {stab_output}")
  
def con_step2(stab_video, yolo_txt, yolo_model) :
    from Model.YOLOv4 import detect
    start = time.time()
    logger.info(f"==================[Step 2] Start. [yolo_model <{yolo_model}>]==================")
    detect.obb_object_detect(stab_video,yolo_txt, yolo_model)

    end = time.time()
    logger.info( "[Step 2] Done.->> Cost time : " + str(round(end-start, 3)) + " s"  )
    logger.info( f"[Step 2] ->> Output : {yolo_txt}" )

def con_step3(yolo_txt, tracking_csv, show, display_callback, trk1_set, trk2_set, stab_video=None) :
    from Model import tracking7_6      # New version
    start = time.time()
    logger.info( "==================[Step 3] Start.==================")
    tracking7_6.main( yolo_txt, tracking_csv, show, display_callback, trk1_set, trk2_set, stab_video=stab_video)     # New version
    end = time.time()
    logger.info( "[Step 3] Done.->> Cost time : " + str(round(end-start, 3)) + " s"  )
    logger.info( f"[Step 3] ->> Output : {tracking_csv}" )

def con_step4(stab_video, background_img, display_callBack) :
    from Model import Nbackground_median
    start = time.time()
    logger.info( "==================[Step 4] Start.==================")
    Nbackground_median.Backgroung_main(stab_video, background_img, display_callBack)
    end = time.time()
    logger.info( "[Step 4] Done. ->> Cost time : " + str(round(end-start, 3)) + " s"  )
    logger.info(f"[Step 4] -> Output : {background_img}")

def con_step5(IOtxt,background) :
    logger.info("==================[Step 5] Start.==================")
    if conf.getSection_mode() == "intersection":
        from Model import drawIO2
        current = drawIO2.Draw(IOtxt,background)
    elif conf.getSection_mode() == "roadsection":
        from Model import drawIO3
        current = drawIO3.Draw(IOtxt,background)

    start = time.time()
    current.main()
    end = time.time()
    logger.info( "[Step 5] Done. ->> Cost time : " + str(round(end-start, 3)) + " s"  )
    logger.info(f"[Step 5] ->> Output : {IOtxt} Type : {conf.getSection_mode()}")

    del current

def con_step6(gateLineIO_txt, tracking_csv, gate_tracking_csv) :
    start = time.time()
    logger.info("==================[Step 6] Start.==================")
    if conf.getSection_mode() == "intersection":
        from Model import IOadded2    
        IOadded2.IOadded_main(gateLineIO_txt, tracking_csv, gate_tracking_csv)
    elif conf.getSection_mode() == "roadsection":
        from Model import IOadded3 
        IOadded3.IOadded_main(gateLineIO_txt, tracking_csv, gate_tracking_csv)
    end = time.time()
        
    logger.info( "[Step 6] Done. ->> Cost time : " + str(round(end-start, 3)) + " s"  )
    logger.info(f"[Step 6] ->> Output : {tracking_csv} Type : {conf.getSection_mode()}")

def con_step7(stab_video, result_video, gate_tracking_csv, gateLineIO_txt, displayType, show, display_callback) :
    # from Model import QReplay
    from Model import Replay2
    start = time.time()
    logger.info("==================[Step 7] Start.==================")
    Replay2.Replay_main(stab_video, result_video, gate_tracking_csv, gateLineIO_txt, displayType, show, display_callback)

    end = time.time()
    logger.info( "[Step 7] Done.->> Cost time : " + str(round(end-start, 3)) + " s"  )
    logger.info(f"[Step 7] -> Output : {result_video}")

def con_DO1(originDataList, resultPath, cutinfo_txt, actionName) :
    # PedestrianDataMaker
    from Model import PedestrianDataMaker
    PedestrianDataMaker.pedestrian_main(originDataList, resultPath, cutinfo_txt, actionName)
    print("[PedestrianDataMaker Done.]")

def con_TIVT(gateCsvPath, singelTIVpath):
    from Model.tool import TrackIntegrityVerificationTool
    logger.info("==================[TIVT] Start.==================")    
    cuurentTIVT = TrackIntegrityVerificationTool.TIVT()
    ans =  cuurentTIVT.trackIntegrity(gateCsvPath, singelTIVpath)
    logger.info( "[TIVT] Done." )

    return ans

def con_TIVP(TIV_path, IO_path, stab_video, result_path, actionName, gate_csv, bkg):
    from Model.tool import TIVPrinter
    logger.info("==================[TIVP] Start.==================")   
    start = time.time()
    currentTIVP = TIVPrinter.TIVP()
    currentTIVP.printer(TIV_path, IO_path, stab_video, result_path, actionName, gate_csv, bkg)
    end = time.time()
    logger.info( "[TIVP] Done. ->> Cost time : " + str(round(end-start, 3)) + " s"  )




