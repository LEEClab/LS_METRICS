#!/c/Python25 python
#---------------------------------------------------------------------------------------
"""
 LSMetrics - Ecologically Scaled Landscape Metrics
 Version 1.0.0
 
 Milton C. Ribeiro - mcr@rc.unesp.br
 John W. Ribeiro - jw.ribeiro.rc@gmail.com
 Bernardo B. S. Niebuhr - bernardo_brandaum@yahoo.com.br
 
 Laboratorio de Ecologia Espacial e Conservacao (LEEC)
 Universidade Estadual Paulista - UNESP
 Rio Claro - SP - Brasil
 
 LSMetrics is a software designed to calculate landscape metrics and
 landscape statistics and generate maps of landscape connectivity.
 Also, the software is designed to prepare maps and enviroment for running 
 BioDIM, an individual-based model of animal movement in fragmented landscapes.
 The software runs in a GRASS GIS environment and uses raster images as input.

 To run LSMetric:
 python LSMetrics_v1_0_0.py
 
 Copyright (C) 2015-2016 by Milton C. Ribeiro, John W. Ribeiro, and Bernardo B. S. Niebuhr.

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 2 of the license, 
 or (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
#---------------------------------------------------------------------------------------

# Import modules
import os, platform
import grass.script as grass
from PIL import Image
import wx
import numpy as np
import math # SUBSTITUIR POR NUMPY? numpy.log(number)
from sets import Set
import collections

# Platform in which LSMetrics is being run
CURRENT_OS = platform.system()

# LSMetrics Version:
VERSION = 'v. 1.0.0'

################
# CONFERIR LISTA DE PATTERN MULTIPLE COM O JOHN (E TODAS AS VEZES QUE APARECEU O [PERMANENT] OU [userbase])

########################
# -arrumar script R para gerar as figuras que queremos
# como conversa o R com o grass? da pra rodar o script R em BATCH mode?

#----------------------------------------------------------------------------------
def reclass_frag_cor(mappidfrag,dirs):
  """
  essa funcao abre o txt cross separa os de transicao validos
  reclassifica o mapa de pidfrag onde 1
  """
  os.chdir(dirs)
  with open("table_cross.txt") as f:
      data = f.readlines()
  
  contfirst=0
  list_pidfrag=[]
  list_pid_cor=[]
  for i in data:
      if contfirst>0: # pulando a primeira linha da tabela 
          if "no data" in i:
              pass
          else:
              lnsplit=i.split(' ')
              list_pidfrag.append(lnsplit[2].replace(';',''))
              list_pid_cor.append(lnsplit[4])    
      contfirst=1
  list_pidfrag=map(int, list_pidfrag)   
  list_pid_cor=map(int, list_pid_cor)   
  counter=collections.Counter(list_pid_cor)
  txt_rules=open("table_cross_reclass_rules.txt",'w')
  for i in counter.keys():
    if counter[i]>=2:
        temp=2
    else:
        temp=1
    txt_rules.write(`i`+'='+`temp`+'\n')
  txt_rules.close() 
  grass.run_command('r.reclass',input=mappidfrag,output=mappidfrag+'_reclass',rules='table_cross_reclass_rules.txt', overwrite = True)
  
  
  
  
  
def getsizepx(mapbin_HABITAT, esc):
  '''
  Function getsizepx
  
  This function uses the scale difined by the user and the pixel size to 
  return the number of pixels that correspond to scale (size of the moving window)
  '''
  
  res = grass.parse_command('g.region', rast=mapbin_HABITAT, flags='m')      
  res3 = float(res['ewres'])  
  fine_scale=(float(esc)*2)/res3
  
  # Checking if number of pixels of moving window is integer and even
  #  and correcting it if necessary
  if int(fine_scale)%2 == 0:
    fine_scale=int(fine_scale)
    fine_scale=fine_scale+1 
  else:
    fine_scale=int(fine_scale)
  
  return fine_scale

#----------------------------------------------------------------------------------
# Auxiliary functions

# Output for preparing BioDIM environment

def create_TXTinputBIODIM(list_maps, outPrefixmap, outputfolder):
  
  txtMap = open(outputfolder+"/"+outPrefixmap+".txt", "w")
  for i in list_maps:
    txtMap.write(i+'\n')
  txtMap.close()
    
#----------------------------------------------------------------------------------
# Output for statistics

def createtxt(mapa, dirs, outname=False):
  """
  This function creates a text file with:
  - Values of area, in hectares, for edge, interior and core areas (for EDGE metrics)
  - Calues of area, in hectares, for each patch (for PATCH, FRAG and CON metrics)
  """
  x=grass.read_command('r.stats',flags='a',input=mapa)
  
  y=x.split('\n')
  os.chdir(dirs)
  if outname:
    txtsaida=outname+'.txt'
  else:
    txtsaida=mapa+'.txt'
  txtreclass=open(txtsaida, 'w')
  txtreclass.write('COD'+','+'HA\n')
  if len(y)!=0:
    for i in y:
      if i !='':
        ##print i
        f=i.split(' ')
        if '*' in f :
          break
        else:
          ##print f
          ids=f[0]
          ids=int(ids)
          ##print ids
          ha=f[1]
          ha=float(ha)
          haint=float(ha)
          haint=haint/10000+1
          ##print haint
          
          ##print haint
          
          txtreclass.write(`ids`+','+`haint`+'\n')
  txtreclass.close()

#----------------------------------------------------------------------------------
# Auxiliary functions

def selectdirectory():
  dialog = wx.DirDialog(None, "Select the folder where the output files will be saved:",
                        style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
  if dialog.ShowModal() == wx.ID_OK:
    #print ">>..................",dialog.GetPath()
    return dialog.GetPath()

def createBinarios_single(ListMapBins, prepareBIODIM):
  """
  This function reclassify an input map into a binary map, according to reclassification rules passed by
  a text file
  """
  readtxt=selectdirectory()
  grass.run_command('g.region',rast=ListMapBins)
  grass.run_command('r.reclass',input=ListMapBins,output=ListMapBins+'_HABMAT',rules=readtxt, overwrite = True)
  
  if prepareBIODIM:
    mapsList=grass.list_grouped ('rast', pattern='(*)') ['userbase']
  else:
    mapsList=grass.list_grouped ('rast', pattern='(*)') ['PERMANENT']  
  return readtxt
  
def createBinarios(ListMapBins, prepareBIODIM):
  """
  This function reclassify a series of input maps into binary maps, according to reclassification rules passed by
  a text file
  """
  readtxt=selectdirectory()
  for i in ListMapBins:
    grass.run_command('g.region',rast=i)
    grass.run_command('r.reclass',input=i,output=i+'_HABMAT',rules=readtxt, overwrite = True)
    if prepareBIODIM:
      mapsList=grass.list_grouped ('rast', pattern='(*)') ['userbase']
    else:
      mapsList=grass.list_grouped ('rast', pattern='(*)') ['current_mapset']    
    return readtxt
  
def create_habmat_single(ListMapBins_in, prefix, list_habitat_classes, prepareBIODIM, calcStatistics, dirout):
  
  """
  Function for a single map
  This function reclassify an input map into a binary map, according to reclassification rules passed by
  a text file
  """

  ListMapBins = prefix+ListMapBins_in
  
  # opcao 1: ler um arquivo e fazer reclass
  # TEMOS QUE ORGANIZAR ISSO AINDA!!
  #readtxt=selectdirectory()
  #grass.run_command('g.region',rast=ListMapBins)
  #grass.run_command('r.reclass',input=ListMapBins,output=ListMapBins+'_HABMAT',rules=readtxt, overwrite = True)
  
  # opcao 2: definir quais classes sao habitat; todas as outras serao matriz
  if(len(list_habitat_classes) > 0):
    
    conditional = ''
    cc = 0
    for j in list_habitat_classes:
      if cc > 0:
        conditional = conditional+' || '
      conditional = conditional+ListMapBins_in+' == '+j
      cc += 1
      
    expression = ListMapBins+'_HABMAT = if('+conditional+', 1, 0)'
    grass.run_command('g.region', rast=ListMapBins_in)
    grass.mapcalc(expression, overwrite = True, quiet = True)
    grass.run_command('r.null', map=ListMapBins+'_HABMAT', null='0') # precisa disso??, nao sei .rsrs 
  else:
    print 'You did not type which class is habitat!! Map not generated' # organizar para dar um erro; pode ser com try except 
    
  if prepareBIODIM:
    create_TXTinputBIODIM([ListMapBins+'_HABMAT'], "simulados_HABMAT", dirout)   
  else:
    grass.run_command('g.region', rast=ListMapBins+'_HABMAT')
    grass.run_command('r.out.gdal', input=ListMapBins+'_HABMAT', out=ListMapBins+'_HABMAT.tif',overwrite = True)
  
  if calcStatistics:
    createtxt(ListMapBins+'_HABMAT', dirout, ListMapBins+'_HABMAT')


def create_habmat(ListMapBins, list_habitat_classes, prepareBIODIM, calcStatistics, dirout, prefix = ''):
  """
  Function for a series of maps
  This function reclassify an input map into a binary map, according to reclassification rules passed by
  a text file
  """
  
  if prepareBIODIM:
    lista_maps_habmat=[]  
  
  # opcao 1: ler um arquivo e fazer reclass
  # TEMOS QUE ORGANIZAR ISSO AINDA!!
  #readtxt=selectdirectory()
  #grass.run_command('g.region',rast=ListMapBins)
  #grass.run_command('r.reclass',input=ListMapBins,output=ListMapBins+'_HABMAT',rules=readtxt, overwrite = True)
  
  # opcao 2: definir quais classes sao habitat; todas as outras serao matriz
  cont = 1
  for i_in in ListMapBins:
    
    if prefix == '':
      pre_numb = ''
    else:
      if cont <= 9:
        pre_numb = "000"+`cont`+'_'
      elif cont <= 99:
        pre_numb = "00"+`cont`+'_'
      elif cont <= 999:        
        pre_numb = "0"+`cont`+'_'
      else: 
        pre_numb = `cont`+'_'
    
    if(len(list_habitat_classes) > 0):
      conditional = ''
      cc = 0
      for j in list_habitat_classes:
        if cc > 0:
          conditional = conditional+' || '
        conditional = conditional+i_in+' == '+j
        cc += 1
      
      i = prefix+pre_numb+i_in
      
      expression = i+'_HABMAT = if('+conditional+', 1, 0)'
      grass.run_command('g.region', rast=i_in)
      grass.mapcalc(expression, overwrite = True, quiet = True)
      grass.run_command('r.null', map=i+'_HABMAT', null='0') # precisa disso?? 
    else:
      print 'You did not type which class is habitat!! Map not generated' # organizar para dar um erro; pode ser com try except 
    
    if prepareBIODIM:
      lista_maps_habmat.append(i+'_HABMAT') 
    else:
      grass.run_command('g.region', rast=i+'_HABMAT')
      grass.run_command('r.out.gdal', input=i+'_HABMAT', out=i+'_HABMAT.tif',overwrite = True)
  
    if calcStatistics:
      createtxt(i+'_HABMAT', dirout, i+'_HABMAT')
      
    cont += 1
      
  if prepareBIODIM:
    create_TXTinputBIODIM(lista_maps_habmat, "simulados_HABMAT", dirout)  
    
def rulesreclass(mapa, dirs):
  """
  This function sets the rules for area reclassification for patch ID, using stats -a for each patch.
  The output is a text file with such rules
  """
  grass.run_command('g.region',rast=mapa)
  x=grass.read_command('r.stats',flags='a',input=mapa)
  
  y=x.split('\n')
 
  os.chdir(dirs)
  txtsaida=mapa+'_rules.txt'
  txtreclass=open(mapa+'_rules.txt','w')
    
  if y!=0:
    for i in y:
          if i !='':
                ##print i
                f=i.split(' ')
          if '*' in f or 'L' in f :
                break
          else:
                ##print f 
                ids=f[0]
                ids=int(ids)
                ##print ids
                ha=f[1]
                ha=float(ha)
                haint=float(round(ha))
                
                ##print haint
                haint2=haint/10000+1
                txtreclass.write(`ids`+'='+`haint2`+ '\n')
    txtreclass.close()      
  return txtsaida

def exportPNG(mapinp=[]):
  """ 
  This function exports a series of raster maps as png images
  """
  lista_png=[]
  for i in mapinp:
    grass.run_command('r.out.png',input=i,out=i)
    lista_png.append(i+'.png')
  return lista_png

#----------------------------------------------------------------------------------
# Leading with scales - organization
 
def escala_con(mapa,esc):
  """
  This function separates the input for functional connectivity maps (CON), separatins scales (distances)
  which will be used to generate the maps. Also, it defines the numbers of pixels to consider, besides distances
  ############# EH ISSO?
  """
  esclist=esc.split(',')
  res=grass.parse_command('g.region', rast=mapa, flags='m')
  res2=float(res['ewres'])
  listasizefinal=[]
  listametersfinal=[]  
  for i in esclist:
    esc=int(i)
    fine_scale=(esc)/res2
    
    fine_scale=int(round(fine_scale, ndigits=0))  
    if fine_scale%2==0:
      fine_scale=int(fine_scale)
      fine_scale=fine_scale+1
      listasizefinal.append(fine_scale)
      listametersfinal.append(esc)
    else:
      fine_scale=int(round(fine_scale, ndigits=0))
      listasizefinal.append(fine_scale)
      listametersfinal.append(esc)      
  return listasizefinal,listametersfinal # number of pixels+1, number of meters
    
def escala_frag(mapa,esclist):
  """
  This function separates the input for fragmented maps (FRAG, excluding corridors/edges), 
  separatins scales (distances) which will be used to generate the maps. 
  Also, it defines the numbers of pixels to consider, besides distances
  ############# EH ISSO?
  """
  esclist_splited=esclist.split(',')
  res=grass.parse_command('g.region', rast=mapa, flags='m')
  res2=float(res['ewres'])
  listasizefinal=[]
  listametersfinal=[]
  for i in esclist_splited:
    esc=int(i)
    fine_scale=esc/res2
    fine_scale=fine_scale*2 # pq vezes 2?
    if fine_scale%2==0:
      fine_scale=int(fine_scale)
      fine_scale=fine_scale+1
      listasizefinal.append(fine_scale)
      listametersfinal.append(esc)
    else:
      fine_scale=int(round(fine_scale, ndigits=0))
      listasizefinal.append(fine_scale)
      listametersfinal.append(esc)      
  return listasizefinal,listametersfinal

#----------------------------------------------------------------------------------
# Metrics for fragmented (excluding edges/corridors) views of landscapes (FRAG)

def areaFragSingle(map_HABITAT_Single, prefix,list_esc_areaFrag,dirout,prepareBIODIM,calcStatistics,removeTrash):
  """
  Function for a single map
  This function fragments patches (FRAG), excluding corridors and edges given input scales (distances), and:
  - generates and exports maps with Patch ID and Area of each "fragmented" patch
  - generatics statistics - Area per patch (if calcStatistics == True)
  """
  
  ListmapsFrag = prefix+map_HABITAT_Single
  
  grass.run_command('g.region', rast=map_HABITAT_Single)
  Lista_escalafragM, listmeters = escala_frag(map_HABITAT_Single,list_esc_areaFrag)

  x=0
  for a in Lista_escalafragM:
    
    meters=int(listmeters[x])  
    #print escalafragM
    grass.run_command('r.neighbors', input=map_HABITAT_Single, output=ListmapsFrag+"_ero_"+`meters`+'m', method='minimum', size=a, overwrite = True)
    grass.run_command('r.neighbors', input=ListmapsFrag+"_ero_"+`meters`+'m', output=ListmapsFrag+"_dila_"+`meters`+'m', method='maximum', size=a, overwrite = True)
    expression1=ListmapsFrag+"_FRAG"+`meters`+"m_mata = if("+ListmapsFrag+"_dila_"+`meters`+'m'+" > 0, "+ListmapsFrag+"_dila_"+`meters`+'m'+", null())"
    grass.mapcalc(expression1, overwrite = True, quiet = True)
    expression2=ListmapsFrag+"_FRAG"+`meters`+"m_mata_lpo = if("+map_HABITAT_Single+" >= 0, "+ListmapsFrag+"_FRAG"+`meters`+"m_mata, null())"
    grass.mapcalc(expression2, overwrite = True, quiet = True)
    grass.run_command('r.clump', input=ListmapsFrag+"_FRAG"+`meters`+"m_mata_lpo", output=ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_pid", overwrite = True)
    
    grass.run_command('g.region', rast=ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_pid")
    nametxtreclass=rulesreclass(ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_pid", dirout)
    grass.run_command('r.reclass', input=ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_pid", output=ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_AreaHA", rules=nametxtreclass, overwrite = True)   
    os.remove(nametxtreclass)
    
    # identificando branch tampulins e corredores
    
    
    expression3='temp_BSSC=if(isnull('+ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_AreaHA"+'),'+map_HABITAT_Single+')'
    grass.mapcalc(expression3, overwrite = True, quiet = True)    
     
    expression1="MapaBinario=temp_BSSC"
    grass.mapcalc(expression1, overwrite = True, quiet = True)    
    grass.run_command('g.region',rast="MapaBinario")
    expression2="A=MapaBinario"
    grass.mapcalc(expression2, overwrite = True, quiet = True)
    grass.run_command('g.region',rast="MapaBinario")
    expression3="MapaBinario_A=if(A[0,0]==0 && A[0,-1]==1 && A[1,-1]==0 && A[1,0]==1,1,A)"
    grass.mapcalc(expression3, overwrite = True, quiet = True)
    expression4="A=MapaBinario_A"
    grass.mapcalc(expression4, overwrite = True, quiet = True)
    expression5="MapaBinario_AB=if(A[0,0]==0 && A[-1,0]==1 && A[-1,1]==0 && A[0,1]==1,1,A)"
    grass.mapcalc(expression5, overwrite = True, quiet = True) 
    expression6="A=MapaBinario_AB"
    grass.mapcalc(expression6, overwrite = True, quiet = True)
    expression7="MapaBinario_ABC=if(A[0,0]==0 && A[0,1]==1 && A[1,1]==0 && A[1,0]==1,1,A)"
    grass.mapcalc(expression7, overwrite = True, quiet = True)
    expression8="A=MapaBinario_ABC"
    grass.mapcalc(expression8, overwrite = True, quiet = True)
    expression9="MapaBinario_ABCD=if(A[0,0]==0 && A[1,0]==1 && A[1,1]==0 && A[0,1]==1,1,A)"
    grass.mapcalc(expression9, overwrite = True, quiet = True)
   
    expression4='MapaBinario_ABCD1=if(MapaBinario_ABCD==0,null(),1)'
    grass.mapcalc(expression4, overwrite = True, quiet = True)    
    grass.run_command('r.clump', input='MapaBinario_ABCD1', output="MapaBinario_ABCD1_pid", overwrite = True)
    
    grass.run_command('r.neighbors', input='MapaBinario_ABCD1_pid', output='MapaBinario_ABCD1_pid_mode', method='mode', size=3, overwrite = True)
    grass.run_command('r.cross', input=ListmapsFrag+"_FRAG"+`meters`+'m_mata_clump_pid,MapaBinario_ABCD1_pid_mode',out=ListmapsFrag+"_FRAG"+`meters`+'m_mata_clump_pid_cross_corredor',overwrite = True)
    cross_TB = grass.read_command('r.stats', input=ListmapsFrag+"_FRAG"+`meters`+'m_mata_clump_pid_cross_corredor', flags='l')  # pegando a resolucao
    print cross_TB 
    txt=open("table_cross.txt",'w')
    txt.write(cross_TB)
    txt.close()
    
    reclass_frag_cor('MapaBinario_ABCD1_pid', dirout)
    
    expression10='MapaBinario_ABCD1_pid_reclass_sttepings=if(isnull(MapaBinario_ABCD1_pid_reclass)&&temp_BSSC==1,3,MapaBinario_ABCD1_pid_reclass)'
    grass.mapcalc(expression10, overwrite = True, quiet = True)    
    expression11='MapaBinario_ABCD1_pid_reclass_sttepings2=if(temp_BSSC==1,MapaBinario_ABCD1_pid_reclass_sttepings,null())'
    grass.mapcalc(expression11, overwrite = True, quiet = True)     
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    if prepareBIODIM:
      #grass.run_command('r.out.gdal',input=ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_pid",out=ListmapsFrag+"_FRAG"+`meters`+"m_PID.tif")
      create_TXTinputBIODIM([ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_pid"], "simulados_HABMAT_FRAC_"+`meters`+"m_PID", dirout)
      create_TXTinputBIODIM([ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_AreaHA"], "simulados_HABMAT_FRAC_"+`meters`+"m_AREApix", dirout)
    else:
      grass.run_command('g.region', rast=ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_AreaHA")
      grass.run_command('r.out.gdal', input=ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_AreaHA", out=ListmapsFrag+"_FRAG"+`meters`+"m_AreaHA.tif",overwrite = True)      
      
    if calcStatistics:
      createtxt(ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_pid", dirout, ListmapsFrag+"_FRAG"+`meters`+"m_AreaHA")        
    
    if removeTrash:
      if prepareBIODIM:
        txts = [ListmapsFrag+"_ero_"+`meters`+'m', ListmapsFrag+"_dila_"+`meters`+'m', ListmapsFrag+"_FRAG"+`meters`+"m_mata", ListmapsFrag+"_FRAG"+`meters`+"m_mata_lpo"]
      else:
        txts = [ListmapsFrag+"_ero_"+`meters`+'m', ListmapsFrag+"_dila_"+`meters`+'m', ListmapsFrag+"_FRAG"+`meters`+"m_mata", ListmapsFrag+"_FRAG"+`meters`+"m_mata_lpo"] #, ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_pid"]
      for txt in txts:
        grass.run_command('g.remove', type="raster", name=txt, flags='f')
    x=x+1     

def areaFrag(ListmapsFrag, prefix,list_esc_areaFrag,dirout,prepareBIODIM,calcStatistics,removeTrash,list_meco,check_func_edge):
  """
  Function for a series of maps
  This function fragments patches (FRAG), excluding corridors and edges given input scales (distances), and:
  - generates and exports maps with Patch ID and Area of each "fragmented" patch
  - generatics statistics - Area per patch (if calcStatistics == True)
  """

  if prepareBIODIM:
    esc, met = escala_frag(ListmapsFrag[0], list_esc_areaFrag)
    lista_maps_pid = np.empty((len(ListmapsFrag), len(esc)), dtype=np.dtype('a200'))
    lista_maps_area = np.empty((len(ListmapsFrag), len(esc)), dtype=np.dtype('a200'))
  
  z = 0
  cont = 1
  list_ssbc_maps=[]
  for i_in in ListmapsFrag:
    
    if prefix == '':
      pre_numb = ''
    else:
      if cont <= 9:
        pre_numb = "000"+`cont`+'_'
      elif cont <= 99:
        pre_numb = "00"+`cont`+'_'
      elif cont <= 999:        
        pre_numb = "0"+`cont`+'_'
      else: 
        pre_numb = `cont`+'_'
      
    i = prefix+pre_numb+i_in
          
    grass.run_command('g.region', rast=i_in)
    Lista_escalafragM, listmeters = escala_frag(i_in, list_esc_areaFrag)
    #print escalafragM
    x=0
    lista_maps_CSSB=[]
    #lista_maps_area=[]
    for a in Lista_escalafragM:
      meters=int(listmeters[x])  
      format_escale_name='0000'+`meters`
      format_escale_name=format_escale_name[-4:]
      grass.run_command('r.neighbors', input=i_in, output=i+"_ero_"+format_escale_name+'m', method='minimum', size=a, overwrite = True)
      grass.run_command('r.neighbors', input=i+"_ero_"+format_escale_name+'m', output=i+"_dila_"+format_escale_name+'m', method='maximum', size=a, overwrite = True)
      expression1=i+"_FRAG"+format_escale_name+"m_mata = if("+i+"_dila_"+format_escale_name+'m'+" > 0, "+i+"_dila_"+format_escale_name+'m'+", null())"
      grass.mapcalc(expression1, overwrite = True, quiet = True)
      expression2=i+"_FRAG"+format_escale_name+"m_mata_lpo = if("+i_in+" >= 0, "+i+"_FRAG"+format_escale_name+"m_mata, null())"
      grass.mapcalc(expression2, overwrite = True, quiet = True)
      grass.run_command('r.clump', input=i+"_FRAG"+format_escale_name+"m_mata_lpo", output=i+"_FRAG"+format_escale_name+"m_mata_clump_pid", overwrite = True)
      
      grass.run_command('g.region', rast=i+"_FRAG"+format_escale_name+"m_mata_clump_pid")
      nametxtreclass=rulesreclass(i+"_FRAG"+format_escale_name+"m_mata_clump_pid", dirout)
      grass.run_command('r.reclass', input=i+"_FRAG"+format_escale_name+"m_mata_clump_pid", output=i+"_FRAG"+format_escale_name+"m_mata_clump_AreaHA", rules=nametxtreclass, overwrite = True)   
      os.remove(nametxtreclass)
      
      # identificando branch tampulins e corredores
      
      
      expression3='temp_BSSC=if(isnull('+i+"_FRAG"+format_escale_name+"m_mata_clump_AreaHA"+'),'+i_in+')'
      grass.mapcalc(expression3, overwrite = True, quiet = True)    
      
      expression1="MapaBinario=temp_BSSC"
      grass.mapcalc(expression1, overwrite = True, quiet = True)    
      grass.run_command('g.region',rast="MapaBinario")
      expression2="A=MapaBinario"
      grass.mapcalc(expression2, overwrite = True, quiet = True)
      grass.run_command('g.region',rast="MapaBinario")
      expression3="MapaBinario_A=if(A[0,0]==0 && A[0,-1]==1 && A[1,-1]==0 && A[1,0]==1,1,A)"
      grass.mapcalc(expression3, overwrite = True, quiet = True)
      expression4="A=MapaBinario_A"
      grass.mapcalc(expression4, overwrite = True, quiet = True)
      expression5="MapaBinario_AB=if(A[0,0]==0 && A[-1,0]==1 && A[-1,1]==0 && A[0,1]==1,1,A)"
      grass.mapcalc(expression5, overwrite = True, quiet = True) 
      expression6="A=MapaBinario_AB"
      grass.mapcalc(expression6, overwrite = True, quiet = True)
      expression7="MapaBinario_ABC=if(A[0,0]==0 && A[0,1]==1 && A[1,1]==0 && A[1,0]==1,1,A)"
      grass.mapcalc(expression7, overwrite = True, quiet = True)
      expression8="A=MapaBinario_ABC"
      grass.mapcalc(expression8, overwrite = True, quiet = True)
      expression9="MapaBinario_ABCD=if(A[0,0]==0 && A[1,0]==1 && A[1,1]==0 && A[0,1]==1,1,A)"
      grass.mapcalc(expression9, overwrite = True, quiet = True)
      
      expression4='MapaBinario_ABCD1=if(MapaBinario_ABCD==0,null(),1)'
      grass.mapcalc(expression4, overwrite = True, quiet = True)    
      grass.run_command('r.clump', input='MapaBinario_ABCD1', output="MapaBinario_ABCD1_pid", overwrite = True)
      
      grass.run_command('r.neighbors', input='MapaBinario_ABCD1_pid', output='MapaBinario_ABCD1_pid_mode', method='mode', size=3, overwrite = True)
      grass.run_command('r.cross', input=i+"_FRAG"+format_escale_name+'m_mata_clump_pid,MapaBinario_ABCD1_pid_mode',out=i+"_FRAG"+format_escale_name+'m_mata_clump_pid_cross_corredor',overwrite = True)
      cross_TB = grass.read_command('r.stats', input=i+"_FRAG"+format_escale_name+'m_mata_clump_pid_cross_corredor', flags='l')  # pegando a resolucao
      print cross_TB 
      txt=open("table_cross.txt",'w')
      txt.write(cross_TB)
      txt.close()
      
      reclass_frag_cor('MapaBinario_ABCD1_pid', dirout) 
      expression10='MapaBinario_ABCD1_pid_reclass_sttepings=if(isnull(MapaBinario_ABCD1_pid_reclass)&&temp_BSSC==1,3,MapaBinario_ABCD1_pid_reclass)'
      grass.mapcalc(expression10, overwrite = True, quiet = True)  
      
      outputmapSCB=i_in+'_SSCB_deph_'+format_escale_name
      expression11=outputmapSCB+'=if(temp_BSSC==1,MapaBinario_ABCD1_pid_reclass_sttepings,null())'
      grass.mapcalc(expression11, overwrite = True, quiet = True) 
      list_ssbc_maps.append(outputmapSCB)
      

      
      if prepareBIODIM:    
        #grass.run_command('r.out.gdal',input=i+"_FRAG"+`meters`+"m_mata_clump_pid",out=i+"_FRAG"+`meters`+"m_PID.tif")
        lista_maps_pid[z,x] = i+"_FRAG"+format_escale_name+"m_mata_clump_pid"
        lista_maps_area[z,x] = i+"_FRAG"+format_escale_name+"m_mata_clump_AreaHA"
        #lista_maps_pid.append(i+"_FRAG"+`meters`+"m_mata_clump_pid")
        #lista_maps_area.append(i+"_FRAG"+`meters`+"m_mata_clump_AreaHA")
      else:
        grass.run_command('g.region', rast=i+"_FRAG"+format_escale_name+"m_mata_clump_AreaHA")
        grass.run_command('r.out.gdal', input=i+"_FRAG"+format_escale_name+"m_mata_clump_AreaHA", out=i+"_FRAG"+format_escale_name+"m_AreaHA.tif", overwrite = True)        
      
      if calcStatistics:      
        createtxt(i+"_FRAG"+format_escale_name+"m_mata_clump_pid", dirout, i+"_FRAG"+format_escale_name+"m_AreaHA")      
      
      if removeTrash:
        if prepareBIODIM:
          txts = ['MapaBinario_ABCD1_pid','MapaBinario_ABCD1_pid_reclass','MapaBinario_ABCD1_pid_reclass_sttepings2',i+"_ero_"+format_escale_name+'m', i+"_dila_"+format_escale_name+'m', i+"_FRAG"+format_escale_name+"m_mata", i+"_FRAG"+format_escale_name+"m_mata_lpo",'temp_BSSC','MapaBinario','A','MapaBinario_A','MapaBinario_AB','MapaBinario_ABC','MapaBinario_ABCD','MapaBinario_ABCD1','MapaBinario_ABCD1_pid','MapaBinario_ABCD1_pid_mode',i+"_FRAG"+`meters`+'m_mata_clump_pid_cross_corredor','MapaBinario_ABCD1_pid_reclass_sttepings']
        else:        
          txts = ['MapaBinario_ABCD1_pid','MapaBinario_ABCD1_pid_reclass','MapaBinario_ABCD1_pid_reclass_sttepings2',i+"_ero_"+format_escale_name+'m', i+"_dila_"+format_escale_name+'m', i+"_FRAG"+format_escale_name+"m_mata", i+"_FRAG"+format_escale_name+"m_mata_lpo",'temp_BSSC','MapaBinario','A','MapaBinario_A','MapaBinario_AB','MapaBinario_ABC','MapaBinario_ABCD','MapaBinario_ABCD1','MapaBinario_ABCD1_pid','MapaBinario_ABCD1_pid_mode',i+"_FRAG"+`meters`+'m_mata_clump_pid_cross_corredor','MapaBinario_ABCD1_pid_reclass_sttepings']#, i+"_FRAG"+`meters`+"m_mata_clump_pid"]
        for txt in txts:
          grass.run_command('g.remove', type="raster", name=txt, flags='f')
      x=x+1
    z=z+1
    cont += 1
 
  if check_func_edge:
    cont=0
    for i in list_ssbc_maps:
      
      meters=int(listmeters[cont])  # lista de escalas em metros
      format_escale_name='0000'+`meters`
      format_escale_name=format_escale_name[-4:]   
      nameaux=i[0:len(ListmapsFrag)]
      outputname=nameaux+'_SSCCB_deph_'+format_escale_name
      inpmaps=i+','+list_meco[cont]
      
      
      grass.run_command('r.patch',input=inpmaps,out=outputname,overwrite = True)
      cont+=1
      
  
  
  
  if prepareBIODIM:
    for i in range(len(met)):
      mm = int(met[i])
      create_TXTinputBIODIM(lista_maps_pid[:,i].tolist(), "simulados_HABMAT_FRAC_"+`mm`+"m_PID", dirout)
      create_TXTinputBIODIM(lista_maps_area[:,i].tolist(), "simulados_HABMAT_FRAC_"+`mm`+"m_AREApix", dirout)              
      
      
#----------------------------------------------------------------------------------
# Metrics for patch size/area/ID (PATCH)

def patchSingle(Listmapspatch_in, prefix,dirout,prepareBIODIM,calcStatistics,removeTrash):
  """
  Function for a single map
  This function calculates area per patch in a map (PATCH), considering structural connectivity 
  (no fragmentation or dilatation):
  - generates and exports maps with Patch ID and Area of each patch
  - generatics statistics - Area per patch (if calcStatistics == True)
  """
  
  Listmapspatch = prefix+Listmapspatch_in
  
  grass.run_command('g.region', rast=Listmapspatch_in)
  grass.run_command('r.clump', input=Listmapspatch_in, output=Listmapspatch+"_patch_clump", overwrite = True)
  ########## essa proxima linha muda algo?? clump * mata/nao-mata  
  expression12=Listmapspatch+"_patch_clump_mata = "+Listmapspatch+"_patch_clump*"+Listmapspatch_in
  grass.mapcalc(expression12, overwrite = True, quiet = True)
  expression13=Listmapspatch+"_patch_clump_mata_limpa_pid = if("+Listmapspatch+"_patch_clump_mata > 0, "+Listmapspatch+"_patch_clump_mata, null())"
  grass.mapcalc(expression13, overwrite = True, quiet = True)
  
  nametxtreclass=rulesreclass(Listmapspatch+"_patch_clump_mata_limpa_pid", dirout)
  grass.run_command('r.reclass', input=Listmapspatch+"_patch_clump_mata_limpa_pid", output=Listmapspatch+"_patch_clump_mata_limpa_AreaHA", rules=nametxtreclass, overwrite = True)
  os.remove(nametxtreclass)
  
  if prepareBIODIM:
    #grass.run_command('r.out.gdal',input=Listmapspatch+"_patch_clump_mata_limpa",out=Listmapspatch+"_patch_PID.tif")
    create_TXTinputBIODIM([Listmapspatch+"_patch_clump_mata_limpa_pid"], "simulados_HABMAT_grassclump_PID", dirout)
    create_TXTinputBIODIM([Listmapspatch+"_patch_clump_mata_limpa_AreaHA"], "simulados_HABMAT_grassclump_AREApix", dirout)    
  else:
    grass.run_command('g.region', rast=Listmapspatch+"_patch_clump_mata_limpa_AreaHA")
    grass.run_command('r.out.gdal', input=Listmapspatch+"_patch_clump_mata_limpa_AreaHA", out=Listmapspatch+"_patch_AreaHA.tif",overwrite = True)
  
  if calcStatistics:
    createtxt(Listmapspatch+"_patch_clump_mata_limpa_pid", dirout, Listmapspatch+"_patch_AreaHA")
  
  if removeTrash:
    if prepareBIODIM:
      txts = [Listmapspatch+"_patch_clump", Listmapspatch+"_patch_clump_mata"]
    else:
      txts = [Listmapspatch+"_patch_clump", Listmapspatch+"_patch_clump_mata"] #, Listmapspatch+"_patch_clump_mata_limpa_pid"]
    for txt in txts:
      grass.run_command('g.remove', type="raster", name=txt, flags='f')
  
def Patch(Listmapspatch_in, prefix,dirout,prepareBIODIM,calcStatistics,removeTrash):
  """
  Function for a series of maps
  This function calculates area per patch in a map (PATCH), considering structural connectivity 
  (no fragmentation or dilatation):
  - generates and exports maps with Patch ID and Area of each patch
  - generatics statistics - Area per patch (if calcStatistics == True)
  """
  
  if prepareBIODIM:
    lista_maps_pid=[]
    lista_maps_area=[]  

  cont = 1
  # isso eh assim mesmo ?????????????????????
  
  
  for i_in in Listmapspatch_in:
    
    if prefix == '':
      pre_numb = ''
    else:
      if cont <= 9:
        pre_numb = "000"+`cont`+'_'
      elif cont <= 99:
        pre_numb = "00"+`cont`+'_'
      elif cont <= 999:        
        pre_numb = "0"+`cont`+'_'
      else: 
        pre_numb = `cont`+'_'
      
    i = prefix+pre_numb+i_in

    grass.run_command('g.region', rast=i_in)
    grass.run_command('r.clump', input=i_in, output=i+"_patch_clump", overwrite = True)
    expression12=i+"_patch_clump_mata = "+i+"_patch_clump*"+i_in
    grass.mapcalc(expression12, overwrite = True, quiet = True)
    expression13=i+"_patch_clump_mata_limpa_pid = if("+i+"_patch_clump_mata > 0, "+i+"_patch_clump_mata, null())"
    grass.mapcalc(expression13, overwrite = True, quiet = True)
    
    nametxtreclass=rulesreclass(i+"_patch_clump_mata_limpa_pid", dirout)
    grass.run_command('r.reclass', input=i+"_patch_clump_mata_limpa_pid", output=i+"_patch_clump_mata_limpa_AreaHA", rules=nametxtreclass, overwrite = True)
    os.remove(nametxtreclass)
    
    if prepareBIODIM:
      #grass.run_command('r.out.gdal',input=i+"_patch_clump_mata_limpa_pid",out=i+"_patch_PID.tif")
      lista_maps_pid.append(i+"_patch_clump_mata_limpa_pid")
      lista_maps_area.append(i+"_patch_clump_mata_limpa_AreaHA")      
    else:
      grass.run_command('g.region', rast=i+"_patch_clump_mata_limpa_AreaHA")
      grass.run_command('r.out.gdal', input=i+"_patch_clump_mata_limpa_AreaHA", out=i+"_patch_AreaHA.tif",overwrite = True)
          
    if calcStatistics:
      createtxt(i+"_patch_clump_mata_limpa_pid", dirout, i+"_patch_AreaHA")
    
    if removeTrash:
      if prepareBIODIM:
        txts = [i+"_patch_clump", i+"_patch_clump_mata"]
      else:
        txts = [i+"_patch_clump", i+"_patch_clump_mata"]#, i+"_patch_clump_mata_limpa_pid"]
      for txt in txts:
        grass.run_command('g.remove', type="raster", name=txt, flags='f')
        
    cont += 1
        
    
  if prepareBIODIM:
    create_TXTinputBIODIM(lista_maps_pid, "simulados_HABMAT_grassclump_PID", dirout)
    create_TXTinputBIODIM(lista_maps_area, "simulados_HABMAT_grassclump_AREApix", dirout)  
  
  return Listmapspatch_in

#----------------------------------------------------------------------------------
# Metrics for functional connectivity area/ID (CON)

def areaconSingle(mapHABITAT_Single, prefix,escala_frag_con,dirout,prepareBIODIM,calcStatistics,removeTrash):
  os.chdir(dirout)
  """
  Function for a single map
  This function calculates functional patch area in a map (CON), considering functional connectivity 
  (dilatation of edges given input scales/distances), and:
  - generates and exports maps with Patch ID and Area of each patch
  - generatics statistics - Area per patch (if calcStatistics == True)
  """
  
  Listmapspatch = prefix+mapHABITAT_Single

  grass.run_command('g.region', rast=mapHABITAT_Single)
  listescalafconM, listmeters = escala_con(mapHABITAT_Single, escala_frag_con)
  
  x=0
  for a in listescalafconM:
    meters = int(listmeters[x])
    grass.run_command('r.neighbors', input=mapHABITAT_Single, output=Listmapspatch+"_dila_"+`meters`+'m_orig', method='maximum', size=a, overwrite = True)
    expression=Listmapspatch+"_dila_"+`meters`+'m_orig_temp = if('+Listmapspatch+"_dila_"+`meters`+'m_orig == 0, null(), '+Listmapspatch+"_dila_"+`meters`+'m_orig)'
    grass.mapcalc(expression, overwrite = True, quiet = True)
    grass.run_command('r.clump', input=Listmapspatch+"_dila_"+`meters`+'m_orig_temp', output=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_pid', overwrite = True)
    espressao1=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata = '+mapHABITAT_Single+'*'+Listmapspatch+"_dila_"+`meters`+'m_orig_clump_pid'
    grass.mapcalc(espressao1, overwrite = True, quiet = True)
    espressao2=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_pid = if('+Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata > 0, '+Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata, null())'
    grass.mapcalc(espressao2, overwrite = True, quiet = True)
    
    nametxtreclass=rulesreclass(Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_pid', dirout)
    grass.run_command('r.reclass', input=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_pid', output=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_AreaHA', rules=nametxtreclass, overwrite = True)
    os.remove(nametxtreclass)
    
    if prepareBIODIM:
      #grass.run_command('r.out.gdal',input=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_pid',out=Listmapspatch+"_dila_"+`meters`+'m_clean_PID.tif')
      create_TXTinputBIODIM([Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_pid'], "simulados_HABMAT_grassclump_dila_"+`meters`+"m_clean_PID", dirout)
      create_TXTinputBIODIM([Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_AreaHA'], "simulados_HABMAT_grassclump_dila_"+`meters`+"m_clean_AREApix",dirout)      
      
      ########### calculando o area complete, exportanto ele e tb PID complete - precisa tambem gerar um area complete mesmo?
      nametxtreclass=rulesreclass(Listmapspatch+"_dila_"+`meters`+'m_orig_clump_pid',dirout)
      grass.run_command('r.reclass', input=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_pid', output=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_complete_AreaHA', rules=nametxtreclass, overwrite = True)
      os.remove(nametxtreclass)
      #grass.run_command('r.out.gdal', input=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_complete_AreaHA', out=Listmapspatch+"_dila_"+`meters`+'m_complete_AreaHA.tif')  
      #grass.run_command('r.out.gdal', input=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_pid', out=Listmapspatch+"_dila_"+`meters`+'m_complete_PID.tif')
      create_TXTinputBIODIM([Listmapspatch+"_dila_"+`meters`+'m_orig_clump_pid'], "simulados_HABMAT_grassclump_dila_"+`meters`+"m_complete_PID", dirout)
      create_TXTinputBIODIM([Listmapspatch+"_dila_"+`meters`+'m_orig_clump_complete_AreaHA'], "simulados_HABMAT_grassclump_dila_"+`meters`+"m_complete_AREApix", dirout)      
    else:
      grass.run_command('g.region', rast=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_AreaHA')
      grass.run_command('r.out.gdal', input=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_AreaHA', out=Listmapspatch+"_dila_"+`meters`+'m_clean_AreaHA.tif',overwrite = True)     
    
    if calcStatistics:
      createtxt(Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_pid', dirout, Listmapspatch+"_dila_"+`meters`+"m_clean_AreaHA") # clean
      createtxt(Listmapspatch+"_dila_"+`meters`+'m_orig_clump_pid', dirout, Listmapspatch+"_dila_"+`meters`+"m_complete_AreaHA") # complete
      
    if removeTrash:
      if prepareBIODIM:
        txts = [Listmapspatch+"_dila_"+`meters`+'m_orig', Listmapspatch+"_dila_"+`meters`+'m_orig_temp', Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata']
      else:
        txts = [Listmapspatch+"_dila_"+`meters`+'m_orig', Listmapspatch+"_dila_"+`meters`+'m_orig_temp', Listmapspatch+"_dila_"+`meters`+'m_orig_clump_pid', Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata']
      for txt in txts:
        grass.run_command('g.remove', type="raster", name=txt, flags='f')
           
    x=x+1

def areacon(Listmapspatch, prefix,escala_frag_con,dirout,prepareBIODIM,calcStatistics,removeTrash):
  """
  Function for a series of maps
  This function calculates functional patch area in a map (CON), considering functional connectivity 
  (dilatation of edges given input scales/distances), and:
  - generates and exports maps with Patch ID and Area of each patch
  - generatics statistics - Area per patch (if calcStatistics == True)
  """
  
  if prepareBIODIM:
    esc, met = escala_con(Listmapspatch[0], escala_frag_con)
    # maps clean
    lista_maps_pid_clean = np.empty((len(Listmapspatch), len(esc)), dtype=np.dtype('a200'))
    lista_maps_area_clean = np.empty((len(Listmapspatch), len(esc)), dtype=np.dtype('a200'))
    # maps complete
    lista_maps_pid_comp = np.empty((len(Listmapspatch), len(esc)), dtype=np.dtype('a200'))
    lista_maps_area_comp = np.empty((len(Listmapspatch), len(esc)), dtype=np.dtype('a200'))        
  
  z = 0
  cont = 1
  for i_in in Listmapspatch:
    
    if prefix == '':
      pre_numb = ''
    else:
      if cont <= 9:
        pre_numb = "000"+`cont`+'_'
      elif cont <= 99:
        pre_numb = "00"+`cont`+'_'
      elif cont <= 999:        
        pre_numb = "0"+`cont`+'_'
      else: 
        pre_numb = `cont`+'_'
      
    i = prefix+pre_numb+i_in
    
    grass.run_command('g.region', rast=i_in)
    listescalafconM, listmeters = escala_con(i_in, escala_frag_con)
    
    x = 0
    for a in listescalafconM:
      meters = int(listmeters[x])    
      grass.run_command('r.neighbors', input=i_in, output=i+"_dila_"+`meters`+'m_orig', method='maximum', size=a, overwrite = True)
      expression=i+"_dila_"+`meters`+'m_orig_temp = if('+i+"_dila_"+`meters`+'m_orig == 0, null(), '+i+"_dila_"+`meters`+'m_orig)'
      grass.mapcalc(expression, overwrite = True, quiet = True)      
      grass.run_command('r.clump', input=i+"_dila_"+`meters`+'m_orig_temp', output=i+"_dila_"+`meters`+'m_orig_clump_pid', overwrite = True)
      espressao1=i+"_dila_"+`meters`+'m_orig_clump_mata = '+i_in+'*'+i+"_dila_"+`meters`+'m_orig_clump_pid'
      grass.mapcalc(espressao1, overwrite = True, quiet = True)
      espressao2=i+"_dila_"+`meters`+'m_orig_clump_mata_limpa_pid = if('+i+"_dila_"+`meters`+'m_orig_clump_mata > 0, '+i+"_dila_"+`meters`+'m_orig_clump_mata, null())'
      grass.mapcalc(espressao2, overwrite = True, quiet = True)
      nametxtreclass=rulesreclass(i+"_dila_"+`meters`+'m_orig_clump_mata_limpa_pid', dirout)
      grass.run_command('r.reclass', input=i+"_dila_"+`meters`+'m_orig_clump_mata_limpa_pid', output=i+"_dila_"+`meters`+'m_orig_clump_mata_limpa_AreaHA', rules=nametxtreclass, overwrite = True)
      os.remove(nametxtreclass)
      
      ############### no biodim eh HABMAT_grassclump_dila01_clean_AREApix.tif (ou complete, abaixo)
      ########## exportando o PID clean
      if prepareBIODIM:
        #grass.run_command('r.out.gdal', input=i+"_dila_"+`meters`+'m_orig_clump_mata_limpa_pid', out=i+"_dila_"+`meters`+'m_clean_PID.tif')
        lista_maps_pid_clean[z,x] = i+"_dila_"+`meters`+'m_orig_clump_mata_limpa_pid'
        lista_maps_area_clean[z,x] = i+"_dila_"+`meters`+'m_orig_clump_mata_limpa_AreaHA'        
        
        ########### calculando o area complete, exportanto ele e tb PID complete - precisa tambem gerar um area complete mesmo?
        nametxtreclass=rulesreclass(i+"_dila_"+`meters`+'m_orig_clump_pid', dirout)
        grass.run_command('r.reclass', input=i+"_dila_"+`meters`+'m_orig_clump_pid', output=i+"_dila_"+`meters`+'m_orig_clump_complete_AreaHA', rules=nametxtreclass, overwrite = True)
        os.remove(nametxtreclass)  
        #grass.run_command('r.out.gdal', input=i+"_dila_"+`meters`+'m_orig_clump_complete_AreaHA', out=i+"_dila_"+`meters`+'m_complete_AreaHA.tif')            
        #grass.run_command('r.out.gdal', input=i+"_dila_"+`meters`+'m_orig_clump_pid', out=i+"_dila_"+`meters`+'m_complete_PID.tif')
        lista_maps_pid_comp[z,x] = i+"_dila_"+`meters`+'m_orig_clump_pid'
        lista_maps_area_comp[z,x] = i+"_dila_"+`meters`+'m_orig_clump_complete_AreaHA'
  
      else:
        grass.run_command('g.region', rast=i+"_dila_"+`meters`+'m_orig_clump_mata_limpa_AreaHA')
        grass.run_command('r.out.gdal', input=i+"_dila_"+`meters`+'m_orig_clump_mata_limpa_AreaHA', out=i+"_dila_"+`meters`+'m_clean_AreaHA.tif',overwrite = True)
            
      if calcStatistics:
        createtxt(i+"_dila_"+`meters`+'m_orig_clump_mata_limpa_pid', dirout, i+"_dila_"+`meters`+"m_clean_AreaHA")
        createtxt(i+"_dila_"+`meters`+'m_orig_clump_pid', dirout, i+"_dila_"+`meters`+"m_complete_AreaHA")
      
      if removeTrash:
        if prepareBIODIM:
          txts = [i+"_dila_"+`meters`+'m_orig', i+"_dila_"+`meters`+'m_orig_temp', i+"_dila_"+`meters`+'m_orig_clump_mata']
        else:
          txts = [i+"_dila_"+`meters`+'m_orig', i+"_dila_"+`meters`+'m_orig_temp', i+"_dila_"+`meters`+'m_orig_clump_pid', i+"_dila_"+`meters`+'m_orig_clump_mata'] #, i+"_dila_"+`meters`+'m_orig_clump_mata_limpa_pid']
        for txt in txts:
          grass.run_command('g.remove', type='raster', name=txt, flags='f')
          
      x=x+1
    z=z+1
    cont += 1
    
  if prepareBIODIM:
    for i in range(len(met)):
      mm = int(met[i])
      create_TXTinputBIODIM(lista_maps_pid_clean[:,i].tolist(), "simulados_HABMAT_grassclump_dila_"+`mm`+"m_clean_PID", dirout)
      create_TXTinputBIODIM(lista_maps_area_clean[:,i].tolist(), "simulados_HABMAT_grassclump_dila_"+`mm`+"m_clean_AREApix", dirout)   

      create_TXTinputBIODIM(lista_maps_pid_comp[:,i].tolist(), "simulados_HABMAT_grassclump_dila_"+`mm`+"m_complete_PID", dirout)
      create_TXTinputBIODIM(lista_maps_area_comp[:,i].tolist(), "simulados_HABMAT_grassclump_dila_"+`mm`+"m_complete_AREApix", dirout)  
      
      
#----------------------------------------------------------------------------------
# Metrics for edge area (EDGE)

def mapcalcED(expression):
  """
  
  """
  grass.mapcalc(expression, overwrite = True, quiet = True)        

def create_EDGE_single(ListmapsED_in, escale_ed, dirs, prefix,calcStatistics,removeTrash,escale_pct):
  """
  Function for a single map
  This function separates habitat area into edge and interior/core regions, given a scale/distance defined as edge, and:
  - generates and exports maps with each region
  - generatics statistics - Area per region (matrix/edge/core) (if calcStatistics == True)
  """  
  os.chdir(dirs)
  ListmapsED = prefix+ListmapsED_in
  
  grass.run_command('g.region', rast=ListmapsED_in)
  listsize, listmeters = escala_frag(ListmapsED_in, escale_ed)
  
  cont_escale=0
  for i in listsize:
    apoioname = int(listmeters[cont_escale])  
    formatnumber='0000'+`apoioname`
    formatnumber=formatnumber[-4:]
    outputname_meco=ListmapsED+'_MECO_'+formatnumber+'m' # nome de saida do mapa edge-core-matriz
    outputname_core=ListmapsED+'_CORE_'+formatnumber+'m' # nome de saida do mapa Core
    outputname_edge=ListmapsED+'_EDGE_'+formatnumber+'m' # nome de saida do mapa edge
    
    
    grass.run_command('r.neighbors', input=ListmapsED_in, output=ListmapsED+"_eroED_"+`apoioname`+'m', method='minimum', size=i, overwrite = True)
    inputs=ListmapsED+"_eroED_"+`apoioname`+'m,'+ListmapsED_in
    out=ListmapsED+'_EDGE'+`apoioname`+'m_temp1'
    grass.run_command('r.series', input=inputs, out=out, method='sum', overwrite = True)
    espressaoEd=ListmapsED+'_EDGE'+`apoioname`+'m_temp2 = int('+ListmapsED+'_EDGE'+`apoioname`+'m_temp1)' # criando uma mapa inteiro
    mapcalcED(espressaoEd)
    
    espressaoclip=outputname_meco+'= if('+ListmapsED_in+' >= 0, '+ListmapsED+'_EDGE'+`apoioname`+'m_temp2, null())'
    mapcalcED(espressaoclip)  
    
    espressaocore=outputname_core+'= if('+outputname_meco+'==2,1,0)'
    grass.mapcalc(espressaocore, overwrite = True, quiet = True)     
    
    espressaoedge=outputname_edge+'= if('+outputname_meco+'==1,1,0)'
    grass.mapcalc(espressaoedge, overwrite = True, quiet = True)  
    
    
     
    grass.run_command('r.out.gdal', input=outputname_meco, out=outputname_meco+'.tif', overwrite = True) 
    grass.run_command('r.out.gdal', input=outputname_edge, out=outputname_edge+'.tif', overwrite = True)
    grass.run_command('r.out.gdal', input=outputname_core, out=outputname_core+'.tif', overwrite = True)
    print '>>>>>>>>>>>>>>>>>>>>',escale_pct
    if len(escale_pct)>0:
      for pct in escale_pct:
        pctint=int(pct)

        formatnumber='0000'+`pctint`
        formatnumber=formatnumber[-4:]        
        outputname_edge_pct=outputname_edge+'_PCT_esc_'+formatnumber
        
        size=getsizepx(outputname_edge, pctint)
        grass.run_command('r.neighbors', input=outputname_edge, output="temp_pct", method='average', size=size, overwrite = True)
        espressaoedge=outputname_edge_pct+'=temp_pct*100'
        grass.mapcalc(espressaoedge, overwrite = True, quiet = True)    
        grass.run_command('r.out.gdal', input=outputname_edge_pct, out=outputname_edge_pct+'.tif', overwrite = True)
        grass.run_command('g.remove', type="raster", name='temp_pct', flags='f')
        
        
        
        
        
    if calcStatistics:
      createtxt(ListmapsED+'_EDGE'+`apoioname`+'m', dirs, out)
      
      
    if removeTrash:
      grass.run_command('g.remove', type="raster", name=ListmapsED+"_eroED_"+`apoioname`+'m,'+ListmapsED+'_EDGE'+`apoioname`+'m_temp1,'+ListmapsED+'_EDGE'+`apoioname`+'m_temp2', flags='f')
    
    cont_escale=cont_escale+1
    
    
def create_EDGE(ListmapsED, escale_ed, dirs, prefix,calcStatistics,removeTrash,escale_pct,checkCalc_PCTedge):
  os.chdir(dirs)
  """
  Function for a series of maps
  This function separates habitat area into edge and interior/core regions, given a scale/distance defined as edge, and:
  - generates and exports maps with each region
  - generatics statistics - Area per region (matrix/edge/core) (if calcStatistics == True)
  """
  
  cont = 1
  list_meco=[] # essa lista sera usada na funcao area frag

  for i_in in ListmapsED:
    
    if prefix == '':
      pre_numb = ''
    else:
      if cont <= 9:
        pre_numb = "000"+`cont`+'_'
      elif cont <= 99:
        pre_numb = "00"+`cont`+'_'
      elif cont <= 999:        
        pre_numb = "0"+`cont`+'_'
      else: 
        pre_numb = `cont`+'_'
    
    i = prefix+pre_numb+i_in
    
    grass.run_command('g.region', rast=i_in)
    listsize, listmeters = escala_frag(i_in, escale_ed)
    
    cont_escale=0
    for size in listsize:
      apoioname = int(listmeters[cont_escale])  
      formatnumber='0000'+`apoioname`
      formatnumber=formatnumber[-4:]
      outputname_meco=i+'_MECO_'+formatnumber+'m' # nome de saida do mapa edge-core-matriz
      outputname_core=i+'_CORE_'+formatnumber+'m' # nome de saida do mapa Core
      outputname_edge=i+'_EDGE_'+formatnumber+'m' # nome de saida do mapa edge
      list_meco.append(outputname_meco)
      
      grass.run_command('r.neighbors', input=i_in, output=i+"_eroED_"+`apoioname`+'m', method='minimum', size=size, overwrite = True)
      inputs=i+"_eroED_"+`apoioname`+'m,'+i_in
      out=i+'_EDGE'+`apoioname`+'m_temp1'
      grass.run_command('r.series', input=inputs, out=out, method='sum', overwrite = True)
      espressaoEd=i+'_EDGE'+`apoioname`+'m_temp2 = int('+i+'_EDGE'+`apoioname`+'m_temp1)' # criando uma mapa inteiro
      mapcalcED(espressaoEd)
           
      
      espressaoclip=i+'_EDGE'+`apoioname`+'m_temp3= if('+i_in+' >= 0, '+i+'_EDGE'+`apoioname`+'m_temp2, null())'
      mapcalcED(espressaoclip)  
      
      espressaoEd=outputname_meco+'=if('+i+'_EDGE'+`apoioname`+'m_temp3==0,0)|if('+i+'_EDGE'+`apoioname`+'m_temp3==1,4)|if('+i+'_EDGE'+`apoioname`+'m_temp3==2,5)'
      mapcalcED(espressaoEd)       
      
      espressaocore=outputname_core+'= if('+i+'_EDGE'+`apoioname`+'m_temp3==2,1,0)'
      grass.mapcalc(espressaocore, overwrite = True, quiet = True)     
      
      espressaoedge=outputname_edge+'= if('+i+'_EDGE'+`apoioname`+'m_temp3==1,1,0)'
      grass.mapcalc(espressaoedge, overwrite = True, quiet = True)  
      
      
       
      grass.run_command('r.out.gdal', input=outputname_meco, out=outputname_meco+'.tif', overwrite = True) 
      grass.run_command('r.out.gdal', input=outputname_edge, out=outputname_edge+'.tif', overwrite = True)
      grass.run_command('r.out.gdal', input=outputname_core, out=outputname_core+'.tif', overwrite = True)
      if len(escale_pct)>0 and checkCalc_PCTedge==True:
        for pct in escale_pct:
          pctint=int(pct)
      
          formatnumber='0000'+`pctint`
          formatnumber=formatnumber[-4:]        
          outputname_edge_pct=outputname_edge+'_PCT_esc_'+formatnumber
          
          size=getsizepx(outputname_edge, pctint)
          grass.run_command('r.neighbors', input=outputname_edge, output="temp_pct", method='average', size=size, overwrite = True)
          espressaoedge=outputname_edge_pct+'=temp_pct*100'
          grass.mapcalc(espressaoedge, overwrite = True, quiet = True)    
          grass.run_command('r.out.gdal', input=outputname_edge_pct, out=outputname_edge_pct+'.tif', overwrite = True)
          grass.run_command('g.remove', type="raster", name='temp_pct', flags='f')     
            
      if calcStatistics:
        createtxt(outputname_meco, i+'_EDGE'+`apoioname`+'m_temp1')
      
      if removeTrash:
        grass.run_command('g.remove', type="raster", name=i+"_eroED_"+`apoioname`+'m,'+i+'_EDGE'+`apoioname`+'m_temp1,'+i+'_EDGE'+`apoioname`+'m_temp2,'+i+'_EDGE'+`apoioname`+'m_temp3', flags="f")
      
      cont_escale +=1
      
    cont += 1
  print list_meco
  return list_meco


#


#----------------------------------------------------------------------------------
# Metrics for distance to edges
    
def dist_edge_Single(Listmapsdist_in, prefix,prepareBIODIM, dirout,removeTrash):
  """
  Function for a single map
  This function calculates the distance of each pixel to habitat edges, considering
  negative values (inside patches) and positive values (into the matrix). Also:
  - generates and exports maps of distance to edge (DIST)
  """

  Listmapsdist = prefix+Listmapsdist_in
  
  grass.run_command('g.region', rast=Listmapsdist_in)
  expression1=Listmapsdist+'_invert = if('+Listmapsdist_in+' == 0, 1, null())'
  grass.mapcalc(expression1, overwrite = True, quiet = True)
  grass.run_command('r.grow.distance', input=Listmapsdist+'_invert', distance=Listmapsdist+'_invert_forest_neg_eucldist',overwrite = True)
  expression2=Listmapsdist+'_invert_matrix = if('+Listmapsdist_in+' == 0, null(), 1)'
  grass.mapcalc(expression2, overwrite = True, quiet = True)
  grass.run_command('r.grow.distance', input=Listmapsdist+'_invert_matrix', distance=Listmapsdist+'_invert_matrix_pos_eucldist',overwrite = True)
  expression3=Listmapsdist+'_dist = '+Listmapsdist+'_invert_matrix_pos_eucldist-'+Listmapsdist+'_invert_forest_neg_eucldist'
  grass.mapcalc(expression3, overwrite = True, quiet = True)
  
  if prepareBIODIM:
    create_TXTinputBIODIM([Listmapsdist+'_dist'], "simulados_HABMAT_DIST", dirout)
  else:
    grass.run_command('r.out.gdal', input=Listmapsdist+'_dist', out=Listmapsdist+'_DIST.tif', overwrite = True)
    
  if removeTrash:
    txts = [Listmapsdist+'_invert', Listmapsdist+'_invert_forest_neg_eucldist', Listmapsdist+'_invert_matrix', Listmapsdist+'_invert_matrix_pos_eucldist']
    for txt in txts:
      grass.run_command('g.remove', type="raster", name=txt, flags='f')

def dist_edge(Listmapsdist_in, prefix,prepareBIODIM, dirout,removeTrash):
  """
  Function for a series of maps
  This function calculates the distance of each pixel to habitat edges, considering
  negative values (inside patches) and positive values (into the matrix). Also:
  - generates and exports maps of distance to edge (DIST)
  """

  if prepareBIODIM:
    lista_maps_dist=[]    
  
  cont = 1
  for i_in in Listmapsdist:
    
    if prefix == '':
      pre_numb = ''
    else:
      if cont <= 9:
        pre_numb = "000"+`cont`+'_'
      elif cont <= 99:
        pre_numb = "00"+`cont`+'_'
      elif cont <= 999:        
        pre_numb = "0"+`cont`+'_'
      else: 
        pre_numb = `cont`+'_'

    i = prefix+pre_numb+i_in

    grass.run_command('g.region', rast=i_in)
    expression1=i+'_invert = if('+i_in+' == 0, 1, null())'
    grass.mapcalc(expression1, overwrite = True, quiet = True)
    grass.run_command('r.grow.distance', input=i+'_invert', distance=i+'_invert_forest_neg_eucldist',overwrite = True)
    expression2=i+'_invert_matrix = if('+i_in+' == 0, null(), 1)'
    grass.mapcalc(expression2, overwrite = True, quiet = True)
    grass.run_command('r.grow.distance', input=i+'_invert_matrix', distance=i+'_invert_matrix_pos_eucldist',overwrite = True)
    expression3=i+'_dist = '+i+'_invert_matrix_pos_eucldist-'+i+'_invert_forest_neg_eucldist'
    grass.mapcalc(expression3, overwrite = True, quiet = True)
    
    if prepareBIODIM:
      lista_maps_dist.append(i+'_dist')
    else:
      grass.run_command('r.out.gdal', input=i+'_dist', out=i+'_DIST.tif', overwrite = True)
      
    if removeTrash:
      txts = [i+'_invert', i+'_invert_forest_neg_eucldist', i+'_invert_matrix', i+'_invert_matrix_pos_eucldist']
      for txt in txts:
        grass.run_command('g.remove', type="raster", name=txt, flags='f')
    
    cont += 1
    
  if prepareBIODIM:
    create_TXTinputBIODIM(lista_maps_dist, "simulados_HABMAT_DIST", dirout)
    
#----------------------------------------------------------------------------------
# funcao de pcts
def PCTs_single(mapbin_HABITAT,escales):
  for i in escales:
    esc=int(i)
    outputname=mapbin_HABITAT+"_PCT_esc_"+`esc`
    windowsize=getsizepx(mapbin_HABITAT, esc)
    grass.run_command('g.region', rast=mapbin_HABITAT)
    grass.run_command('r.neighbors',input=mapbin_HABITAT,out="temp_PCT",method='average',size=windowsize,overwrite = True )
    expression1=outputname+'=temp_PCT*100'
    grass.mapcalc(expression1, overwrite = True, quiet = True)    
    grass.run_command('r.out.gdal', input=outputname, out=outputname+'.tif', overwrite = True)
    grass.run_command('g.remove', type="raster", name='temp_PCT', flags='f')
    
def PCTs(Listmap_HABITAT,escales):
  for i in escales:
    esc=int(i)
    for mapHABT in Listmap_HABITAT:
      outputname=mapHABT+"_PCT_esc_"+`esc`
      windowsize=getsizepx(mapHABT, esc)
      grass.run_command('g.region', rast=mapHABT)
      grass.run_command('r.neighbors',input=mapHABT,out="temp_PCT",method='average',size=windowsize,overwrite = True )
      expression1=outputname+'=temp_PCT*100'
      grass.mapcalc(expression1, overwrite = True, quiet = True)    
      grass.run_command('r.out.gdal', input=outputname, out=outputname+'.tif', overwrite = True)
      grass.run_command('g.remove', type="raster", name='temp_PCT', flags='f')
    

#----------------------------------------------------------------------------------
#def para diversidade de shannon

def createUiqueList(tab_fid00_arry_subset_list,dim):
    tab_fid00_arry_subset_list_apoio=[]
    for i in xrange(dim):
        temp1=tab_fid00_arry_subset_list[i][:]
        for j in temp1:
            if j != -9999 :
                tab_fid00_arry_subset_list_apoio.append(j)
    return tab_fid00_arry_subset_list_apoio
      
      


def Shannon(st):
    st = st
    stList = list(st)
    alphabet = list(Set(st)) # list of symbols in the string
    
    # calculate the frequency of each symbol in the string
    freqList = []
    for symbol in alphabet:
        ctr = 0
        for sym in stList:
            if sym == symbol:
                ctr += 1
        freqList.append(float(ctr) / len(stList))
    
    # Shannon entropy
    ent = 0.0
    for freq in freqList:
        ent = ent + freq * math.log(freq, 2)
    ent = -ent
    
    #print int(math.ceil(ent))
    return ent


    
def removeBlancsapce(ls):
    ls2=[]
    for i in ls:
        if i != "":
            ls2.append(i)
            
    return ls2

def setNodata(arry,nrow,ncol,nodata):
    for i in xrange(nrow):
        for j in xrange(ncol):
            arry[i][j]=nodata
    return arry

#----------------------------------------------------------------------------------
def shannon_diversity(landuse_map,dirout,Raio_Analise):
  for raio in Raio_Analise:
    raio_int=int(raio)
    os.chdir(dirout) #
    grass.run_command('g.region',rast=landuse_map)
    grass.run_command('r.out.ascii',input=landuse_map,output='landuse_map.asc',null_value=-9999,flags='h')
    landusemap_arry=np.loadtxt('landuse_map.asc')
    NRows,Ncols=landusemap_arry.shape
    region_info = grass.parse_command('g.region', rast=landuse_map, flags='m')  # pegando a resolucao    
    cell_size = float(region_info['ewres'])    
    north=float(region_info['n'])
    south=float(region_info['s'])
    east=float(region_info['e'])
    west=float(region_info['w'])
    rows=int(region_info['rows'])
    cols=int(region_info['cols'])
    
    Nodata=-9999
    
    JanelaLinha=(raio_int/cell_size)
    
    new_array = np.zeros(shape=(NRows,Ncols))
    new_array=setNodata(new_array,NRows,Ncols,Nodata)  
    
    JanelaLinha= int(JanelaLinha)
    #
    for i in xrange(JanelaLinha,NRows-JanelaLinha):
      for j in xrange(JanelaLinha,Ncols-JanelaLinha):
        landusemap_arry_subset=landusemap_arry[i-JanelaLinha:i+JanelaLinha,j-JanelaLinha:j+JanelaLinha]    
        landusemap_arry_subset_list=landusemap_arry_subset.tolist()
        landusemap_arry_subset_list=createUiqueList(landusemap_arry_subset_list,len(landusemap_arry_subset_list))
        landusemap_arry_subset_list=map(str,landusemap_arry_subset_list)
        new_array[i][j]=round(Shannon(landusemap_arry_subset_list),6)   

    txt=open("landuse_map_shannon.asc",'w')
    
    L_parameters_Info_asc=['north: ',`north`+'\nsouth: ',`south`+'\neast: ',`east`+'\nwest: ',`west`+'\nrows: ',`rows`+'\ncols: '+`cols`+'\n']
    
    check_ultm=1 # variavel que vai saber se e o ultimo
    for i in L_parameters_Info_asc:
        if check_ultm==len(L_parameters_Info_asc):
            txt.write(i)    
        else:
            txt.write(i+' ')  
        check_ultm=check_ultm+1 
        
    for i in range(NRows):
        for j in range(Ncols):
            txt.write(str(new_array[i][j])+' ')
        
        txt.write('\n')
    
    txt.close()  
    grass.run_command('r.in.ascii',input="landuse_map_shannon.asc",output=landuse_map+"_Shanno_Div_Esc_"+`raio_int`,overwrite=True,null_value=-9999)
    grass.run_command('r.colors',map=landuse_map+"_Shanno_Div_Esc_"+`raio_int`,color='differences')
    os.remove('landuse_map_shannon.asc')
    os.remove('landuse_map.asc')
    
#----------------------------------------------------------------------------------
def percentage_edge():
  pass
  












#----------------------------------------------------------------------------------
# LSMetrics is the main class, in which the software is initialized and runs

class LSMetrics(wx.Panel):
    def __init__(self, parent, id):
        # Initializing GUI
        wx.Panel.__init__(self, parent, id)
        
        # Takes the current mapset and looks for maps only inside it
        self.current_mapset = grass.read_command('g.mapset', flags = 'p').replace('\n','').replace('\r','')        
        
        # Parameters
        
        # Maps to be processed
        self.input_map = ''
        self.background_filename = []
        
        # Metrics to be calculated
        self.Patch = False # Option: Patch area maps
        self.Frag = False # Option: Core area maps (degrading patch edges)
        self.Con = False # Option: Functional connectivity maps
        self.Dist = False # Option: Distance from edge maps
        self.Habmat = False # Option: Transform land use maps in binary class maps
        self.PCT = False # Option: Generate percentage (of habitat, of edges) maps
        
        # Options
        # removeTrash: If True, maps generated in the middle of the processes for creating final maps are removed from GRASS location
        self.removeTrash = True
        # prepareBIODIM: If True, the package is run to prepare input maps and files to run BioDIM individual-based model package
        self.prepareBIODIM = False
        # calcStatistics: If True, statistics files of the maps are saved while creating them
        self.calcStatistics = False
        # formcalculate: 'Multiple' in case of running metrics for multiple maps, and 'Single' if running for only one map
        self.formcalculate = 'Single'
        
        # Auxiliary variables
        self.list_habitat_classes = []
        self.list_esc_pct = ''
        
        # GUI options
        
        # Size of the image of GUI
        self.size = 450
        self.hsize = 450
        
        # List of maps to be chosen inside a mapset, in GUI
        self.mapsList = []
        # Chosen map to be shown in the list
        self.chosen_map = ''
        #
        self.petternmaps = ''
        #
        self.start_raio = 0
        
        # Output options
        self.output_prefix2='' 
        
        self.label_prefix = ''
        self.RegularExp = ''
        self.listMapsPng = []
        self.listMapsPngAux = []
        self.contBG = 0
        self.plotmaps = 0
        self.lenlistpng = 0  
        
        self.ListmapsPatch = []
        self.ListMapsGroupCalc = []
        self.escala_frag_con = ''

        self.escala_ED = ''
        self.dirout = ''
        self.chebin = ''
        self.checEDGE = ''
        self.checkCalc_PCTedge = ''
        self.checPCT = ''
        self.check_diversity = ''
        self.analise_rayos = ''
        self.list_meco = ''
        
        
        
        
        #------------------------------------------------------#
        #---------------INITIALIZING GUI-----------------------#
        #------------------------------------------------------#
        
        ########### ver como conversar tamanho de pixel em windows e linux
        # Adjusting width of GUI elements depending on the Operational System
        if CURRENT_OS == "Windows":
          self.add_width = 0
        elif CURRENT_OS == "Linux":
          self.add_width = 100
        # MAC?
        else:
          self.add_width = 0
        
        # Listing maps within the mapset, to be displayed and select as input maps
        
        # If preparing maps for running BioDIM, the maps must be inside a mapset named 'userbase'
        if self.prepareBIODIM: 
          self.mapsList=grass.list_grouped ('rast') ['userbase']
        else:
          self.mapsList=grass.list_grouped ('rast') [self.current_mapset]
          
        #################### colocar isso de novo no final de uma rodada e atualizar o combobox - talvez o mapa
        ### gerado aparececa la!! testar!        
        
        #---------------------------------------------#
        #------------ MAIN GUI ELEMENTS --------------#
        #---------------------------------------------#
        
        # Title
        #self.quote = wx.StaticText(self, id=-1, label = "LandScape Metrics", pos = wx.Point(20, 20))
        
        #font = wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD)
        #self.quote.SetForegroundColour("blue")
        #self.quote.SetFont(font)
        #if not self.perform_tests:
        self.imageFile0 = 'lsmetrics_logo.png'
        im0 = Image.open(self.imageFile0)
        jpg0 = wx.Image(self.imageFile0, wx.BITMAP_TYPE_ANY).Scale(200, 82).ConvertToBitmap()
        wx.StaticBitmap(self, -1, jpg0, (100, 15), (jpg0.GetWidth(), jpg0.GetHeight()), style=wx.SUNKEN_BORDER)                  
        
        # LEEC lab logo
        imageFile = 'logo_lab.png'
        im1 = Image.open(imageFile)
        jpg1 = wx.Image(imageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        wx.StaticBitmap(self, -1, jpg1, (20, 470), (jpg1.GetWidth(), jpg1.GetHeight()), style=wx.SUNKEN_BORDER)
        
        # A multiline TextCtrl - This is here to show how the events work in this program, don't pay too much attention to it
        self.logger = wx.TextCtrl(self, 5, '', wx.Point(200, 470), wx.Size(160,150), wx.TE_MULTILINE | wx.TE_READONLY)        
        
        #---------------------------------------------#
        #-------------- RADIO BOXES ------------------#
        #---------------------------------------------#   
      
        # Calculate metrics for a single or multiple maps?
        self.single_multiple_maps = ['Single', 'Multiple']
        rb = wx.RadioBox(self, 92, "Calculate metrics for a \nsingle or multiple maps?", wx.Point(20, 102), wx.DefaultSize,
                         self.single_multiple_maps, 2, wx.RA_SPECIFY_ROWS)
        wx.EVT_RADIOBOX(self, 92, self.EvtRadioBox)
      
      
        # Prepare files and maps for running BioDIM individual-based model?
        self.BioDimChoice = ['No', 'Yes']
        rb = wx.RadioBox(self, 905, "Prepare maps for BioDIM?", wx.Point(20, 200), wx.DefaultSize,
                         self.BioDimChoice, 2, wx.RA_SPECIFY_COLS)
        wx.EVT_RADIOBOX(self, 905, self.EvtRadioBox)                   
        
        #---------------------------------------------#
        #-------------- STATIC TEXT ------------------#
        #---------------------------------------------#          
        
        # TEXT FOR OPTIONS
        self.SelectMap = wx.StaticText(self, -1, "Select input map:", wx.Point(250, 102))
        
        self.SelectMetrics = wx.StaticText(self,-1,"Regular Expression:", wx.Point(200, 165))    
  
        self.SelectMetrics = wx.StaticText(self,-1,"Create habitat map:", wx.Point(20, 260)) # Ou binary map?
        self.SelectMetrics = wx.StaticText(self,-1,"Codes for habitat:", wx.Point(140 + self.add_width, 260))
      
        self.SelectMetrics = wx.StaticText(self,-1,"Fragment- and patch-based metrics:", wx.Point(20, 290))
        self.SelectMetrics = wx.StaticText(self,-1,"Connectivity map:", wx.Point(20, 320))
        self.SelectMetrics = wx.StaticText(self,-1,"Gap crossing list (m):", wx.Point(140, 320))
      
        self.SelectMetrics = wx.StaticText(self,-1,"Core/Edge map:", wx.Point(20, 308))
        self.SelectMetrics = wx.StaticText(self,-1,"Edge depth list (m):", wx.Point(140, 308))
      
        self.SelectMetrics = wx.StaticText(self,-1,"Percentage:", wx.Point(20, 348))
        self.SelectMetrics = wx.StaticText(self,-1,"Habitat", wx.Point(90, 348))
        self.SelectMetrics = wx.StaticText(self,-1,"Edge/Core", wx.Point(156, 348))
      
        self.SelectMetrics = wx.StaticText(self,-1,"Extents:", wx.Point(236, 348)) # para as pct
      
        self.SelectMetrics = wx.StaticText(self,-1,"Calculate Statistics:", wx.Point(20, 445))
        self.SelectMetrics = wx.StaticText(self,-1,"Distance from edge map:", wx.Point(20, 375))
      
        self.SelectMetrics = wx.StaticText(self,-1,"Landscape diversity map:", wx.Point(20, 400))
        self.SelectMetrics = wx.StaticText(self,-1,"Extents (m):", wx.Point(170, 400)) # para  diversidade de shannon
      
        #self.SelectMetrics = wx.StaticText(self,-1,"List of scales for Area Path or Area Frag Unit(m):", wx.Point(20,190))
      
        self.SelectMetrics = wx.StaticText(self,-1,"Export: Hab/Edge/Matrix", wx.Point(20, 448))
        self.SelectMetrics = wx.StaticText(self,-1,"| Corridor/Branch/SS", wx.Point(170, 448))
        
        #---------------------------------------------#
        #-------------- COMBO BOXES ------------------#
        #---------------------------------------------#        
      
        # Maps shown when selecting a single map to calculate metrics
        try: # Try to select the first map of the list of maps loaded in the GRASS GIS location
          self.chosen_map = self.mapsList[0]
        except: # If there are no maps loaded
          self.chosen_map = ''
      
        self.editmapsList = wx.ComboBox(self, 93, self.chosen_map, wx.Point(100 + self.add_width, 130), wx.Size(280, -1),
                                        self.mapsList, wx.CB_DROPDOWN)
        wx.EVT_COMBOBOX(self, 93, self.EvtComboBox)
        wx.EVT_TEXT(self, 93, self.EvtText)        
        
        
        #---------------------------------------------#
        #-------------- CHECK BOXES ------------------#
        #---------------------------------------------#          
      
        #self.insure = wx.CheckBox(self, 96, "AH Patch.", wx.Point(70,150))
        #wx.EVT_CHECKBOX(self, 96,   self.EvtCheckBox)     
      
        #self.insure = wx.CheckBox(self, 95, "AH Frag.", wx.Point(143,150))
        #wx.EVT_CHECKBOX(self, 95,   self.EvtCheckBox)
        
        self.insure = wx.CheckBox(self, 100, "", wx.Point(120 + self.add_width, 265)) # Criando mapa de habitat botaozainho self.Habmat
        wx.EVT_CHECKBOX(self, 100,   self.EvtCheckBox)           
      
        self.insure = wx.CheckBox(self, 97, "", wx.Point(120, 320)) # area con connectivity
        wx.EVT_CHECKBOX(self, 97,   self.EvtCheckBox)  
      
        self.insure = wx.CheckBox(self, 150, "", wx.Point(120, 308)) #EDGE/Core
        wx.EVT_CHECKBOX(self, 150,   self.EvtCheckBox)  
        #"""
        #essa funcao a baixo eh o botao para saber se vai ou nao calcular o mapa de distancia euclidiana
          #"""        
        self.insure = wx.CheckBox(self, 151, "", wx.Point(135, 348)) # pct habitat
        wx.EVT_CHECKBOX(self, 151,   self.EvtCheckBox)            
      
        #"""
        #essa funcao a baixo eh o botao para saber se vai ou nao calcular o mapa de distancia euclidiana
        #"""
        self.insure = wx.CheckBox(self, 99, "", wx.Point(150, 375)) # self.Distedge botaozainho da distancia em relacao a borda
        wx.EVT_CHECKBOX(self, 99,   self.EvtCheckBox)  
      
      
        
      
        """
              essa funcao a baixo eh o botao para saber se vai ou nao calcular o mapa de diveridade de shannon
              """
        self.insure = wx.CheckBox(self, 101, "", wx.Point(150, 400)) # Criando mapa de diversidade de shannon
        wx.EVT_CHECKBOX(self, 101,   self.EvtCheckBox)   
      
      
        self.insure = wx.CheckBox(self, 152, "", wx.Point(215, 348)) # pct edge edge/core preciso implementar
        wx.EVT_CHECKBOX(self, 152,   self.EvtCheckBox)   
      
      
        """
              essa funcao a baixo eh o botao para saber se vai ou nao calcular a statistica para os mapas
              """
        self.insure = wx.CheckBox(self, 98, "", wx.Point(150, 445)) # self.calcStatistics botaozainho da statisica
        wx.EVT_CHECKBOX(self, 98,   self.EvtCheckBox)      
      
        self.insure = wx.CheckBox(self, 153, "", wx.Point(150, 448)) # export hab/edge/matrix
        wx.EVT_CHECKBOX(self, 153,   self.EvtCheckBox)       
      
        self.insure = wx.CheckBox(self, 154, "", wx.Point(275, 448)) # export corridor branch ss
        wx.EVT_CHECKBOX(self, 154,   self.EvtCheckBox)     

        #---------------------------------------------#
        #-------------- TEXT CONTROLS ----------------#
        #---------------------------------------------# 
        
        # Include fast description
        
        # Regular expression for selecting multiple maps
        self.editname1 = wx.TextCtrl(self, 190, '', wx.Point(240 + self.add_width, 160), wx.Size(100,-1))
        self.editname1.Disable()
        # List of gap crossing capability
        self.editname2 = wx.TextCtrl(self, 191, '', wx.Point(250 + self.add_width, 273), wx.Size(80,-1))
        # List of edge depths
        self.editname3 = wx.TextCtrl(self, 192, '', wx.Point(250 + self.add_width, 305), wx.Size(80,-1))
        # List of extents for percentage maps
        self.editname4 = wx.TextCtrl(self, 194, '', wx.Point(283 + self.add_width, 341), wx.Size(80,-1))
        # List of codes that represent habitat, for generating binary class maps
        self.editname5 = wx.TextCtrl(self, 193, '', wx.Point(250 + self.add_width, 242), wx.Size(80,-1))
        # List of radii on influence for calculating landscape diversity/heterogeneity
        self.editname6 = wx.TextCtrl(self, 195, '', wx.Point(250 + self.add_width, 395), wx.Size(80,-1))
        
        #---------------------------------------------#
        #-------------- TEXT EVENTS ------------------#
        #---------------------------------------------#       
        
        wx.EVT_TEXT(self, 190, self.EvtText)
        wx.EVT_TEXT(self, 191, self.EvtText)
        wx.EVT_TEXT(self, 192, self.EvtText)
        wx.EVT_TEXT(self, 193, self.EvtText)
        wx.EVT_TEXT(self, 194, self.EvtText)
        wx.EVT_TEXT(self, 195, self.EvtText)
        
        #---------------------------------------------#
        #-------------- BUTTONS ----------------------#
        #---------------------------------------------#        
        
        self.button = wx.Button(self, 10, "START CALCULATIONS", wx.Point(20, 630))
        wx.EVT_BUTTON(self, 10, self.OnClick)
        
        self.button = wx.Button(self, 8, "EXIT", wx.Point(270, 630))
        wx.EVT_BUTTON(self, 8, self.OnExit)        

        



                
        
    
        
        
        #______________________________________________________________________________________________________________ 
        #backgroun inicial
        #self.background_filename=['Pai10.png']
        #self.background_filename_start=self.background_filename[0]
                                
                                                          
        #img =Image.open(self.background_filename[0])
      
        ## redimensionamos sem perder a qualidade
        #img = img.resize((self.size,self.hsize),Image.ANTIALIAS)
        #img.save(self.background_filename[0])        
      
      
        #imageFile=self.background_filename[0]
        #im1 = Image.open(imageFile)
        #jpg1 = wx.Image(imageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        #wx.StaticBitmap(self, -1, jpg1, (380,40), (jpg1.GetWidth(),  jpg1.GetHeight()), style=wx.SIMPLE_BORDER)        
 
    def EvtRadioBox(self, event):
      if event.GetId()==905:
        self.prepareBIODIM=event.GetString()
        print self.prepareBIODIM
        if self.prepareBIODIM=="No":
          self.prepareBIODIM=False
        else:
          self.prepareBIODIM=True
          
      if self.prepareBIODIM:        
        self.mapsList=grass.list_grouped ('rast') ['userbase']
      else:
        self.mapsList=grass.list_grouped ('rast') ['PERMANENT']      
      
      # -----------
      # Radio Boxes
      
      if event.GetId() == 92: # Single or Multiple maps?
        
        self.formcalculate = event.GetString()
        
        if self.formcalculate == 'Single':
          self.editmapsList.Enable()
          self.editname1.Disable()
        elif self.formcalculate == 'Multiple':
          self.editmapsList.Disable()
          self.editname1.Enable()
        else:
          raise "Error: Calculations must be done for either single or multiple maps!"
          
        
        
        
        
       # self.logger.AppendText('Dispersive behaviour: %s\n' % )
     
     
     
     
    #______________________________________________________________________________________________________    
    def EvtComboBox(self, event):
        if event.GetId() == 93:   # 93 -> Single or Multiple maps combo box
            self.input_map=event.GetString()
            self.logger.AppendText('Map : %s' % event.GetString())
        else:
            self.logger.AppendText('EvtComboBox: NEED TO BE SPECIFIED' )
            
            


        
    #______________________________________________________________________________________________________   
    def OnClick(self,event):
        #self.logger.AppendText(" Click on object with Id %d\n" %event.GetId())
        
        #______________________________________________________________________________________________________________ 
        if event.GetId()==10:   #10==START

          # Before running and calculating the metrics, the user must define the output folder
          # where output maps and files will be saved
          self.dirout=selectdirectory()
          
          
          if self.formcalculate=="Single":
            
            if self.prepareBIODIM:
              self.output_prefix2 = 'lndscp_0001_'            
            
            if self.Habmat: ############ adicionei isso aqui: talvez temos que aplicar as outras funcoes ja nesse mapa?
              ###### as outras funcoes precisam de um mapa binario de entrada? ou pode ser so um mapa habitat/null?
              
              create_habmat_single(self.input_map, self.output_prefix2, self.list_habitat_classes, prepareBIODIM=self.prepareBIODIM, 
                                   calcStatistics=self.calcStatistics, dirout=self.dirout)
            if self.Patch==True:   
              
              patchSingle(self.input_map, self.output_prefix2, self.dirout, self.prepareBIODIM,self.calcStatistics,self.removeTrash)
              
            if self.Frag==True:
              
              areaFragSingle(self.input_map, self.output_prefix2, self.escala_frag_con, self.dirout, self.prepareBIODIM,self.calcStatistics,self.removeTrash)
            if self.Con==True:
              areaconSingle(self.input_map, self.output_prefix2, self.escala_frag_con, self.dirout, self.prepareBIODIM, self.calcStatistics, self.removeTrash)
            if self.checEDGE==True:
              
              create_EDGE_single(self.input_map, self.escala_ED, self.dirout, self.output_prefix2, self.calcStatistics, self.removeTrash,self.list_esc_pct)
             
            if self.Dist==True:
              dist_edge_Single(self.input_map,self.output_prefix2, self.prepareBIODIM, self.dirout, self.removeTrash)
              
            if self.checPCT==True:
              PCTs_single(self.input_map, self.list_esc_pct)
            if self.check_diversity==True:
              shannon_diversity(self.input_map, self.dirout, self.analise_rayos)
            
          else: # caso seja pra mais de um arquivos
                      
            if self.prepareBIODIM:
              self.ListMapsGroupCalc=grass.list_grouped ('rast', pattern=self.RegularExp) ['userbase']
              self.output_prefix2 = 'lndscp_'              
            else:
              self.ListMapsGroupCalc=grass.list_grouped ('rast', pattern=self.RegularExp) ['PERMANENT']   
              
            if self.Habmat: ############ adicionei isso aqui: talvez temos que aplicar as outras funcoes ja nesse mapa?
              ###### as outras funcoes precisam de um mapa binario de entrada? ou pode ser so um mapa habitat/null?
              create_habmat(self.ListMapsGroupCalc, list_habitat_classes=self.list_habitat_classes, 
                            prepareBIODIM=self.prepareBIODIM, calcStatistics=self.calcStatistics, prefix = self.output_prefix2)            
            
             
            
            if self.checEDGE==True:
              self.list_meco=create_EDGE(self.ListMapsGroupCalc, self.escala_ED, self.dirout, self.output_prefix2, self.calcStatistics, self.removeTrash,self.list_esc_pct,self.checkCalc_PCTedge)     
              areaFrag(self.ListMapsGroupCalc, self.output_prefix2,self.escala_ED, self.dirout, self.prepareBIODIM,self.calcStatistics,self.removeTrash,self.list_meco,self.checEDGE)
              
            
            if self.Frag==True:
              self.list_meco=[]
              self.checEDGE=False
              
              areaFrag(self.ListMapsGroupCalc, self.output_prefix2, self.escala_frag_con, self.dirout, self.prepareBIODIM,self.calcStatistics,self.removeTrash,self.list_meco,self.checEDGE)
              
            if self.Con==True:
              self.ListmapsPatch=Patch(self.ListMapsGroupCalc, self.output_prefix2, self.dirout, self.prepareBIODIM,self.calcStatistics,self.removeTrash)
              areacon(self.ListMapsGroupCalc,self.output_prefix2, self.escala_frag_con, self.dirout, self.prepareBIODIM, self.calcStatistics, self.removeTrash) 
              
            
            if self.Dist==True:
              dist_edge(self.ListMapsGroupCalc,self.output_prefix2, self.prepareBIODIM, self.dirout, self.removeTrash)
            
            if self.checPCT==True:
              PCTs(self.ListMapsGroupCalc, self.list_esc_pct)
               
        
        #______________________________________________________________________________________________________________ 
        if event.GetId()==9:   #9==CHANGE BACKGROUND
          if self.plotmaps==1:
            if self.formcalculate=="Single":
              x=1
            else:
              self.Refresh()
              self.background_filename=self.listMapsPng
              self.background_filename_start=self.background_filename[self.contBG]   
              img =Image.open(self.background_filename[self.contBG])
            
              # redimensionamos sem perder a qualidade
              img = img.resize((self.size,self.hsize),Image.ANTIALIAS)
              img.save(self.background_filename[self.contBG])        
            
            
              imageFile=self.background_filename[self.contBG]
              im1 = Image.open(imageFile)
              jpg1 = wx.Image(imageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
              wx.StaticBitmap(self, -1, jpg1, (380,40), (jpg1.GetWidth(),  jpg1.GetHeight()), style=wx.SIMPLE_BORDER)
                                
              self.background_filename=self.background_filename_start
              self.contBG=self.contBG+1
              self.Refresh() 
              if len(self.listMapsPng)==self.contBG:
                self.contBG=0      
                self.Refresh() 
              #______________________________________________________________________________________________________________ 
        if event.GetId()==11:   
          if self.chebin==True:
            if  self.formcalculate=="Single":
              createBinarios_single(self.input_map)
            else:
              
              if self.prepareBIODIM:
                self.ListMapsGroupCalc=grass.list_grouped ('rast', pattern=self.RegularExp) ['userbase']
              else:
                self.ListMapsGroupCalc=grass.list_grouped ('rast', pattern=self.RegularExp) ['PERMANENT']                
              
              createBinarios(self.ListMapsGroupCalc)
          
          
        
        
        # 
        d= wx.MessageDialog( self, " Calculations finished! \n"
                            " ","Thanks", wx.OK)
                            # Create a message dialog box
        d.ShowModal() # Shows it
        d.Destroy()
        
    
    #______________________________________________________________________________________________________________                
    def EvtText(self, event):
        #self.logger.AppendText('EvtText: %s\n' % event.GetString())
      #______________________________________________________________________________________________________________ 
           
        if event.GetId()==190:
          self.RegularExp=event.GetString() 
          
        if event.GetId()==191:
          self.escala_frag_con=event.GetString()
          
        if event.GetId()==192:
          self.escala_ED=event.GetString()    
          
        if event.GetId()==193:
          list_habitat=event.GetString()
          self.list_habitat_classes=list_habitat.split(',')
          #self.list_habitat_classes=[int(i) for i in list_habitat.split(',')] # we do not have to transform in integers - command run already in strings, for passing it to GRASS
        
        if event.GetId()==194:
          # funcao para pegar a lista de escalas de porcentagem
          list_esc_percent=event.GetString()
          self.list_esc_pct=list_esc_percent.split(',')
        if event.GetId()==195:
          # funcao para pegar a lista de escalas de porcentagem
          list_esc_raios_DV=event.GetString()
          self.analise_rayos=list_esc_raios_DV.split(',')        
          
        

    #______________________________________________________________________________________________________
    def EvtCheckBox(self, event):
        #self.logger.AppendText('EvtCheckBox: %d\n' % event.Checked())
        if event.GetId()==95:
            if event.Checked()==1:
                self.Frag=True
                self.logger.AppendText('EvtCheckBox:\nMetric Selected: Frag \n')
            else:
                self.Frag=False
                self.logger.AppendText('EvtCheckBox: \nMetric Not Selected: Frag \n')
                
                
        if event.GetId()==96:
          if event.Checked()==1:
            self.Patch=True
            self.logger.AppendText('EvtCheckBox:\nMetric Selected: Patch \n')
          else:
            self.Patch=False
            self.logger.AppendText('EvtCheckBox:\nMetric Not Selected: Patch \n')
                   
            
        if event.GetId()==97:
          if event.Checked()==1:
            self.Con=True
            self.logger.AppendText('EvtCheckBox:\nMetric Selected: Connectivity \n')
          else:
            self.Con=False
            self.logger.AppendText('EvtCheckBox:\nMetric Not Selected: Connectivity \n')
                         
        
        if event.GetId()==98: #criando txtx de statitiscas
          if int(event.Checked())==1: 
            self.calcStatistics=True           
            self.logger.AppendText('EvtCheckBox:\nCalculate connectivity statistics: '+`self.calcStatistics`+' \n')
            
            
            
        if event.GetId()==99: #criando mapa de distancia 
          if int(event.Checked())==1:
            self.Dist=True
            self.logger.AppendText('EvtCheckBox:\n Create Distance map: '+`self.Dist`+' \n')
            
        if event.GetId()==100:
          if int(event.Checked())==1:
            self.Habmat=True
            self.logger.AppendText('EvtCheckBox:\nCreate Habitat Map '+`self.Dist`+' \n')
        
        #
        if event.GetId()==101: #check EDGE
          if int(event.Checked())==1:
            self.check_diversity=True
            self.logger.AppendText('EvtCheckBox:\nMetric Selected: Diversity shannon map \n')
          else:
            self.check_diversity=False
            self.logger.AppendText('EvtCheckBox:\nMetric Not Selected: Diversity shannon map \n')         
        
        if event.GetId()==150: #check EDGE
          if int(event.Checked())==1:
            self.checEDGE=True
            self.logger.AppendText('EvtCheckBox:\nMetric Selected: Edge \n')
          else:
            self.checEDGE=False
            self.logger.AppendText('EvtCheckBox:\nMetric Not Selected: Edge \n')
          
         
         
        if event.GetId()==151: #check EDGE
          if int(event.Checked())==1:
            self.checPCT=True
            self.logger.AppendText('EvtCheckBox:\nMetric Selected: Percentage habitat \n')
          else:
            self.checPCT=False
            self.logger.AppendText('EvtCheckBox:\nMetric Not Selected: Percentage habitat \n')           
        
        # CRIAR UM BOTAO E UM EVENTO DESSES AQUI, PARA O MAPA DE DIST (mesmo que ele so seja usado para o biodim)
        if event.GetId()==152: #check EDGE
          if int(event.Checked())==1:
            self.checkCalc_PCTedge=True
            self.logger.AppendText('EvtCheckBox:\nMetric Selected: Percentage from edge/core \n')
          else:
            self.checkCalc_PCTedge=False
            self.logger.AppendText('EvtCheckBox:\nMetric Not Selected: Percentage from edge/core \n')             
        
         
            
    #______________________________________________________________________________________________________
    def OnExit(self, event):
        d= wx.MessageDialog( self, " Thanks for using LSMetrics "+VERSION+"!\n"
                            "","Good bye", wx.OK)
                            # Create a message dialog box
        d.ShowModal() # Shows it
        d.Destroy() # finally destroy it when finished.
        frame.Close(True)  # Close the frame. 

#----------------------------------------------------------------------
#......................................................................
#----------------------------------------------------------------------
if __name__ == "__main__":
    
    # Size of the window
    ########### ver como conversar tamanho de pixel em windows e linux
    # Adjusting width of GUI depending on the Operational System
    if CURRENT_OS == "Windows":
      size = (500, 680)
    elif CURRENT_OS == "Linux":
      size = (600, 680)
    # MAC?    
    
    app = wx.PySimpleApp()
    frame = wx.Frame(None, -1, "LSMetrics "+VERSION, size=size)
    LSMetrics(frame,-1)
    frame.Show(1)
    
    app.MainLoop()
