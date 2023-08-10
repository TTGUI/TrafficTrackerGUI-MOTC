
import csvParser
import argparse

currentClass = csvParser.csvParse()

args = currentClass.parser.parse_args([
    '-c', r'e:\Traffic\Block14_桃園_台南\桃園市高鐵北路一段、青心路\1120704_60m_B架次\行人分支\0809\桃園市高鐵北路一段青心路_B_gate(A).csv', 
    '-rcl', 'p',
    '-a', r'e:\Traffic\Block14_桃園_台南\桃園市高鐵北路一段、青心路\1120704_60m_B架次\行人分支\0809\桃園市高鐵北路一段青心路_B_gate(P).csv',
    '-s', 
    '-o', 
    r'e:\Traffic\Block14_桃園_台南\桃園市高鐵北路一段、青心路\1120704_60m_B架次\行人分支\0809\桃園市高鐵北路一段青心路_B_gate.csv'
    ])

currentClass.main(args)

args = currentClass.parser.parse_args([
    '-c', r'e:\Traffic\Block14_桃園_台南\桃園市高鐵北路一段、青心路\1120704_60m_C架次\行人分支\0809\桃園市高鐵北路一段青心路_C_gate(A).csv', 
    '-rcl', 'p',
    '-a', r'e:\Traffic\Block14_桃園_台南\桃園市高鐵北路一段、青心路\1120704_60m_C架次\行人分支\0809\桃園市高鐵北路一段青心路_C_gate(P).csv',
    '-s', 
    '-o', 
    r'e:\Traffic\Block14_桃園_台南\桃園市高鐵北路一段、青心路\1120704_60m_C架次\行人分支\0809\桃園市高鐵北路一段青心路_C_gate.csv'
    ])

currentClass.main(args)

args = currentClass.parser.parse_args([
    '-c', r'e:\Traffic\Block14_桃園_台南\桃園市高鐵北路一段、青心路\1120704_60m_D架次\行人分支\0809\桃園市高鐵北路一段青心路_D_gate(A).csv', 
    '-rcl', 'p',
    '-a', r'e:\Traffic\Block14_桃園_台南\桃園市高鐵北路一段、青心路\1120704_60m_D架次\行人分支\0809\桃園市高鐵北路一段青心路_D_gate(P).csv',
    '-s', 
    '-o', 
    r'e:\Traffic\Block14_桃園_台南\桃園市高鐵北路一段、青心路\1120704_60m_D架次\行人分支\0809\桃園市高鐵北路一段青心路_D_gate.csv'
    ])

currentClass.main(args)

