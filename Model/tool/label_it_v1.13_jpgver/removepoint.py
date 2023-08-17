import os


current_path = os.path.dirname(__file__)
print("DIR : " + current_path)

fileList =  os.listdir(current_path) 

print ("=====  OR file  =====")
print (fileList)
print ("=====  =======  =====")


for fname in fileList :
    if fname != "removepoint.py" :
        newName = ""
        for i in range(0,len(fname)-4):
            
            if fname[i] != '.':
                newName += fname[i]
            else: 
                newName += '_'
        fname = current_path+"\\"+fname
        newName = current_path+"\\"  + newName + ".jpg"
        print(str(fname) + " ==>> " + str(newName))
       
        os.rename(fname,newName)
        