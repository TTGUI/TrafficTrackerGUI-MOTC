#https://github.com/pogam/ExtractRect/blob/master/extractRect.py
import numpy as np
from scipy import ndimage, optimize
import pdb 
import matplotlib.pyplot as plt
import cv2
import matplotlib.patches as patches
import multiprocessing
import datetime

####################################################
def findMaxRect(data):
   
    '''http://stackoverflow.com/a/30418912/5008845'''

    nrows,ncols = data.shape
    w = np.zeros(dtype=int, shape=data.shape)
    h = np.zeros(dtype=int, shape=data.shape)
    skip = 1
    # area_max = (0, [])
    area_max = (1E-16, [])

    for r in range(nrows):
        for c in range(ncols):
            if data[r][c] == skip:
                continue
            if r == 0:
                h[r][c] = 1
            else:
                h[r][c] = h[r-1][c]+1
            if c == 0:
                w[r][c] = 1
            else:
                w[r][c] = w[r][c-1]+1
            minw = w[r][c]
            for dh in range(h[r][c]):
                minw = min(minw, w[r-dh][c])
                area = (dh+1)*minw
                if area > area_max[0]:
                    area_max = (area, [(r-dh, c-minw+1, r, c)])

    return area_max


########################################################################
def residual(angle,data):
   
    nx,ny = data.shape
    # opencv 3.4.6  angle     opencv 4.4  float(angle)
    M = cv2.getRotationMatrix2D(((nx-1)/2,(ny-1)/2),float(angle),1)
    RotData = cv2.warpAffine(data,M,(nx,ny),flags=cv2.INTER_NEAREST,borderValue=1)
    rectangle = findMaxRect(RotData)
    # print('residual rectangle', rectangle)
    return 1./rectangle[0]


########################################################################
def residual_star(args):
    return residual(*args)
    

########################################################################
def get_rectangle_coord(angle,data,flag_out=None):
    nx,ny = data.shape
    M = cv2.getRotationMatrix2D(((nx-1)/2,(ny-1)/2),angle,1)
    RotData = cv2.warpAffine(data,M,(nx,ny),flags=cv2.INTER_NEAREST,borderValue=1)
    rectangle = findMaxRect(RotData)

    # print('get_rectangle_coord rectangle', rectangle)
    # print('get_rectangle_coord rectangle[1]', rectangle[1])

    if len(rectangle[1]) == 0: rect_coord = []
    else: rect_coord = rectangle[1][0]
    
    if flag_out:
        return rect_coord, M, RotData
    else:
        return rect_coord, M


