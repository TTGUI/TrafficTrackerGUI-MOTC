import os
from logs import logger


if __name__ == '__main__':
    print("::::Stabilization.py Example::::")
    print("> Please put the video which need to stabilez in same directrory,")
    print("> and make the file name as '1.mp4'.")
    print("> sand then there were be a file output as '2.avi'.")



def stab_main(stab_input,stab_output,show,cut_txt, output_height=2160, output_width=3840):
    # cmd = '.\Model\ECC_GPU.exe ' + './Model/fuck' + ' ' + './Model/out.avi' + ' ' +  './Model/cut.txt' + ' -e=1e-6 -N=300 -v=1 -l=1'
    if show:
        cmd = r'.\Model\Stab_ECC_GPU_source\x64\Release\Stab_ECC_GPU_source.exe ' + stab_input + ' ' + stab_output + ' ' +  cut_txt + ' -e=0.0005 -N=300 -v=1 -l=1 ' + f'-h={output_height} -w={output_width}'
    else:
        cmd = r'.\Model\Stab_ECC_GPU_source\x64\Release\Stab_ECC_GPU_source.exe ' + stab_input + ' ' + stab_output + ' ' +  cut_txt + ' -e=0.0005 -N=300 -v=0 -l=1 ' + f'-h={output_height} -w={output_width}'
    os.system(cmd)
