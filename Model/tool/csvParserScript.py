
import csvParser
import argparse
import os

currentClass = csvParser.csvParse()



folder = r"E:\Traffic\Block14_桃園_台南\臺南市新市區台1線中山路_中華路\11207_120m_"

folder_B = r"架次\行人分支\0908\\"

alphaBete = "D"
folder = folder + alphaBete + folder_B
actionName = "臺南市新化區台1線中山路中華路_" + alphaBete 

os.rename( str(folder + actionName + "_gate.csv"), str(folder + actionName + "_gate(P).csv"))

args = currentClass.parser.parse_args([
    '-c', folder + actionName + "_gate(A).csv", 
    '-rcl', 'p',
    '-a', folder + actionName + "_gate(P).csv",
    '-s', 
    '-o', 
    folder + actionName + "_gate.csv"
    ])

currentClass.main(args)




# os.rename(r'e:\Traffic\Block14_桃園_台南\桃園市高鐵北路一段、青心路\1120704_60m_B架次\行人分支\0821_RGGray\桃園市高鐵北路一段青心路_B_gate.csv', r'e:\Traffic\Block14_桃園_台南\桃園市高鐵北路一段、青心路\1120704_60m_B架次\行人分支\0821_RGGray\桃園市高鐵北路一段青心路_B_gate(P).csv')
# args = currentClass.parser.parse_args([
#     '-c', r'e:\Traffic\Block14_桃園_台南\桃園市高鐵北路一段、青心路\1120704_60m_B架次\行人分支\0821_RGGray\桃園市高鐵北路一段青心路_B_gate(A).csv', 
#     '-rcl', 'p',
#     '-a', r'e:\Traffic\Block14_桃園_台南\桃園市高鐵北路一段、青心路\1120704_60m_B架次\行人分支\0821_RGGray\桃園市高鐵北路一段青心路_B_gate(P).csv',
#     '-s', 
#     '-o', 
#     r'e:\Traffic\Block14_桃園_台南\桃園市高鐵北路一段、青心路\1120704_60m_B架次\行人分支\0821_RGGray\桃園市高鐵北路一段青心路_B_gate.csv'
#     ])

# currentClass.main(args)
