
import pathlib


# 讀取CSV軌跡並輸出完整度



class TIVT:
    def __init__(self):
        self.lineTitle = "gate.csv,汽機車完整度比例,汽車完整度比例,機車完整度比例,汽車同方向進出佔完整軌跡比例,機車同方向進出佔完整軌跡比例"
        self.lineTitle = self.lineTitle + ",汽車同方向進出數量,汽車完整軌跡數量,汽車總軌跡數量(濾除全X),機車同方向進出數量,機車完整軌跡數量,機車總軌跡數量(濾除全X)"        
        print("[TIVT Start.]")

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

    def trackIntegrity(self, gateCsvPath, actionName, resultPath) :
        resultPath = resultPath + actionName + "_TIV.csv"
        f = open(gateCsvPath, 'r')
        lines = f.readlines()
        f.close()

        goodcar = 0
        badcar = 0
        sameIOcar = 0
        allCar = 0
        
        goodmotor = 0
        badmotor = 0
        sameIOmotor = 0
        allmotor = 0

        for i in range ( 0 , len(lines)):
            eachLineSplit = lines[i].split(",")
            if self.vehicleTypeBool('c', eachLineSplit):
                if self.goodData(eachLineSplit):
                    goodcar += 1
                if self.badData(eachLineSplit):
                    badcar += 1
                if self.sameIO(eachLineSplit):
                    sameIOcar += 1
                if not self.failData(eachLineSplit):
                    allCar += 1

            if self.vehicleTypeBool('m', eachLineSplit):
                if self.goodData(eachLineSplit):
                    goodmotor += 1
                if self.badData(eachLineSplit):
                    badmotor += 1
                if self.sameIO(eachLineSplit):
                    sameIOmotor += 1
                if not self.failData(eachLineSplit):
                    allmotor += 1
             



        ans = gateCsvPath.split('/')[-1] + ',' + self.div( (goodcar + goodmotor) , (allCar + allmotor) ) + ',' + self.div( goodcar , allCar ) + ',' 
        ans = ans + self.div( goodmotor , allmotor ) + ',' + self.div( sameIOcar , goodcar ) + ',' + self.div( sameIOmotor , goodmotor) + ',' 
        ans = ans + str( sameIOcar ) + ',' + str( goodmotor ) + ',' + str( allCar ) + ',' + str( sameIOmotor ) + ',' + str( goodmotor ) + ',' + str( allmotor )


        fp = open(resultPath, "w")
        fp.write(self.lineTitle)
        fp.write("\n")
        fp.write(ans)
        fp.close()

        # print("good car : " + str(goodcar))
        # print("bad car : " + str(badcar) )
        # print("same IO : " + str(sameIOcar))
        # print("all car : " + str(allCar))

        # print("good motor : " + str(goodmotor))
        # print("bad motor : " + str(badmotor) )
        # print("same IO : " + str(sameIOmotor))
        # print("all motor : " + str(allmotor))

        lineOneSp = self.lineTitle.split(',')
        lineTwoSp = ans.split(',')
        for i in range(0 , len(lineOneSp)):
            print(lineOneSp[i] + " : " + lineTwoSp[i])

        print("Done.")

        return ans

if __name__ == '__main__':
    # Code file direct opreation
    curPath = str(pathlib.Path(__file__).parent.resolve())
    csvName = input("Enter GATE_CSV name, folder paht default codefile current folder : ")
    inName = curPath + '\\' + csvName
    curPath = curPath + '\\'
    currentTIVT = TIVT()
    currentTIVT.trackIntegrity(inName, csvName[:-9], curPath)