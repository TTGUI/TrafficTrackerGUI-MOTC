import os

current_path = os.path.dirname(__file__)
print("DIR : " + current_path)

fileList =  os.listdir(current_path) 

print ("=====  OR file  =====")
print (fileList)
print ("=====  =======  =====")


for fname in fileList :
    if fname != "changeFileName.py" :
        newName = ""
        for i in range(0,len(fname)):
            if ord(fname[i]) >= 20 and ord(fname[i]) <= 126 :
                if not (len(newName) == 0 and fname[i] == "_") :
                    newName = newName + fname[i]

        fname = current_path+"\\"+fname
        newName = current_path+"\\"+newName
        print(str(fname) + " ==>> " + str(newName))
       
        os.rename(fname,newName)
        