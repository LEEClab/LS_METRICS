import os, platform
import grass.script as grass,array
import numpy as np
import grass.script.array as garray


def readCSV(filename):
    """
    This function creates the formatting for output names.
    It combines a given prefix with an index number to generate
    consistent and organized output raster names.
    Example: prefix_01, prefix_02, etc.
    """
    with open(filename) as file:
        lines = [line.rstrip() for line in file]
    auxListCodname=[]
    auxListCodprocess=[]
    for i in lines:  
        valueLimpo=int(i.replace(',',''))
        auxListCodprocess.append(valueLimpo)
        pre_numb = '00000{}'.format(valueLimpo)
        pre_numb = pre_numb[-5:]
        #print(pre_numb)
        auxListCodname.append(pre_numb)
    return(auxListCodname,auxListCodprocess)
    

def proportionGenerator(mapin,dir,windowsize):
    __classes = grass.read_command('r.stats', input=mapin, flags='l',output=dir+'rstats.txt', separator=',',overwrite = True) # geting values rast
    CodName,CodProcess=readCSV(dir+'rstats.txt') # Calling the function to generate an output name with the prefix 'raster' and index 1
    
    contaux=0
    lisMapAux=[]
    
    # looping in list of the cods
    for i in CodProcess:
        expression1 = '{}_C{} = if({} == {},{},0)'.format(mapin,CodName[contaux],mapin,i,1) # input expression for r.mapcalc
        grass.mapcalc(expression1, overwrite = True, quiet = True) # exec expression
        
        # Running r.neighbors on a specific class to apply a neighborhood operation (e.g., smoothing or majority filter)
        grass.run_command('r.neighbors', input = '{}_C{}'.format(mapin,CodName[contaux]), output = '{}_C{}_WS{}'.format(mapin,CodName[contaux],windowsize), method = 'sum', size = 3, overwrite = True, flags = 'c')
        
        
        lisMapAux.append('{}_C{}_WS{}'.format(mapin,CodName[contaux],windowsize))
        contaux=contaux+1
    os.remove(dir+'rstats.txt') # removin txt aux cods file external
    print(lisMapAux)
    grass.run_command('r.series', input = lisMapAux, output = 'sumRasts', method = 'sum', overwrite = True) # creating rast map sum.
    
    #loop creating Proportions
    for i in lisMapAux:
        expression1 = '{}_pi={}/sumRasts'.format(i,i) # creating proportion map
        grass.mapcalc(expression1, overwrite = True, quiet = True)
    
    # remove aux files
    #grass.run_command('g.remove', type="raster", name='sumRasts', flags='f') # remove sumRasts <uncomment> 
        
        
    
# change parameters 

inputamp ='cenario_4_cut_teste' # map rast name
dirfolder = 'D:/_____dados/Space__Gits/LS_METRICS/DB_demo/ScriptShannon/' # Setting the path to the directory containing the raster files
windowsize = 3 # windowsize for using moviwindow

proportionGenerator(inputamp,dirfolder,windowsize) #calling funcion
