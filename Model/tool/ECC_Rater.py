
import os
from pathlib import Path
import cv2
import numpy as np
import argparse
import time
import re



class ECC_Rater():
    """
    提供基於 cv2.findTransformECC 給出兩圖之間相異程度之分數
    """
    def __init__(self) -> None:

        self.warp_mode = cv2.MOTION_HOMOGRAPHY
        self.number_of_iterations = 300
        self.termination_eps = 5*1e-4
        self.criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, self.number_of_iterations,  self.termination_eps)

        self.parser = argparse.ArgumentParser(description="提供圖像相似度分數，運作模式包含一對一、一對多、list多對多。",
                                              epilog="example:\n[One to One] : ECC_Rater.py -t file.jpg -b file.jpg"
                                              +"\n[One to Many] : ECC_Rater.py -t file.jpg -b FOLDER_PATH"
                                              +"\n[List Many to Many] : ECC_Rater.py -l list.txt -t FOLDER_PATH -b FOLDER_PATH",
                                              formatter_class=argparse.RawTextHelpFormatter)
        self.parser.add_argument("-l", "--list",
                            help="[list file path] activation multi mission, request list file. 啟動多項目任務，檢查清單檔案路徑，檔案每行一組，目標圖名稱與搜尋路口，該list.txt需事先自製。"
                            +"\n內容例如 : 'target.png,background.jpg'",
                            type=str)
        self.parser.add_argument("-t", "--target", required=True,
                                 help="[target images folder path or file path] 欲檢查目標之檔案路徑，list模式下為資料夾路徑",
                                 type=str)
        self.parser.add_argument("-b", "--background", required=True,
                                 help="[background folder path or file path] 比對圖像之檔案路徑，一對多與list多對多模式下為資料夾路徑",
                                 type=str)
        self.parser.add_argument("-s", "--save",
                            help="[result file name] save finding result file, only name ,needn't File extension, the path will same as list file. 另存搜尋結果為檔案，同於list file位置",
                            type=str)
        
    def listLoader(self):
        """ Load list info from file. """
        self.mission = []
        f = open(self.args.list, 'r')
        inputline = f.readlines()
        f.close()        
        
        for i in range(0, len(inputline)) :
            temp = []
            temp.append(inputline[i].split(",")[0])
            temp.append(inputline[i].split(",")[1])
            self.mission.append(temp)
        print(f"[List File : {self.args.list}]")

    def ECC_Rater(self, imgPath1, imgPath2):
        """ return two images similarity score, the closer the score is to 1; otherwise, it approaches -1. """
        print("ECC Start." , end="\r")
        ECC_S = time.time()
        frame1 = cv2.imdecode(np.fromfile(imgPath1,dtype=np.uint8), -1)
        frame2 = cv2.imdecode(np.fromfile(imgPath2,dtype=np.uint8), -1)
        frame1 = cv2.resize(frame1, (1920, 1080), interpolation=cv2.INTER_CUBIC)
        frame2 = cv2.resize(frame2, (1920, 1080), interpolation=cv2.INTER_CUBIC)
        frame1_gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        frame2_gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        warp_matrix = np.eye(3, 3, dtype=np.float32)

        try:
            (cc, warp_matrix) = cv2.findTransformECC(frame1_gray, frame2_gray, warp_matrix, self.warp_mode, self.criteria)
        except Exception as e:
            print(f"Error in ECC : {e}.\nimgPath1 : {imgPath1}\n imgPath2 : {imgPath2}")
        
        ECC_E = time.time()
        ECC_costTime = ( ECC_E - ECC_S)
        print(f"ECC End.{imgPath2} cc: {cc} ({ECC_costTime}s)")
        return cc

    def backgroundNameFinder(self, title, folder):
        """ 從輸入的文件名中提取主要的中文名稱，並回傳指定資料夾中符合該主要名稱之所有項目名稱 """
        
        # 使用正則表達式從輸入的文件名中提取主要的中文名稱
        # 這裡我們假設 "background.jpg" 是固定的結尾，如果有其他結尾也可以再調整
        match = re.match(r'(.+?)(_[A-Za-z0-9]+)?_background\.jpg$', title)
        
        if not match:
            print("檔名格式不符合預期！")
            return []
        
        main_name = match.group(1)
        
        similar_files = []

        for filename in os.listdir(folder):
            if main_name in filename and filename.endswith("_background.jpg"):
                similar_files.append(filename)
        print(similar_files)
        return similar_files

    def multiMission(self):
        """ multi mission caller. """

        self.listLoader()
        resultList = []
        for i in range(0, len(self.mission)):
            print(f"========== {i+1} / {len(self.mission)} ==========")
            similarList = self.backgroundNameFinder(self.mission[i][1], self.args.background)
            
            
            image1Path = Path(self.args.target) / Path(self.mission[i][0])
            solution = []
            solution.append(image1Path)
            for j in range(0, len(similarList)):
                
                solution.append(similarList[j])
                image2Path = Path(self.args.background) / Path(similarList[j])
                cc = 0
                try :
                    cc = self.ECC_Rater(image1Path, image2Path)
                except :
                    print(f"[ERROR] Target File Not Found : {image1Path}")
                    cc = -1
                solution.append(cc)

            resultList.append(solution)

        print ("================================")

        self.resultPrinter(resultList)
        if self.args.save:
            self.resultSaver(resultList)
        
    def find_highest_score_subject(self, data_list):
        """
        專門為list資料設計的針對性任務
        """
        # 從第二項開始，每隔2項取一次，這樣可以取得所有的科目
        subjects = data_list[1::2]
        
        # 從第三項開始，每隔2項取一次，這樣可以取得所有的分數
        scores = data_list[2::2]
        
        # 使用`max`找出最高分數，然後使用`index`找到該分數在scores列表中的位置
        max_score = max(scores)
        max_score_index = scores.index(max_score)
        
        # 使用上述的索引找到相應的科目
        max_score_subject = subjects[max_score_index]            
        return max_score_subject, max_score
        
    def resultPrinter(self, resultList):
        """ Print result. """
        for i in range(0, len(resultList)):
            print(f"========== {i+1} / {len(resultList)} ==========")
            print (resultList[i][0])

            for j in range(1, len(resultList[i]), 2):
                bkg = Path(self.args.background) / Path(resultList[i][j])
                print(f"\t>> {bkg}\t{resultList[i][j+1]}")
            subject, score = self.find_highest_score_subject(resultList[i])
            bkg = Path(self.args.background) / Path(subject)
            print(f">>> Best : {bkg} ({score})")

        print ("================================")

    def resultSaver(self, resultList):
        """ Save result as txt file in folder which list file exist. """

        resultPath, nouse = os.path.split(self.args.list)
        simpleResult = Path(resultPath) / Path(self.args.save + "_Rate.csv")
        fullResult = Path(resultPath) / Path(self.args.save + "_RateFull.csv")
        
        simple = open(simpleResult, 'w',encoding='utf-8')
        full = open(fullResult, 'w', encoding='utf-8')

        for i in range(0, len(resultList)):
            simpleLine = ""
            fullLine = ""
            fullLine += str(resultList[i][0])
            simpleLine += os.path.split(resultList[i][0])[1]
            simpleLine += ","
            
            subject, score = self.find_highest_score_subject(resultList[i])
            simpleLine += subject
            for j in range(1, len(resultList[i]), 2):
                bkg = Path(self.args.background) / Path(resultList[i][j])
                fullLine += ","
                fullLine += str(bkg)
                fullLine += ",("
                fullLine += str(resultList[i][j+1])
                fullLine += ")"


            simpleLine += "\n"
            fullLine += "\n"
            simple.write(simpleLine)
            full.write(fullLine)
        simple.close()
        full.close()

        print(f"Output : {simpleResult} / {fullResult}")

    def main(self, args):
        self.args = args

        if not args.list:

            cc = self.ECC_Rater(args.target, args.background)
        else :
            self.multiMission()



        
if __name__ == '__main__':
    currentClass = ECC_Rater()
    args = currentClass.parser.parse_args()
    currentClass.main(args)        
    