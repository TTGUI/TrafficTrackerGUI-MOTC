import math
  
fp = open('彰化縣公園路一段_中山路二段路口120米_C_gate.csv', 'r')
lines = fp.readlines()
fp.close()

fout = open('彰化縣公園路一段_中山路二段路口120米_C_gate_bike.csv', 'w')

interval = 8*10 # 10frames = 1sec
pixelsize = 0.08 #0.08 m/pixel
LowerBound = 2.8/pixelsize # 30km/s = 8.3m/s

i = 0
for i in range(0, len(lines)):
    V = lines[i].split(",")
    
    if len(V) > 6+interval:
        if V[5] == 'm' and V[4] != 'X' and V[3] != 'X' :
            Cx = (int(V[6])+int(V[8])+int(V[10])+int(V[12]))/4
            Cy = (int(V[7])+int(V[9])+int(V[11])+int(V[13]))/4
            Cx2 = (int(V[len(V)-8])+int(V[len(V)-6])+int(V[len(V)-4])+int(V[len(V)-2]))/4
            Cy2 = (int(V[len(V)-7])+int(V[len(V)-5])+int(V[len(V)-3])+int(V[len(V)-1]))/4            
            dist = math.sqrt((Cx2-Cx)*(Cx2-Cx)+(Cy2-Cy)*(Cy2-Cy))
            if dist > LowerBound:
                V[5] = 'u'
                for j in range(6, len(V)-interval, 8):
                    Cx = (int(V[j])+int(V[j+2])+int(V[j+4])+int(V[j+6]))/4
                    Cy = (int(V[j+1])+int(V[j+3])+int(V[j+5])+int(V[j+7]))/4
                    Cx2 = (int(V[j+interval])+int(V[j+2+interval])+int(V[j+4+interval])+int(V[j+6+interval]))/4
                    Cy2 = (int(V[j+1+interval])+int(V[j+3+interval])+int(V[j+5+interval])+int(V[j+7+interval]))/4
                    dist = math.sqrt((Cx2-Cx)*(Cx2-Cx)+(Cy2-Cy)*(Cy2-Cy))
                    if dist > LowerBound: 
                        V[5] = 'm'
                        break
            V = ",".join(V)
            fout.writelines(V)  
           
fout.close()