########################################################################
def findRotMaxRect(data_in,flag_opt=False,flag_parallel = False, nbre_angle=10,flag_out=None,flag_enlarge_img=False,limit_image_size=300):
   
    '''
    flag_opt     : True only nbre_angle are tested between 90 and 180 
                        and a opt descent algo is run on the best fit
                   False 100 angle are tested from 90 to 180.
    flag_parallel: only valid when flag_opt=False. the 100 angle are run on multithreading
    flag_out     : angle and rectangle of the rotated image are output together with the rectangle of the original image
    flag_enlarge_img : the image used in the function is double of the size of the original to ensure all feature stay in when rotated
    limit_image_size : control the size numbre of pixel of the image use in the function. 
                       this speeds up the code but can give approximated results if the shape is not simple
    '''
   
    #time_s = datetime.datetime.now()

    #make the image square
    #----------------
    # print('~~~~~data_in.shape', data_in.shape)
    nx_in, ny_in = data_in.shape
    # print('nx_in, ny_in', nx_in, ny_in)
    if nx_in != ny_in:
        n = max([nx_in,ny_in])
        data_square = np.ones([n,n])
        # xshift = (n-nx_in)/2
        # yshift = (n-ny_in)/2 
        xshift = round((n-nx_in)/2)
        yshift = round((n-ny_in)/2)
        # print('xshift, yshift', xshift, yshift)
        if yshift == 0 and (n-ny_in) != 1: # 原作者沒考慮到(n-ny_in) == 1 yshift會被當成0
            # print('n-nx_in, n-ny_in', n-nx_in, n-ny_in)
            data_square[xshift:(xshift+nx_in),:] = data_in[:,:]
        else: 
            # print('yshift', yshift)
            # print('ny_in', ny_in)
            # print('n-nx_in, n-ny_in', n-nx_in, n-ny_in)
            data_square[:,yshift:(yshift+ny_in)] = data_in[:,:]
    else:
        xshift = 0
        yshift = 0
        data_square = data_in

    #apply scale factor if image bigger than limit_image_size
    #----------------
    if data_square.shape[0] > limit_image_size:
        data_small = cv2.resize(data_square,(limit_image_size, limit_image_size),interpolation=0)
        scale_factor = 1.*data_square.shape[0]/data_small.shape[0]
    else:
        data_small = data_square
        scale_factor = 1


    # set the input data with an odd number of point in each dimension to make rotation easier
    #----------------
    nx,ny = data_small.shape
    nx_extra = -nx; ny_extra = -ny   
    if nx%2==0:
        nx+=1
        nx_extra = 1
    if ny%2==0:
        ny+=1
        ny_extra = 1
    data_odd = np.ones([data_small.shape[0]+max([0,nx_extra]),data_small.shape[1]+max([0,ny_extra])])
    data_odd[:-nx_extra, :-ny_extra] = data_small
    nx,ny = data_odd.shape
    # print('data_odd shape', data_odd.shape)
    # print('data_odd<1 shape', data_odd[data_odd<1].shape)

    nx_odd,ny_odd = data_odd.shape

    if flag_enlarge_img:
        data = np.zeros([2*data_odd.shape[0]+1,2*data_odd.shape[1]+1]) + 1
        nx,ny = data.shape
        data[int(nx/2-nx_odd/2):int(nx/2+nx_odd/2),int(ny/2-ny_odd/2):int(ny/2+ny_odd/2)] = data_odd
        # get error if no int() 
        # data[nx/2-nx_odd/2:nx/2+nx_odd/2,ny/2-ny_odd/2:ny/2+ny_odd/2] = data_odd
    else:
        data = np.copy(data_odd)
        nx,ny = data.shape
    
    #print (datetime.datetime.now()-time_s).total_seconds()

    if flag_opt:
        myranges_brute = ([(90.,180.),])
        coeff0 = np.array([0.,])
        coeff1  = optimize.brute(residual, myranges_brute, args=(data,), Ns=nbre_angle, finish=None)
        popt = optimize.fmin(residual, coeff1, args=(data,), xtol=5, ftol=1.e-5, disp=False)
        angle_selected = popt[0]
        # print('popt[0]', popt[0])
        #rotation_angle = np.linspace(0,360,100+1)[:-1]
        #mm = [residual(aa,data) for aa in rotation_angle]
        #plt.plot(rotation_angle,mm)
        #plt.show()
        #pdb.set_trace()

    else:
        rotation_angle = np.linspace(90,180,100+1)[:-1]
        args_here=[]
        for angle in rotation_angle:
            args_here.append([angle,data])
        
        if flag_parallel: 
   
            # set up a pool to run the parallel processing
            cpus = multiprocessing.cpu_count()
            pool = multiprocessing.Pool(processes=cpus)

            # then the map method of pool actually does the parallelisation  

            results = pool.map(residual_star, args_here)
            
            pool.close()
            pool.join()
            
       
        else:
            results = []
            for arg in args_here:
                results.append(residual_star(arg))
                
        argmin = np.array(results).argmin()
        angle_selected = args_here[argmin][0]
        # print('args_here[argmin][0]', args_here[argmin][0])

    rectangle, M_rect_max, RotData  = get_rectangle_coord(angle_selected,data,flag_out=True)
    #rectangle, M_rect_max  = get_rectangle_coord(angle_selected,data)

    if len(rectangle) == 0:
        if flag_out is None:
            return []
        elif flag_out == 'rotation':
            return [], None, None
        else:
            print('bad def in findRotMaxRect input. stop')
            pdb.set_trace()
    

    #print (datetime.datetime.now()-time_s).total_seconds()

    #invert rectangle 
    M_invert = cv2.invertAffineTransform(M_rect_max)
    rect_coord = [rectangle[:2], [rectangle[0],rectangle[3]] , 
                  rectangle[2:], [rectangle[2],rectangle[1]] ]
   
    #ax = plt.subplot(111)
    #ax.imshow(RotData.T,origin='lower',interpolation='nearest')
    #patch = patches.Polygon(rect_coord, edgecolor='k', facecolor='None', linewidth=2)
    #ax.add_patch(patch)
    #plt.show()

    rect_coord_ori = []
    for coord in rect_coord:
        rect_coord_ori.append(np.dot(M_invert,[coord[0],(ny-1)-coord[1],1]))

    #transform to numpy coord of input image
    coord_out = []
    for coord in rect_coord_ori:
        coord_out.append(    [ scale_factor*round(coord[0]-(nx/2-nx_odd/2),0)-xshift,\
                               scale_factor*round((ny-1)-coord[1]-(ny/2-ny_odd/2),0)-yshift])
    
    coord_out_rot = []
    coord_out_rot_h = []
    for coord in rect_coord:
        coord_out_rot.append( [ scale_factor*round(coord[0]-(nx/2-nx_odd/2),0)-xshift, \
                                scale_factor*round(coord[1]-(ny/2-ny_odd/2),0)-yshift ])
        coord_out_rot_h.append( [ scale_factor*round(coord[0]-(nx/2-nx_odd/2),0), \
                                  scale_factor*round(coord[1]-(ny/2-ny_odd/2),0) ])

    #M = cv2.getRotationMatrix2D( ( (data_square.shape[0]-1)/2, (data_square.shape[1]-1)/2 ), angle_selected,1)
    #RotData = cv2.warpAffine(data_square,M,data_square.shape,flags=cv2.INTER_NEAREST,borderValue=1)
    #ax = plt.subplot(121)
    #ax.imshow(data_square.T,origin='lower',interpolation='nearest')
    #ax = plt.subplot(122)
    #ax.imshow(RotData.T,origin='lower',interpolation='nearest')
    #patch = patches.Polygon(coord_out_rot_h, edgecolor='k', facecolor='None', linewidth=2)
    #ax.add_patch(patch)
    #plt.show()      
    
    #coord for data_in
    #----------------
    #print scale_factor, xshift, yshift
    #coord_out2 = []
    #for coord in coord_out:
    #    coord_out2.append([int(np.round(scale_factor*coord[0]-xshift,0)),int(np.round(scale_factor*coord[1]-yshift,0))])

    #print (datetime.datetime.now()-time_s).total_seconds()

    if flag_out is None:
        return coord_out
    elif flag_out == 'rotation':
        return coord_out, angle_selected, coord_out_rot
    else:
        print('bad def in findRotMaxRect input. stop')
        pdb.set_trace()

