import os
import pathlib


# 讀取CSV軌跡並輸出完整度
# 略過首尾設定長度(預設900 frames)不處理


class TIVT:
    def __init__(self):
        if __name__ == '__main__':
            self.ignoreFrame = 900
        else:
            from config import conf
            self.ignoreFrame = conf.getTIV_ignoreFrame()
        self.ignoreFinalFrame = 0
        self.lineTitle = "gate.csv,Ignore Frame / Ignore Final Frame,汽機車完整度比例,汽車完整度比例,機車完整度比例,汽車同方向進出佔完整軌跡比例,機車同方向進出佔完整軌跡比例"
        self.lineTitle = self.lineTitle + ",汽車同方向進出數量,汽車完整軌跡數量,汽車總軌跡數量(濾除全X),機車同方向進出數量,機車完整軌跡數量,機車總軌跡數量(濾除全X)"

        print("[TIVT Start.]")

    def needIgnore(self, lineSp):
        
        if int(lineSp[1]) < self.ignoreFrame :
            return True
        elif int(lineSp[2]) > self.ignoreFinalFrame :
            return True
        else:
            return False

    def setFinalFrame(self, lineSpLast20):
        theMax = 0
        for i in range(0, len(lineSpLast20)):
            fn = lineSpLast20[i].split(",")[2]
            if int(fn) > theMax:
                theMax = int(fn)

        self.ignoreFinalFrame = theMax - self.ignoreFrame

    def vehicleTypeBool(self, type, lineSp):
        if type == lineSp[5]:
            return True
        else:
            return False
        
    def goodData(self, lineSp):
        if lineSp[3] != 'X' and lineSp[4] != 'X' :
            # print("good " + lineSp[3] + " " + lineSp[4])
            return True
        else :
            return False
        
    def badData(self, lineSp):
        if lineSp[3] == 'X' and lineSp[4] != 'X' :
            # print("bad " + lineSp[3] + " " + lineSp[4])   
            return True
        if lineSp[3] != 'X' and lineSp[4] == 'X' :
            # print("bad " + lineSp[3] + " " + lineSp[4])   
            return True
        else :
            return False

    def failData(self, lineSp):
        if lineSp[3] == 'X' and lineSp[4] == 'X' :
            # print("fail " + lineSp[3] + " " + lineSp[4])
            return True
        else :
            return False        

    def sameIO(self, lineSp):
        if lineSp[3][0] != 'X' and lineSp[4][0] != 'X' and lineSp[3][0] == lineSp[4][0] :
            # print("same " + lineSp[3] + " " + lineSp[4])
            return True
        else :
            return False

    def div(self, A, B) :
        if B == 0 :
            return "DIV ZERO"
        else :
            return str(A/B)

    def retTitle(self):
        return self.lineTitle

    def trackIntegrity(self, gateCsvPath, singelTIVpath) :
        resultPath = singelTIVpath
        f = open(gateCsvPath, 'r')
        lines = f.readlines()
        f.close()

        final20 = lines[-20:]
        self.setFinalFrame(final20)

        goodcar = 0
        badcar = 0
        sameIOcar = 0
        sameIOcarList = []
        allCar = 0
        
        goodmotor = 0
        badmotor = 0
        sameIOmotor = 0
        sameIOmotorList = []
        allmotor = 0

        for i in range ( 0 , len(lines)):
            
            eachLineSplit = lines[i].split(",")
            if not self.needIgnore(eachLineSplit):
                if self.vehicleTypeBool('c', eachLineSplit):
                    if self.goodData(eachLineSplit):
                        goodcar += 1
                    if self.badData(eachLineSplit):
                        badcar += 1
                    if self.sameIO(eachLineSplit):
                        sameIOcar += 1
                        temp = ""
                        for p in (range(0,6)):
                            temp += (eachLineSplit[p])
                            temp += ","
                        sameIOcarList.append(temp)

                if self.vehicleTypeBool('m', eachLineSplit):
                    if self.goodData(eachLineSplit):
                        goodmotor += 1
                    if self.badData(eachLineSplit):
                        badmotor += 1
                    if self.sameIO(eachLineSplit):
                        sameIOmotor += 1
                        temp = ""
                        for p in (range(0,6)):
                            temp += (eachLineSplit[p])
                            temp += ","
                        sameIOmotorList.append(temp)
                    if not self.failData(eachLineSplit):
                        allmotor += 1
             

        allCar = goodcar + badcar + sameIOcar
        allmotor = goodmotor + badmotor + sameIOmotor

        ans = gateCsvPath.split('/')[-1] + ',' + f"{self.ignoreFrame} / {self.ignoreFinalFrame}" + ',' + self.div( (goodcar + goodmotor) , (allCar + allmotor) ) + ',' + self.div( goodcar , allCar ) + ',' 
        ans = ans + self.div( goodmotor , allmotor ) + ',' + self.div( sameIOcar , goodcar ) + ',' + self.div( sameIOmotor , goodmotor) + ',' 
        ans = ans + str( sameIOcar ) + ',' + str( goodcar ) + ',' + str( allCar ) + ',' + str( sameIOmotor ) + ',' + str( goodmotor ) + ',' + str( allmotor )


        fp = open(resultPath, "w")
        fp.write(self.lineTitle)
        fp.write("\n")
        fp.write(ans)
        fp.write("\nSameIOCar\n")
        for i in range(0,len(sameIOcarList)):
            for k in range(0,len(sameIOcarList[i])):
                fp.write(sameIOcarList[i][k])
            fp.write("\n")
        fp.write("SameIOMotor\n")
        for i in range(0,len(sameIOmotorList)):
            for k in range(0,len(sameIOmotorList[i])):
                fp.write(sameIOmotorList[i][k])
            fp.write("\n")
        fp.close()

        lineOneSp = self.lineTitle.split(',')
        lineTwoSp = ans.split(',')
        for i in range(0 , len(lineOneSp)):
            print(lineOneSp[i] + " : " + lineTwoSp[i])

        print("Done.")

        return ans

if __name__ == '__main__':
    # Code file direct opreation
    curPath = str(pathlib.Path(__file__).parent.resolve())
    print("[Folder paht default codefile current folder.]")
    csvName = input("[Enter GATE_CSV] >> ")
    inName = curPath + '\\' + csvName
    TIVpath = curPath + '\\' + csvName[:-4] + "_TIV.csv"

    base, extension = os.path.splitext(TIVpath)
    k = 0
    while os.path.exists(TIVpath):
        k += 1
        TIVpath = f"{base}_{k}{extension}"

    currentTIVT = TIVT()
    currentTIVT.trackIntegrity(inName, TIVpath)