######################################################
def factors(n):    
    return set(reduce(list.__add__, 
                ([i, n//i] for i in range(1, int(n**0.5) + 1) if n % i == 0)))




def extract_rect_from_poly(img):
    """
        img: binary image  fill polygon with 255 other pixels with 0
    """
    #----------------
    a = img[::-1].T
    
    #change with 0 and 1
    idx_in  = np.where(a==255) 
    idx_out = np.where(a==0) 
    aa = np.ones_like(a)
    aa[idx_in] = 0

    #get coordinate of biggest rectangle
    #----------------
    time_start = datetime.datetime.now()

    # rect_coord_ori: [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
    # y為笛卡爾座標系跟影像座標系相反，角點以順時針排序
    rect_coord_ori, angle, coord_out_rot= findRotMaxRect(aa, flag_opt=True, nbre_angle=4,
                                                             flag_parallel=False,
                                                             flag_out='rotation',
                                                             flag_enlarge_img=False,
                                                             limit_image_size=100)
    # print('time elapsed =', (datetime.datetime.now()-time_start).total_seconds())
    # print('angle        =',  angle)
    

    #plot
    #----------------
    # fig = plt.figure()
    # ax = fig.add_subplot(121, aspect='equal')
    # ax.imshow(aa.T,origin='lower',interpolation='nearest')
    # patch = patches.Polygon(rect_coord_ori, edgecolor='green', facecolor='None', linewidth=2)
    # ax.add_patch(patch)
   
    # center_rot = ( (aa.shape[1]-1)/2, (aa.shape[0]-1)/2 )
    # if max(center_rot)%2 == 0:
    #     center_rot = (center_rot[0]+1,center_rot[1]+1) 
    # M = cv2.getRotationMatrix2D( center_rot, angle,1)
    # nx,ny = aa.shape
    # RotData = cv2.warpAffine(aa,M,(ny,nx),flags=cv2.INTER_NEAREST,borderValue=1)
    # ax = plt.subplot(122)
    # ax.imshow(RotData.T,origin='lower',interpolation='nearest')
    # patch = patches.Polygon(coord_out_rot, edgecolor='green', facecolor='None', linewidth=2)
    # ax.add_patch(patch)
    # plt.show()

    return rect_coord_ori, angle








#######################################
if __name__ == '__main__':
#######################################

    # image_name = 'QlbyX.png' 
    image_name = '3VcIL.png'
    # image_name = 'Untitled.png'
    # image_name = 'o943j.png'

    #read image
    #----------------
    import os
    if os.name == 'nt':
        frame = cv2.imdecode(np.fromfile(image_name,dtype=np.uint8),-1)
        frame = cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
        a = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)[::-1].T
    else:
        a = cv2.cvtColor(cv2.imread(image_name),cv2.COLOR_BGR2GRAY)[::-1].T
    
    
    #change with 0 and 1
    idx_in  = np.where(a==255) 
    idx_out = np.where(a==0) 
    aa = np.ones_like(a)
    aa[idx_in]  = 0

    #get coordinate of biggest rectangle
    #----------------
    time_start = datetime.datetime.now()

    # rect_coord_ori: [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
    # y為笛卡爾座標系跟影像座標系相反，角點以順時針排序
    rect_coord_ori, angle, coord_out_rot= findRotMaxRect(aa, flag_opt=False, nbre_angle=4,
                                                             flag_parallel=False,
                                                             flag_out='rotation',
                                                             flag_enlarge_img=False,
                                                             limit_image_size=100)
   
    print('time elapsed =', (datetime.datetime.now()-time_start).total_seconds())
    print('angle        =',  angle)
    print('rect_coord_ori', rect_coord_ori)
    print('coord_out_rot', coord_out_rot)
    
    #plot
    #----------------
    fig = plt.figure()
    ax = fig.add_subplot(121, aspect='equal')
    ax.imshow(aa.T,origin='lower',interpolation='nearest')
    patch = patches.Polygon(rect_coord_ori, edgecolor='green', facecolor='None', linewidth=2)
    ax.add_patch(patch)
   
    center_rot = ( (aa.shape[1]-1)/2, (aa.shape[0]-1)/2 )
    if max(center_rot)%2 == 0:
        center_rot = (center_rot[0]+1,center_rot[1]+1) 
    M = cv2.getRotationMatrix2D( center_rot, angle,1)
    nx,ny = aa.shape
    RotData = cv2.warpAffine(aa,M,(ny,nx),flags=cv2.INTER_NEAREST,borderValue=1)
    ax = plt.subplot(122)
    ax.imshow(RotData.T,origin='lower',interpolation='nearest')
    patch = patches.Polygon(coord_out_rot, edgecolor='green', facecolor='None', linewidth=2)
    ax.add_patch(patch)
    plt.show()



