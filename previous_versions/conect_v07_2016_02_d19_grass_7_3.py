#!/c/Python25 python
#---------------------------------------------------------------------------------------
"""
 LS Connectivity - LandScape Connectivity Calculator
 Version 0.9
 
 John W. Ribeiro - jw.ribeiro.rc@gmail.com
 Bernardo B. S. Niebuhr - bernardo_brandaum@yahoo.com.br
 Milton C. Ribeiro - mcr@rc.unesp.br
 
 Laboratorio de Ecologia Espacial e Conservacao
 Universidade Estadual Paulista - UNESP
 Rio Claro - SP - Brasil
 
 LS Connectivity is a software designed to calculate landscape metrics and
 landscape statistics and generate maps of landscape connectivity.
 Also, the software is designed to prepare maps and enviroment for running 
 BioDIM, an individual-based model of animal movement in fragmented landscapes.
 The software runs in a GRASS GIS environment and uses raster images as input.
 
 Aqui podemos colocar mais comentarios sobre o funcionamento do LS Con...
"""
#---------------------------------------------------------------------------------------

import sys, os, numpy #sys, os, PIL, numpy, Image, ImageEnhance
import grass.script as grass
from PIL import Image
import wx
import random
import numpy as np
import re
import math


ID_ABOUT=101
ID_IBMCFG=102
ID_EXIT=110

################
# CONFERIR LISTA DE PATTERN MULTIPLE COM O JOHN (E TODAS AS VEZES QUE APARECEU O [PERMANENT] OU [userbase])

########################
# -arrumar script R para gerar as figuras que queremos
# como conversa o R com o grass? da pra rodar o script R em BATCH mode?

#----------------------------------------------------------------------------------
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
  dialog = wx.DirDialog(None, "Select the output folder:",style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
  if dialog.ShowModal() == wx.ID_OK:
    #print ">>..................",dialog.GetPath()
    return dialog.GetPath()


def createBinarios_single(ListMapBins):
  """
  This function reclassify an input map into a binary map, according to reclassification rules passed by
  a text file
  """
  readtxt=selectdirectory()
  grass.run_command('g.region',rast=ListMapBins)
  grass.run_command('r.reclass',input=ListMapBins,output=ListMapBins+'_HABMAT',rules=readtxt, overwrite = True)
  
  if Form1.prepareBIODIM:
    Form1.speciesList=grass.list_grouped ('rast', pattern='(*)') ['userbase']
  else:
    Form1.speciesList=grass.list_grouped ('rast', pattern='(*)') ['PERMANENT']  
  return readtxt
  
def createBinarios(ListMapBins):
  """
  This function reclassify a series of input maps into binary maps, according to reclassification rules passed by
  a text file
  """
  readtxt=selectdirectory()
  for i in ListMapBins:
    grass.run_command('g.region',rast=i)
    grass.run_command('r.reclass',input=i,output=i+'_HABMAT',rules=readtxt, overwrite = True)
    if Form1.prepareBIODIM:
      Form1.speciesList=grass.list_grouped ('rast', pattern='(*)') ['userbase']
    else:
      Form1.speciesList=grass.list_grouped ('rast', pattern='(*)') ['PERMANENT']    
    return readtxt
  
def create_habmat_single(ListMapBins_in, prefix = ''):
  """
  Function for a single map
  This function reclassify an input map into a binary map, according to reclassification rules passed by
  a text file
  """

  ListMapBins = prefix+'_'+ListMapBins_in
  
  # opcao 1: ler um arquivo e fazer reclass
  # TEMOS QUE ORGANIZAR ISSO AINDA!!
  #readtxt=selectdirectory()
  #grass.run_command('g.region',rast=ListMapBins)
  #grass.run_command('r.reclass',input=ListMapBins,output=ListMapBins+'_HABMAT',rules=readtxt, overwrite = True)
  
  # opcao 2: definir quais classes sao habitat; todas as outras serao matriz
  if(len(Form1.list_habitat_classes) > 0):
    
    conditional = ''
    cc = 0
    for j in Form1.list_habitat_classes:
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
    
  if Form1.prepareBIODIM:
    create_TXTinputBIODIM([ListMapBins+'_HABMAT'], "simulados_HABMAT", Form1.dirout)   
  else:
    grass.run_command('g.region', rast=ListMapBins+'_HABMAT')
    grass.run_command('r.out.gdal', input=ListMapBins+'_HABMAT', out=ListMapBins+'_HABMAT.tif',overwrite = True)
  
  if Form1.calcStatistics:
    createtxt(ListMapBins+'_HABMAT', Form1.dirout, ListMapBins+'_HABMAT')


def create_habmat(ListMapBins, prefix = ''):
  """
  Function for a series of maps
  This function reclassify an input map into a binary map, according to reclassification rules passed by
  a text file
  """
  
  if Form1.prepareBIODIM:
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
        pre_numb = "000"+`cont`
      elif cont <= 99:
        pre_numb = "00"+`cont`
      elif cont <= 999:        
        pre_numb = "0"+`cont`
      else: 
        pre_numb = `cont`  
    
    if(len(Form1.list_habitat_classes) > 0):
      conditional = ''
      cc = 0
      for j in Form1.list_habitat_classes:
        if cc > 0:
          conditional = conditional+' || '
        conditional = conditional+i_in+' == '+j
        cc += 1
      
      i = prefix+pre_numb+'_'+i_in
      
      expression = i+'_HABMAT = if('+conditional+', 1, 0)'
      grass.run_command('g.region', rast=i_in)
      grass.mapcalc(expression, overwrite = True, quiet = True)
      grass.run_command('r.null', map=i+'_HABMAT', null='0') # precisa disso?? 
    else:
      print 'You did not type which class is habitat!! Map not generated' # organizar para dar um erro; pode ser com try except 
    
    if Form1.prepareBIODIM:
      lista_maps_habmat.append(i+'_HABMAT') 
    else:
      grass.run_command('g.region', rast=i+'_HABMAT')
      grass.run_command('r.out.gdal', input=i+'_HABMAT', out=i+'_HABMAT.tif',overwrite = True)
  
    if Form1.calcStatistics:
      createtxt(i+'_HABMAT', Form1.dirout, i+'_HABMAT')
      
    cont += 1
      
  if Form1.prepareBIODIM:
    create_TXTinputBIODIM(lista_maps_habmat, "simulados_HABMAT", Form1.dirout)  
    
def rulesreclass(mapa,dirs):
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
 
############
# JOHN, as funcoes escala con e escala frag sao realmente diferentes?
# sao sim Ber, depois te explico melhor como funciona

def escala_con(mapa,esc):
  """
  This function separates the input for functional connectivity maps (CON), separatins scales (distances)
  which will be used to generate the maps. Also, it defines the numbers of pixels to consider, besides distances
  ############# EH ISSO?
  """
  esclist=esc.split(',')
  res=grass.read_command('g.region', rast=mapa, flags='m')
  res2=res.split('\n')
  res3=res2[5]
  res3=float(res3.replace('ewres=',''))
  listasizefinal=[]
  listametersfinal=[]  
  for i in esclist:
    esc=int(i)
    escfina1=(esc)/res3
    
    escfina1=int(round(escfina1, ndigits=0))  
    if escfina1%2==0:
      escfina1=int(escfina1)
      escfina1=escfina1+1
      listasizefinal.append(escfina1)
      listametersfinal.append(esc)
    else:
      escfina1=int(round(escfina1, ndigits=0))
      listasizefinal.append(escfina1)
      listametersfinal.append(esc)      
  return listasizefinal,listametersfinal # number of pixels+1, number of meters
    
def escala_frag(mapa,esc):
  """
  This function separates the input for fragmented maps (FRAG, excluding corridors/edges), 
  separatins scales (distances) which will be used to generate the maps. 
  Also, it defines the numbers of pixels to consider, besides distances
  ############# EH ISSO?
  """
  esclist=esc.split(',')
  res=grass.read_command('g.region', rast=mapa, flags='m')
  res2=res.split('\n')
  res3=res2[5]
  res3=float(res3.replace('ewres=',''))
  
  listasizefinal=[]
  listametersfinal=[]
  for i in esclist:
    esc=int(i)
    escfina1=esc/res3
    escfina1=escfina1*2 # pq vezes 2?
    if escfina1%2==0:
      escfina1=int(escfina1)
      escfina1=escfina1+1
      listasizefinal.append(escfina1)
      listametersfinal.append(esc)
    else:
      escfina1=int(round(escfina1, ndigits=0))
      listasizefinal.append(escfina1)
      listametersfinal.append(esc)      
  return listasizefinal,listametersfinal

#----------------------------------------------------------------------------------
# Metrics for fragmented (excluding edges/corridors) views of landscapes (FRAG)

def areaFragSingle(ListmapsFrag_in, prefix = ''):
  """
  Function for a single map
  This function fragments patches (FRAG), excluding corridors and edges given input scales (distances), and:
  - generates and exports maps with Patch ID and Area of each "fragmented" patch
  - generatics statistics - Area per patch (if Form1.calcStatistics == True)
  """
  
  ListmapsFrag = prefix+'_'+ListmapsFrag_in
  
  grass.run_command('g.region', rast=ListmapsFrag_in)
  Lista_escalafragM, listmeters = escala_frag(ListmapsFrag_in, Form1.escala_frag_con)

  x=0
  for a in Lista_escalafragM:
    meters=int(listmeters[x])  
    #print escalafragM
    grass.run_command('r.neighbors', input=ListmapsFrag_in, output=ListmapsFrag+"_ero_"+`meters`+'m', method='minimum', size=a, overwrite = True)
    grass.run_command('r.neighbors', input=ListmapsFrag+"_ero_"+`meters`+'m', output=ListmapsFrag+"_dila_"+`meters`+'m', method='maximum', size=a, overwrite = True)
    expressao1=ListmapsFrag+"_FRAG"+`meters`+"m_mata = if("+ListmapsFrag+"_dila_"+`meters`+'m'+" > 0, "+ListmapsFrag+"_dila_"+`meters`+'m'+", null())"
    grass.mapcalc(expressao1, overwrite = True, quiet = True)
    expressao2=ListmapsFrag+"_FRAG"+`meters`+"m_mata_lpo = if("+ListmapsFrag_in+" >= 0, "+ListmapsFrag+"_FRAG"+`meters`+"m_mata, null())"
    grass.mapcalc(expressao2, overwrite = True, quiet = True)
    grass.run_command('r.clump', input=ListmapsFrag+"_FRAG"+`meters`+"m_mata_lpo", output=ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_pid", overwrite = True)
    
    grass.run_command('g.region', rast=ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_pid")
    nametxtreclass=rulesreclass(ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_pid", Form1.dirout)
    grass.run_command('r.reclass', input=ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_pid", output=ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_AreaHA", rules=nametxtreclass, overwrite = True)    
    os.remove(nametxtreclass)
    
    if Form1.prepareBIODIM:
      #grass.run_command('r.out.gdal',input=ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_pid",out=ListmapsFrag+"_FRAG"+`meters`+"m_PID.tif")
      create_TXTinputBIODIM([ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_pid"], "simulados_HABMAT_FRAC_"+`meters`+"m_PID", Form1.dirout)
      create_TXTinputBIODIM([ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_AreaHA"], "simulados_HABMAT_FRAC_"+`meters`+"m_AREApix", Form1.dirout)
    else:
      grass.run_command('g.region', rast=ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_AreaHA")
      grass.run_command('r.out.gdal', input=ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_AreaHA", out=ListmapsFrag+"_FRAG"+`meters`+"m_AreaHA.tif",overwrite = True)      
      
    if Form1.calcStatistics:
      createtxt(ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_pid", Form1.dirout, ListmapsFrag+"_FRAG"+`meters`+"m_AreaHA")        
    
    if Form1.removeTrash:
      if Form1.prepareBIODIM:
        txts = [ListmapsFrag+"_ero_"+`meters`+'m', ListmapsFrag+"_dila_"+`meters`+'m', ListmapsFrag+"_FRAG"+`meters`+"m_mata", ListmapsFrag+"_FRAG"+`meters`+"m_mata_lpo"]
      else:
        txts = [ListmapsFrag+"_ero_"+`meters`+'m', ListmapsFrag+"_dila_"+`meters`+'m', ListmapsFrag+"_FRAG"+`meters`+"m_mata", ListmapsFrag+"_FRAG"+`meters`+"m_mata_lpo"] #, ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_pid"]
      for txt in txts:
        grass.run_command('g.remove', type="raster", name=txt, flags='f')
    x=x+1     

def areaFrag(ListmapsFrag, prefix = ''):
  """
  Function for a series of maps
  This function fragments patches (FRAG), excluding corridors and edges given input scales (distances), and:
  - generates and exports maps with Patch ID and Area of each "fragmented" patch
  - generatics statistics - Area per patch (if Form1.calcStatistics == True)
  """

  if Form1.prepareBIODIM:
    esc, met = escala_frag(ListmapsFrag[0], Form1.escala_frag_con)
    lista_maps_pid = np.empty((len(ListmapsFrag), len(esc)), dtype=np.dtype('a200'))
    lista_maps_area = np.empty((len(ListmapsFrag), len(esc)), dtype=np.dtype('a200'))
  
  z = 0
  cont = 1
  for i_in in ListmapsFrag:
    
    if prefix == '':
      pre_numb = ''
    else:
      if cont <= 9:
        pre_numb = "000"+`cont`
      elif cont <= 99:
        pre_numb = "00"+`cont`
      elif cont <= 999:        
        pre_numb = "0"+`cont`
      else: 
        pre_numb = `cont`
      
    i = prefix+pre_numb+'_'+i_in
          
    grass.run_command('g.region', rast=i_in)
    Lista_escalafragM, listmeters = escala_frag(i_in, Form1.escala_frag_con)
    #print escalafragM
    x=0
    #lista_maps_pid=[]
    #lista_maps_area=[]
    for a in Lista_escalafragM:
      meters=int(listmeters[x])
      #print a
      grass.run_command('r.neighbors', input=i_in, output=i+"_ero_"+`meters`+'m', method='minimum', size=a, overwrite = True)
      grass.run_command('r.neighbors', input=i+"_ero_"+`meters`+'m', output=i+"_dila_"+`meters`+'m', method='maximum', size=a, overwrite = True)
      expressao1=i+"_FRAG"+`meters`+"m_mata = if("+i+"_dila_"+`meters`+'m'+">0,"+i+"_dila_"+`meters`+'m'+",null())"
      grass.mapcalc(expressao1, overwrite = True, quiet = True)
      expressao2=i+"_FRAG"+`meters`+"m_mata_lpo = if("+i_in+" >= 0, "+i+"_FRAG"+`meters`+"m_mata, null())"
      grass.mapcalc(expressao2, overwrite = True, quiet = True)      
      grass.run_command('r.clump', input=i+"_FRAG"+`meters`+"m_mata_lpo", output=i+"_FRAG"+`meters`+"m_mata_clump_pid", overwrite = True)
      grass.run_command('g.region', rast=i+"_FRAG"+`meters`+"m_mata_clump_pid")
      nametxtreclass=rulesreclass(i+"_FRAG"+`meters`+"m_mata_clump_pid", Form1.dirout)
      grass.run_command('r.reclass', input=i+"_FRAG"+`meters`+"m_mata_clump_pid", output=i+"_FRAG"+`meters`+"m_mata_clump_AreaHA", rules=nametxtreclass, overwrite = True)    
      os.remove(nametxtreclass) 
      
      if Form1.prepareBIODIM:    
        #grass.run_command('r.out.gdal',input=i+"_FRAG"+`meters`+"m_mata_clump_pid",out=i+"_FRAG"+`meters`+"m_PID.tif")
        lista_maps_pid[z,x] = i+"_FRAG"+`meters`+"m_mata_clump_pid"
        lista_maps_area[z,x] = i+"_FRAG"+`meters`+"m_mata_clump_AreaHA"
        #lista_maps_pid.append(i+"_FRAG"+`meters`+"m_mata_clump_pid")
        #lista_maps_area.append(i+"_FRAG"+`meters`+"m_mata_clump_AreaHA")
      else:
        grass.run_command('g.region', rast=i+"_FRAG"+`meters`+"m_mata_clump_AreaHA")
        grass.run_command('r.out.gdal', input=i+"_FRAG"+`meters`+"m_mata_clump_AreaHA", out=i+"_FRAG"+`meters`+"m_AreaHA.tif", overwrite = True)        
      
      if Form1.calcStatistics:      
        createtxt(i+"_FRAG"+`meters`+"m_mata_clump_pid", Form1.dirout, i+"_FRAG"+`meters`+"m_AreaHA")      
      
      if Form1.removeTrash:
        if Form1.prepareBIODIM:
          txts = [i+"_ero_"+`meters`+'m', i+"_dila_"+`meters`+'m', i+"_FRAG"+`meters`+"m_mata", i+"_FRAG"+`meters`+"m_mata_lpo"]
        else:        
          txts = [i+"_ero_"+`meters`+'m', i+"_dila_"+`meters`+'m', i+"_FRAG"+`meters`+"m_mata", i+"_FRAG"+`meters`+"m_mata_lpo"] #, i+"_FRAG"+`meters`+"m_mata_clump_pid"]
        for txt in txts:
          grass.run_command('g.remove', type="raster", name=txt, flags='f')
      x=x+1
    z=z+1
    cont += 1
  
  if Form1.prepareBIODIM:
    for i in range(len(met)):
      mm = int(met[i])
      create_TXTinputBIODIM(lista_maps_pid[:,i].tolist(), "simulados_HABMAT_FRAC_"+`mm`+"m_PID", Form1.dirout)
      create_TXTinputBIODIM(lista_maps_area[:,i].tolist(), "simulados_HABMAT_FRAC_"+`mm`+"m_AREApix", Form1.dirout)              
      
      
#----------------------------------------------------------------------------------
# Metrics for patch size/area/ID (PATCH)

def patchSingle(Listmapspatch_in, prefix = ''):
  """
  Function for a single map
  This function calculates area per patch in a map (PATCH), considering structural connectivity 
  (no fragmentation or dilatation):
  - generates and exports maps with Patch ID and Area of each patch
  - generatics statistics - Area per patch (if Form1.calcStatistics == True)
  """
  
  Listmapspatch = prefix+'_'+Listmapspatch_in
  
  grass.run_command('g.region', rast=Listmapspatch_in)
  grass.run_command('r.clump', input=Listmapspatch_in, output=Listmapspatch+"_patch_clump", overwrite = True)
  ########## essa proxima linha muda algo?? clump * mata/nao-mata  
  expression12=Listmapspatch+"_patch_clump_mata = "+Listmapspatch+"_patch_clump*"+Listmapspatch_in
  grass.mapcalc(expression12, overwrite = True, quiet = True)
  expression13=Listmapspatch+"_patch_clump_mata_limpa_pid = if("+Listmapspatch+"_patch_clump_mata > 0, "+Listmapspatch+"_patch_clump_mata, null())"
  grass.mapcalc(expression13, overwrite = True, quiet = True)
  
  nametxtreclass=rulesreclass(Listmapspatch+"_patch_clump_mata_limpa_pid", Form1.dirout)
  grass.run_command('r.reclass', input=Listmapspatch+"_patch_clump_mata_limpa_pid", output=Listmapspatch+"_patch_clump_mata_limpa_AreaHA", rules=nametxtreclass, overwrite = True)
  os.remove(nametxtreclass)
  
  if Form1.prepareBIODIM:
    #grass.run_command('r.out.gdal',input=Listmapspatch+"_patch_clump_mata_limpa",out=Listmapspatch+"_patch_PID.tif")
    create_TXTinputBIODIM([Listmapspatch+"_patch_clump_mata_limpa_pid"], "simulados_HABMAT_grassclump_PID", Form1.dirout)
    create_TXTinputBIODIM([Listmapspatch+"_patch_clump_mata_limpa_AreaHA"], "simulados_HABMAT_grassclump_AREApix", Form1.dirout)    
  else:
    grass.run_command('g.region', rast=Listmapspatch+"_patch_clump_mata_limpa_AreaHA")
    grass.run_command('r.out.gdal', input=Listmapspatch+"_patch_clump_mata_limpa_AreaHA", out=Listmapspatch+"_patch_AreaHA.tif",overwrite = True)
  
  if Form1.calcStatistics:
    createtxt(Listmapspatch+"_patch_clump_mata_limpa_pid", Form1.dirout, Listmapspatch+"_patch_AreaHA")
  
  if Form1.removeTrash:
    if Form1.prepareBIODIM:
      txts = [Listmapspatch+"_patch_clump", Listmapspatch+"_patch_clump_mata"]
    else:
      txts = [Listmapspatch+"_patch_clump", Listmapspatch+"_patch_clump_mata"] #, Listmapspatch+"_patch_clump_mata_limpa_pid"]
    for txt in txts:
      grass.run_command('g.remove', type="raster", name=txt, flags='f')
  
def Patch(Listmapspatch, prefix = ''):
  """
  Function for a series of maps
  This function calculates area per patch in a map (PATCH), considering structural connectivity 
  (no fragmentation or dilatation):
  - generates and exports maps with Patch ID and Area of each patch
  - generatics statistics - Area per patch (if Form1.calcStatistics == True)
  """
  
  if Form1.prepareBIODIM:
    lista_maps_pid=[]
    lista_maps_area=[]  

  cont = 1
  for i_in in Listmapspatch:
    
    if prefix == '':
      pre_numb = ''
    else:
      if cont <= 9:
        pre_numb = "000"+`cont`
      elif cont <= 99:
        pre_numb = "00"+`cont`
      elif cont <= 999:        
        pre_numb = "0"+`cont`
      else: 
        pre_numb = `cont`
      
    i = prefix+pre_numb+'_'+i_in

    grass.run_command('g.region', rast=i_in)
    grass.run_command('r.clump', input=i_in, output=i+"_patch_clump", overwrite = True)
    expression12=i+"_patch_clump_mata = "+i+"_patch_clump*"+i_in
    grass.mapcalc(expression12, overwrite = True, quiet = True)
    expression13=i+"_patch_clump_mata_limpa_pid = if("+i+"_patch_clump_mata > 0, "+i+"_patch_clump_mata, null())"
    grass.mapcalc(expression13, overwrite = True, quiet = True)
    
    nametxtreclass=rulesreclass(i+"_patch_clump_mata_limpa_pid", Form1.dirout)
    grass.run_command('r.reclass', input=i+"_patch_clump_mata_limpa_pid", output=i+"_patch_clump_mata_limpa_AreaHA", rules=nametxtreclass, overwrite = True)
    os.remove(nametxtreclass)
    
    if Form1.prepareBIODIM:
      #grass.run_command('r.out.gdal',input=i+"_patch_clump_mata_limpa_pid",out=i+"_patch_PID.tif")
      lista_maps_pid.append(i+"_patch_clump_mata_limpa_pid")
      lista_maps_area.append(i+"_patch_clump_mata_limpa_AreaHA")      
    else:
      grass.run_command('g.region', rast=i+"_patch_clump_mata_limpa_AreaHA")
      grass.run_command('r.out.gdal', input=i+"_patch_clump_mata_limpa_AreaHA", out=i+"_patch_AreaHA.tif",overwrite = True)
          
    if Form1.calcStatistics:
      createtxt(i+"_patch_clump_mata_limpa_pid", Form1.dirout, i+"_patch_AreaHA")
    
    if Form1.removeTrash:
      if Form1.prepareBIODIM:
        txts = [i+"_patch_clump", i+"_patch_clump_mata"]
      else:
        txts = [i+"_patch_clump", i+"_patch_clump_mata"]#, i+"_patch_clump_mata_limpa_pid"]
      for txt in txts:
        grass.run_command('g.remove', type="raster", name=txt, flags='f')
        
    cont += 1
        
    
  if Form1.prepareBIODIM:
    create_TXTinputBIODIM(lista_maps_pid, "simulados_HABMAT_grassclump_PID", Form1.dirout)
    create_TXTinputBIODIM(lista_maps_area, "simulados_HABMAT_grassclump_AREApix", Form1.dirout)  
  
  return Listmapspatch

#----------------------------------------------------------------------------------
# Metrics for functional connectivity area/ID (CON)

def areaconSingle(Listmapspatch_in, prefix = ''):
  """
  Function for a single map
  This function calculates functional patch area in a map (CON), considering functional connectivity 
  (dilatation of edges given input scales/distances), and:
  - generates and exports maps with Patch ID and Area of each patch
  - generatics statistics - Area per patch (if Form1.calcStatistics == True)
  """
  
  Listmapspatch = prefix+'_'+Listmapspatch_in

  grass.run_command('g.region', rast=Listmapspatch_in)
  listescalafconM, listmeters = escala_con(Listmapspatch_in, Form1.escala_frag_con)
  
  x=0
  for a in listescalafconM:
    meters = int(listmeters[x])
    grass.run_command('r.neighbors', input=Listmapspatch_in, output=Listmapspatch+"_dila_"+`meters`+'m_orig', method='maximum', size=a, overwrite = True)
    expression=Listmapspatch+"_dila_"+`meters`+'m_orig_temp = if('+Listmapspatch+"_dila_"+`meters`+'m_orig == 0, null(), '+Listmapspatch+"_dila_"+`meters`+'m_orig)'
    grass.mapcalc(expression, overwrite = True, quiet = True)
    grass.run_command('r.clump', input=Listmapspatch+"_dila_"+`meters`+'m_orig_temp', output=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_pid', overwrite = True)
    espressao1=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata = '+Listmapspatch_in+'*'+Listmapspatch+"_dila_"+`meters`+'m_orig_clump_pid'
    grass.mapcalc(espressao1, overwrite = True, quiet = True)
    espressao2=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_pid = if('+Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata > 0, '+Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata, null())'
    grass.mapcalc(espressao2, overwrite = True, quiet = True)
    
    nametxtreclass=rulesreclass(Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_pid', Form1.dirout)
    grass.run_command('r.reclass', input=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_pid', output=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_AreaHA', rules=nametxtreclass, overwrite = True)
    os.remove(nametxtreclass)
    
    if Form1.prepareBIODIM:
      #grass.run_command('r.out.gdal',input=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_pid',out=Listmapspatch+"_dila_"+`meters`+'m_clean_PID.tif')
      create_TXTinputBIODIM([Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_pid'], "simulados_HABMAT_grassclump_dila_"+`meters`+"m_clean_PID", Form1.dirout)
      create_TXTinputBIODIM([Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_AreaHA'], "simulados_HABMAT_grassclump_dila_"+`meters`+"m_clean_AREApix", Form1.dirout)      
      
      ########### calculando o area complete, exportanto ele e tb PID complete - precisa tambem gerar um area complete mesmo?
      nametxtreclass=rulesreclass(Listmapspatch+"_dila_"+`meters`+'m_orig_clump_pid', Form1.dirout)
      grass.run_command('r.reclass', input=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_pid', output=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_complete_AreaHA', rules=nametxtreclass, overwrite = True)
      os.remove(nametxtreclass)
      #grass.run_command('r.out.gdal', input=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_complete_AreaHA', out=Listmapspatch+"_dila_"+`meters`+'m_complete_AreaHA.tif')  
      #grass.run_command('r.out.gdal', input=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_pid', out=Listmapspatch+"_dila_"+`meters`+'m_complete_PID.tif')
      create_TXTinputBIODIM([Listmapspatch+"_dila_"+`meters`+'m_orig_clump_pid'], "simulados_HABMAT_grassclump_dila_"+`meters`+"m_complete_PID", Form1.dirout)
      create_TXTinputBIODIM([Listmapspatch+"_dila_"+`meters`+'m_orig_clump_complete_AreaHA'], "simulados_HABMAT_grassclump_dila_"+`meters`+"m_complete_AREApix", Form1.dirout)      
    else:
      grass.run_command('g.region', rast=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_AreaHA')
      grass.run_command('r.out.gdal', input=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_AreaHA', out=Listmapspatch+"_dila_"+`meters`+'m_clean_AreaHA.tif',overwrite = True)     
    
    if Form1.calcStatistics:
      createtxt(Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_pid', Form1.dirout, Listmapspatch+"_dila_"+`meters`+"m_clean_AreaHA") # clean
      createtxt(Listmapspatch+"_dila_"+`meters`+'m_orig_clump_pid', Form1.dirout, Listmapspatch+"_dila_"+`meters`+"m_complete_AreaHA") # complete
      
    if Form1.removeTrash:
      if Form1.prepareBIODIM:
        txts = [Listmapspatch+"_dila_"+`meters`+'m_orig', Listmapspatch+"_dila_"+`meters`+'m_orig_temp', Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata']
      else:
        txts = [Listmapspatch+"_dila_"+`meters`+'m_orig', Listmapspatch+"_dila_"+`meters`+'m_orig_temp', Listmapspatch+"_dila_"+`meters`+'m_orig_clump_pid', Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata']
      for txt in txts:
        grass.run_command('g.remove', type="raster", name=txt, flags='f')
           
    x=x+1

def areacon(Listmapspatch, prefix = ''):
  """
  Function for a series of maps
  This function calculates functional patch area in a map (CON), considering functional connectivity 
  (dilatation of edges given input scales/distances), and:
  - generates and exports maps with Patch ID and Area of each patch
  - generatics statistics - Area per patch (if Form1.calcStatistics == True)
  """
  
  if Form1.prepareBIODIM:
    esc, met = escala_con(Listmapspatch[0], Form1.escala_frag_con)
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
        pre_numb = "000"+`cont`
      elif cont <= 99:
        pre_numb = "00"+`cont`
      elif cont <= 999:        
        pre_numb = "0"+`cont`
      else: 
        pre_numb = `cont`
      
    i = prefix+pre_numb+'_'+i_in
    
    grass.run_command('g.region', rast=i_in)
    listescalafconM, listmeters = escala_con(i_in, Form1.escala_frag_con)
    
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
      nametxtreclass=rulesreclass(i+"_dila_"+`meters`+'m_orig_clump_mata_limpa_pid', Form1.dirout)
      grass.run_command('r.reclass', input=i+"_dila_"+`meters`+'m_orig_clump_mata_limpa_pid', output=i+"_dila_"+`meters`+'m_orig_clump_mata_limpa_AreaHA', rules=nametxtreclass, overwrite = True)
      os.remove(nametxtreclass)
      
      ############### no biodim eh HABMAT_grassclump_dila01_clean_AREApix.tif (ou complete, abaixo)
      ########## exportando o PID clean
      if Form1.prepareBIODIM:
        #grass.run_command('r.out.gdal', input=i+"_dila_"+`meters`+'m_orig_clump_mata_limpa_pid', out=i+"_dila_"+`meters`+'m_clean_PID.tif')
        lista_maps_pid_clean[z,x] = i+"_dila_"+`meters`+'m_orig_clump_mata_limpa_pid'
        lista_maps_area_clean[z,x] = i+"_dila_"+`meters`+'m_orig_clump_mata_limpa_AreaHA'        
        
        ########### calculando o area complete, exportanto ele e tb PID complete - precisa tambem gerar um area complete mesmo?
        nametxtreclass=rulesreclass(i+"_dila_"+`meters`+'m_orig_clump_pid', Form1.dirout)
        grass.run_command('r.reclass', input=i+"_dila_"+`meters`+'m_orig_clump_pid', output=i+"_dila_"+`meters`+'m_orig_clump_complete_AreaHA', rules=nametxtreclass, overwrite = True)
        os.remove(nametxtreclass)  
        #grass.run_command('r.out.gdal', input=i+"_dila_"+`meters`+'m_orig_clump_complete_AreaHA', out=i+"_dila_"+`meters`+'m_complete_AreaHA.tif')            
        #grass.run_command('r.out.gdal', input=i+"_dila_"+`meters`+'m_orig_clump_pid', out=i+"_dila_"+`meters`+'m_complete_PID.tif')
        lista_maps_pid_comp[z,x] = i+"_dila_"+`meters`+'m_orig_clump_pid'
        lista_maps_area_comp[z,x] = i+"_dila_"+`meters`+'m_orig_clump_complete_AreaHA'
  
      else:
        grass.run_command('g.region', rast=i+"_dila_"+`meters`+'m_orig_clump_mata_limpa_AreaHA')
        grass.run_command('r.out.gdal', input=i+"_dila_"+`meters`+'m_orig_clump_mata_limpa_AreaHA', out=i+"_dila_"+`meters`+'m_clean_AreaHA.tif',overwrite = True)
            
      if Form1.calcStatistics:
        createtxt(i+"_dila_"+`meters`+'m_orig_clump_mata_limpa_pid', Form1.dirout, i+"_dila_"+`meters`+"m_clean_AreaHA")
        createtxt(i+"_dila_"+`meters`+'m_orig_clump_pid', Form1.dirout, i+"_dila_"+`meters`+"m_complete_AreaHA")
      
      if Form1.removeTrash:
        if Form1.prepareBIODIM:
          txts = [i+"_dila_"+`meters`+'m_orig', i+"_dila_"+`meters`+'m_orig_temp', i+"_dila_"+`meters`+'m_orig_clump_mata']
        else:
          txts = [i+"_dila_"+`meters`+'m_orig', i+"_dila_"+`meters`+'m_orig_temp', i+"_dila_"+`meters`+'m_orig_clump_pid', i+"_dila_"+`meters`+'m_orig_clump_mata'] #, i+"_dila_"+`meters`+'m_orig_clump_mata_limpa_pid']
        for txt in txts:
          grass.run_command('g.remove', type='raster', name=txt, flags='f')
          
      x=x+1
    z=z+1
    cont += 1
    
  if Form1.prepareBIODIM:
    for i in range(len(met)):
      mm = int(met[i])
      create_TXTinputBIODIM(lista_maps_pid_clean[:,i].tolist(), "simulados_HABMAT_grassclump_dila_"+`mm`+"m_clean_PID", Form1.dirout)
      create_TXTinputBIODIM(lista_maps_area_clean[:,i].tolist(), "simulados_HABMAT_grassclump_dila_"+`mm`+"m_clean_AREApix", Form1.dirout)   

      create_TXTinputBIODIM(lista_maps_pid_comp[:,i].tolist(), "simulados_HABMAT_grassclump_dila_"+`mm`+"m_complete_PID", Form1.dirout)
      create_TXTinputBIODIM(lista_maps_area_comp[:,i].tolist(), "simulados_HABMAT_grassclump_dila_"+`mm`+"m_complete_AREApix", Form1.dirout)  
      
      
#----------------------------------------------------------------------------------
# Metrics for edge area (EDGE)

def mapcalcED(expressao):
  grass.mapcalc(expressao, overwrite = True, quiet = True)        

def create_EDGE_single(ListmapsED_in, escale_ed, dirs, prefix = ''):
  """
  Function for a single map
  This function separates habitat area into edge and interior/core regions, given a scale/distance defined as edge, and:
  - generates and exports maps with each region
  - generatics statistics - Area per region (matrix/edge/core) (if Form1.calcStatistics == True)
  """  
  
  ListmapsED = prefix+'_'+ListmapsED_in
  
  grass.run_command('g.region', rast=ListmapsED_in)
  listsize, listapoioname = escala_frag(ListmapsED_in, escale_ed)
  
  x=0
  for i in listsize:
    apoioname = int(listapoioname[x])  
    grass.run_command('r.neighbors', input=ListmapsED_in, output=ListmapsED+"_eroED_"+`apoioname`+'m', method='minimum', size=i, overwrite = True)
    inputs=ListmapsED+"_eroED_"+`apoioname`+'m,'+ListmapsED_in
    out=ListmapsED+'_EDGE'+`apoioname`+'m_temp1'
    grass.run_command('r.series', input=inputs, out=out, method='sum', overwrite = True)
    espressaoEd=ListmapsED+'_EDGE'+`apoioname`+'m_temp2 = int('+ListmapsED+'_EDGE'+`apoioname`+'m_temp1)'
    mapcalcED(espressaoEd)
    espressaoclip=ListmapsED+'_EDGE'+`apoioname`+'m= if('+ListmapsED_in+' >= 0, '+ListmapsED+'_EDGE'+`apoioname`+'m_temp2, null())'
    mapcalcED(espressaoclip)    
     
    grass.run_command('r.out.gdal', input=ListmapsED+'_EDGE'+`apoioname`+'m', out=ListmapsED+'_EDGE'+`apoioname`+'m.tif', overwrite = True) 
    
    if Form1.calcStatistics:
      createtxt(ListmapsED+'_EDGE'+`apoioname`+'m', dirs, out)
      
    if Form1.removeTrash:
      grass.run_command('g.remove', type="raster", name=ListmapsED+"_eroED_"+`apoioname`+'m,'+ListmapsED+'_EDGE'+`apoioname`+'m_temp1,'+ListmapsED+'_EDGE'+`apoioname`+'m_temp2', flags='f')
    
    x=x+1
    
    
def create_EDGE(ListmapsED, escale_ed, dirs, prefix = ''):
  """
  Function for a series of maps
  This function separates habitat area into edge and interior/core regions, given a scale/distance defined as edge, and:
  - generates and exports maps with each region
  - generatics statistics - Area per region (matrix/edge/core) (if Form1.calcStatistics == True)
  """
  
  cont = 1
  for i_in in ListmapsED:
    
    if prefix == '':
      pre_numb = ''
    else:
      if cont <= 9:
        pre_numb = "000"+`cont`
      elif cont <= 99:
        pre_numb = "00"+`cont`
      elif cont <= 999:        
        pre_numb = "0"+`cont`
      else: 
        pre_numb = `cont`    
    
    i = prefix+pre_numb+'_'+i_in
    
    grass.run_command('g.region', rast=i_in)
    listsize, listapoioname = escala_frag(i_in, escale_ed)
    
    x=0
    for a in listsize:
      apoioname = int(listapoioname[x])
      grass.run_command('r.neighbors', input=i_in, output=i+"_eroED_"+`apoioname`+'m', method='minimum', size=a, overwrite = True)
      inputs=i+"_eroED_"+`apoioname`+'m,'+i_in
      out=i+'_EDGE'+`apoioname`+'m_temp1'
      grass.run_command('r.series', input=inputs, out=out, method='sum', overwrite = True)
      espressaoEd=i+'_EDGE'+`apoioname`+'m_temp2= int('+i+'_EDGE'+`apoioname`+'m_temp1)'
      mapcalcED(espressaoEd)
      espressaoclip=i+'_EDGE'+`apoioname`+'m = if('+i_in+' >= 0, '+i+'_EDGE'+`apoioname`+'m_temp2, null())'
      mapcalcED(espressaoclip)
      grass.run_command('r.out.gdal', input=i+'_EDGE'+`apoioname`+'m', out=i+'_EDGE'+`apoioname`+'m.tif', overwrite = True)     
      
      if Form1.calcStatistics:
        createtxt(i+'_EDGE'+`apoioname`+'m', dirs, i+'_EDGE'+`apoioname`+'m_temp1')
      
      if Form1.removeTrash:
        grass.run_command('g.remove', type="raster", name=i+"_eroED_"+`apoioname`+'m,'+i+'_EDGE'+`apoioname`+'m_temp1,'+i+'_EDGE'+`apoioname`+'m_temp2', flags="f")
      
      x=x+1
      
    cont += 1
      

#----------------------------------------------------------------------------------
# Metrics for distance to edges
    
def dist_edge_Single(Listmapsdist_in, prefix = ''):
  """
  Function for a single map
  This function calculates the distance of each pixel to habitat edges, considering
  negative values (inside patches) and positive values (into the matrix). Also:
  - generates and exports maps of distance to edge (DIST)
  """

  Listmapsdist = prefix+'_'+Listmapsdist_in
  
  grass.run_command('g.region', rast=Listmapsdist_in)
  expression1=Listmapsdist+'_invert = if('+Listmapsdist_in+' == 0, 1, null())'
  grass.mapcalc(expression1, overwrite = True, quiet = True)
  grass.run_command('r.grow.distance', input=Listmapsdist+'_invert', distance=Listmapsdist+'_invert_forest_neg_eucldist',overwrite = True)
  expression2=Listmapsdist+'_invert_matrix = if('+Listmapsdist_in+' == 0, null(), 1)'
  grass.mapcalc(expression2, overwrite = True, quiet = True)
  grass.run_command('r.grow.distance', input=Listmapsdist+'_invert_matrix', distance=Listmapsdist+'_invert_matrix_pos_eucldist',overwrite = True)
  expression3=Listmapsdist+'_dist = '+Listmapsdist+'_invert_matrix_pos_eucldist-'+Listmapsdist+'_invert_forest_neg_eucldist'
  grass.mapcalc(expression3, overwrite = True, quiet = True)
  
  if Form1.prepareBIODIM:
    create_TXTinputBIODIM([Listmapsdist+'_dist'], "simulados_HABMAT_DIST", Form1.dirout)
  else:
    grass.run_command('r.out.gdal', input=Listmapsdist+'_dist', out=Listmapsdist+'_DIST.tif', overwrite = True)
    
  if Form1.removeTrash:
    txts = [Listmapsdist+'_invert', Listmapsdist+'_invert_forest_neg_eucldist', Listmapsdist+'_invert_matrix', Listmapsdist+'_invert_matrix_pos_eucldist']
    for txt in txts:
      grass.run_command('g.remove', type="raster", name=txt, flags='f')

def dist_edge(Listmapsdist, prefix = ''):
  """
  Function for a series of maps
  This function calculates the distance of each pixel to habitat edges, considering
  negative values (inside patches) and positive values (into the matrix). Also:
  - generates and exports maps of distance to edge (DIST)
  """

  if Form1.prepareBIODIM:
    lista_maps_dist=[]    
  
  cont = 1
  for i_in in Listmapsdist:
    
    if prefix == '':
      pre_numb = ''
    else:
      if cont <= 9:
        pre_numb = "000"+`cont`
      elif cont <= 99:
        pre_numb = "00"+`cont`
      elif cont <= 999:        
        pre_numb = "0"+`cont`
      else: 
        pre_numb = `cont`    

    i = prefix+pre_numb+'_'+i_in

    grass.run_command('g.region', rast=i_in)
    expression1=i+'_invert = if('+i_in+' == 0, 1, null())'
    grass.mapcalc(expression1, overwrite = True, quiet = True)
    grass.run_command('r.grow.distance', input=i+'_invert', distance=i+'_invert_forest_neg_eucldist',overwrite = True)
    expression2=i+'_invert_matrix = if('+i_in+' == 0, null(), 1)'
    grass.mapcalc(expression2, overwrite = True, quiet = True)
    grass.run_command('r.grow.distance', input=i+'_invert_matrix', distance=i+'_invert_matrix_pos_eucldist',overwrite = True)
    expression3=i+'_dist = '+i+'_invert_matrix_pos_eucldist-'+i+'_invert_forest_neg_eucldist'
    grass.mapcalc(expression3, overwrite = True, quiet = True)
    
    if Form1.prepareBIODIM:
      lista_maps_dist.append(i+'_dist')
    else:
      grass.run_command('r.out.gdal', input=i+'_dist', out=i+'_DIST.tif', overwrite = True)
      
    if Form1.removeTrash:
      txts = [i+'_invert', i+'_invert_forest_neg_eucldist', i+'_invert_matrix', i+'_invert_matrix_pos_eucldist']
      for txt in txts:
        grass.run_command('g.remove', type="raster", name=txt, flags='f')
    
    cont += 1
    
  if Form1.prepareBIODIM:
    create_TXTinputBIODIM(lista_maps_dist, "simulados_HABMAT_DIST", Form1.dirout)
    

#----------------------------------------------------------------------------------
# GUI

class Form1(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)
        
        #variavels_______________________________________
        Form1.mapa_entrada=''
        Form1.Patch=False
        Form1.Frag=False
        Form1.Cone=False
        Form1.Dist=False
        Form1.Habmat=False
        Form1.background_filename=[]
        
        ###########################
        Form1.removeTrash=True
        Form1.prepareBIODIM=False
        Form1.calcStatistics=False
        Form1.list_habitat_classes=[]
        
        Form1.size = 450
        Form1.hsize = 450
        
        Form1.formcalculate='Multiple'
        Form1.species_profile_group=''
        Form1.speciesList=[]
        Form1.species_profile=''
        Form1.petternmaps=''
        Form1.start_raio=0
        
        Form1.label_prefix=''
        Form1.RegularExp=''
        Form1.listMapsPng=[]
        Form1.listMapsPngAux=[]
        Form1.contBG=0
        Form1.plotmaps=0
        Form1.lenlistpng=0  
        
        Form1.ListmapsPatch=[]
        Form1.ListMapsGroupCalc=[]
        Form1.escala_frag_con=''
        Form1.escala_ED=''
        Form1.dirout=''
        Form1.chebin=''
        Form1.checEDGE=''
        
        
        
        
        #________________________________________________

        if Form1.prepareBIODIM: 
          Form1.speciesList=grass.list_grouped ('rast') ['userbase']
        else:
          Form1.speciesList=grass.list_grouped ('rast') ['PERMANENT']
        
        #____________________________________________________________________________
        


        Form1.dirout=selectdirectory()
        
        Form1.output_prefix2=''

        self.quote = wx.StaticText(self, id=-1, label="LandScape Connectivity", pos=wx.Point(20, 20))
        
        font = wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD)
        self.quote.SetForegroundColour("blue")
        self.quote.SetFont(font)

        #____________________________________________________________________________
        
        # A multiline TextCtrl - This is here to show how the events work in this program, don't pay too much attention to it
        #caixa de mensagem
        self.logger = wx.TextCtrl(self,5, '',wx.Point(20,350), wx.Size(340,120),wx.TE_MULTILINE | wx.TE_READONLY)
        
        self.editname = wx.TextCtrl(self, 190, '', wx.Point(160, 82),
                                    wx.Size(100,-1)) #Regular expression
        self.editname = wx.TextCtrl(self, 191, '', wx.Point(270,200), wx.Size(80,-1)) #escala
        self.editname = wx.TextCtrl(self, 192, '', wx.Point(270,225), wx.Size(80,-1)) #borda
        self.editname = wx.TextCtrl(self, 193, '', wx.Point(270,318), wx.Size(80,-1)) #habitat maps
        
        wx.EVT_TEXT(self, 190, self.EvtText)
        wx.EVT_TEXT(self, 191, self.EvtText)
        wx.EVT_TEXT(self, 192, self.EvtText)
        wx.EVT_TEXT(self, 193, self.EvtText)
        #____________________________________________________________________________
        # A button
        self.button =wx.Button(self, 10, "START CALCULATIONS", wx.Point(20, 480))
        wx.EVT_BUTTON(self, 10, self.OnClick)
        self.button =wx.Button(self, 8, "EXIT", wx.Point(270, 480))
        wx.EVT_BUTTON(self, 8, self.OnExit)        
        #self.button =wx.Button(self, 9, "change Map", wx.Point(280, 295))
        #wx.EVT_BUTTON(self, 9, self.OnClick) 
        
        #self.button =wx.Button(self, 11, "TXT RULES", wx.Point(283,260))
        #wx.EVT_BUTTON(self,11, self.OnClick)        

        #____________________________________________________________________________
        ##------------ LElab_logo
        imageFile = 'logo_lab.png'
        im1 = Image.open(imageFile)
        jpg1 = wx.Image(imageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        wx.StaticBitmap(self, -1, jpg1, (20,190), (jpg1.GetWidth(), jpg1.GetHeight()), style=wx.SUNKEN_BORDER)
        
       

       #______________________________________________________________________________________________________________
       #static text
        
        self.SelecMetrcis = wx.StaticText(self,-1,"Choose Metric:", wx.Point(15,150))
        
        
        self.SelecMetrcis = wx.StaticText(self,-1,"Calculate Statistics:", wx.Point(180,260))
        self.SelecMetrcis = wx.StaticText(self,-1,"Create Distance Map:", wx.Point(180,280))
        self.SelecMetrcis = wx.StaticText(self,-1,"Create Habitat Map:", wx.Point(180,300))
        self.SelecMetrcis = wx.StaticText(self,-1,"Codes for habitat:", wx.Point(180,320))
        self.SelecMetrcis = wx.StaticText(self,-1,"Regular Expression:", wx.Point(165, 62))
        self.SelecMetrcis = wx.StaticText(self,-1,"List Scale Unit(m):", wx.Point(180,200))
        self.SelecMetrcis = wx.StaticText(self,-1,"List Edge Unit(m):", wx.Point(180,228))
        
        wx.EVT_TEXT(self, 185, self.EvtText)
        
        
        #______________________________________________________________________________________________________________
        
        
        #______________________________________________________________________________________________________________
        # Checkbox

        self.insure = wx.CheckBox(self, 96, "AH Patch.", wx.Point(90,150))
        wx.EVT_CHECKBOX(self, 96,   self.EvtCheckBox)     
        
        self.insure = wx.CheckBox(self, 95, "AH Frag.", wx.Point(160,150))
        wx.EVT_CHECKBOX(self, 95,   self.EvtCheckBox)   
        
        self.insure = wx.CheckBox(self, 97, "AH Con.", wx.Point(230,150))
        wx.EVT_CHECKBOX(self, 97,   self.EvtCheckBox)  
        
        self.insure = wx.CheckBox(self, 150, "EDGE", wx.Point(295,150))
        wx.EVT_CHECKBOX(self, 150,   self.EvtCheckBox)        
        
        """
        essa funcao a baixo eh o botao para saber se vai ou nao calcular a statistica para os mapas
        """
        self.insure = wx.CheckBox(self, 98, "", wx.Point(290,260)) # Form1.calcStatistics botaozainho da statisica
        wx.EVT_CHECKBOX(self, 98,   self.EvtCheckBox)  
        
        
        """
        essa funcao a baixo eh o botao para saber se vai ou nao calcular o mapa de distancia euclidiana
        """
        self.insure = wx.CheckBox(self, 99, "", wx.Point(290,280)) # Form1.Distedge botaozainho da distancia em relacao a borda
        wx.EVT_CHECKBOX(self, 99,   self.EvtCheckBox)  
        
        
        """
        essa funcao a baixo eh o botao para saber se vai ou nao calcular o mapa de distancia euclidiana
        """
        self.insure = wx.CheckBox(self, 100, "", wx.Point(290,300)) # Criando mapa de habitat botaozainho Form1.Habmat
        wx.EVT_CHECKBOX(self, 100,   self.EvtCheckBox)          
        
            
        
        #______________________________________________________________________________________________________________
        #Radio Boxes
        self.dispersiveList = ['Multiple', 'Single',          ]
        rb = wx.RadioBox(self, 92, "Choose form calculate", wx.Point(20, 62), wx.DefaultSize,
                        self.dispersiveList, 2, wx.RA_SPECIFY_COLS)
        wx.EVT_RADIOBOX(self, 92, self.EvtRadioBox)
        
        
        # radio boxes para saber se vai cacular pro BIODIM ou Nao
        self.BioDimChosse = ['No', 'Yes',          ]
        rb = wx.RadioBox(self, 905, "Calc. For BioDim", wx.Point(275, 62), wx.DefaultSize,
                         self.BioDimChosse, 2, wx.RA_SPECIFY_COLS)
        wx.EVT_RADIOBOX(self, 905, self.EvtRadioBox)        
        
        
        #______________________________________________________________________________________________________________ 
        #backgroun inicial
        Form1.background_filename=['Pai10.png']
        Form1.background_filename_start=Form1.background_filename[0]
                                
                                                          
        img =Image.open(Form1.background_filename[0])
      
        # redimensionamos sem perder a qualidade
        img = img.resize((Form1.size,Form1.hsize),Image.ANTIALIAS)
        img.save(Form1.background_filename[0])        
      
      
        imageFile=Form1.background_filename[0]
        im1 = Image.open(imageFile)
        jpg1 = wx.Image(imageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        wx.StaticBitmap(self, -1, jpg1, (380,40), (jpg1.GetWidth(),  jpg1.GetHeight()), style=wx.SIMPLE_BORDER)        
 
    def EvtRadioBox(self, event):
      if event.GetId()==905:
        Form1.prepareBIODIM=event.GetString()
        print Form1.prepareBIODIM
        if Form1.prepareBIODIM=="No":
          Form1.prepareBIODIM=False
        else:
          Form1.prepareBIODIM=True
          
      if Form1.prepareBIODIM:        
        Form1.speciesList=grass.list_grouped ('rast') ['userbase']
      else:
        Form1.speciesList=grass.list_grouped ('rast') ['PERMANENT']      
      
      if event.GetId()==92:
        Form1.formcalculate=event.GetString()
        print Form1.formcalculate
        if Form1.formcalculate=="Single":
          
          Form1.species_profile=Form1.speciesList[0] 
          self.SelcMap = wx.StaticText(self,-1,"Selec Map:",wx.Point(20, 120))
          #______________________________________________________________________________________________________
          Form1.editspeciesList=wx.ComboBox(self, 93, Form1.species_profile, wx.Point(80, 120), wx.Size(280, -1),
                                            Form1.speciesList, wx.CB_DROPDOWN)
          wx.EVT_COMBOBOX(self, 93, self.EvtComboBox)
          wx.EVT_TEXT(self, 93, self.EvtText)          
          #______________________________________________________________________________________________________
        else:
          self.Refresh()
        
        
       # self.logger.AppendText('Dispersive behaviour: %s\n' % )
     
     
     
     
    #______________________________________________________________________________________________________    
    def EvtComboBox(self, event):
        if event.GetId()==93:   #93==Species Profile Combo box
            Form1.mapa_entrada=event.GetString()
            self.logger.AppendText('Map : %s' % event.GetString())
        else:
            self.logger.AppendText('EvtComboBox: NEED TO BE SPECIFIED' )
            
            


        
    #______________________________________________________________________________________________________   
    def OnClick(self,event):
        #self.logger.AppendText(" Click on object with Id %d\n" %event.GetId())
        
        #______________________________________________________________________________________________________________ 
        if event.GetId()==10:   #10==START
          
          os.chdir(Form1.dirout)
          
          if Form1.formcalculate=="Single":
            
            if Form1.prepareBIODIM:
              Form1.output_prefix2 = 'lndscp_0001'            
            
            if Form1.Habmat: ############ adicionei isso aqui: talvez temos que aplicar as outras funcoes ja nesse mapa?
              ###### as outras funcoes precisam de um mapa binario de entrada? ou pode ser so um mapa habitat/null?
              create_habmat_single(Form1.mapa_entrada, prefix = Form1.output_prefix2)            
            if Form1.Patch==True:   
              patchSingle(Form1.mapa_entrada, prefix = Form1.output_prefix2)
            if Form1.Frag==True:
              areaFragSingle(Form1.mapa_entrada, prefix = Form1.output_prefix2)
            if Form1.Cone==True:
              areaconSingle(Form1.mapa_entrada, prefix = Form1.output_prefix2)
            if Form1.checEDGE==True:
              create_EDGE_single(Form1.mapa_entrada, Form1.escala_ED, Form1.dirout, prefix = Form1.output_prefix2)
            if Form1.Dist==True:
              dist_edge_Single(Form1.mapa_entrada, prefix = Form1.output_prefix2)
            
          else:
                      
            if Form1.prepareBIODIM:
              Form1.ListMapsGroupCalc=grass.list_grouped ('rast', pattern=Form1.RegularExp) ['userbase']
              Form1.output_prefix2 = 'lndscp_'              
            else:
              Form1.ListMapsGroupCalc=grass.list_grouped ('rast', pattern=Form1.RegularExp) ['PERMANENT']   
              
            if Form1.Habmat: ############ adicionei isso aqui: talvez temos que aplicar as outras funcoes ja nesse mapa?
              ###### as outras funcoes precisam de um mapa binario de entrada? ou pode ser so um mapa habitat/null?
              create_habmat(Form1.ListMapsGroupCalc, prefix = Form1.output_prefix2)            
            if Form1.Patch==True:
              Form1.ListmapsPatch=Patch(Form1.ListMapsGroupCalc, prefix = Form1.output_prefix2) ####### john precisa atribuir isso aqui?
            if Form1.Frag==True:
              areaFrag(Form1.ListMapsGroupCalc, prefix = Form1.output_prefix2)
            if Form1.Cone==True:
              areacon(Form1.ListMapsGroupCalc, prefix = Form1.output_prefix2) 
            if Form1.checEDGE==True:
              create_EDGE(Form1.ListMapsGroupCalc, Form1.escala_ED, Form1.dirout, prefix = Form1.output_prefix2)
            if Form1.Dist==True:
              dist_edge(Form1.ListMapsGroupCalc, prefix = Form1.output_prefix2)
            
               
        
        #______________________________________________________________________________________________________________ 
        if event.GetId()==9:   #9==CHANGE BACKGROUND
          if Form1.plotmaps==1:
            if Form1.formcalculate=="Single":
              x=1
            else:
              self.Refresh()
              Form1.background_filename=Form1.listMapsPng
              Form1.background_filename_start=Form1.background_filename[Form1.contBG]   
              img =Image.open(Form1.background_filename[Form1.contBG])
            
              # redimensionamos sem perder a qualidade
              img = img.resize((Form1.size,Form1.hsize),Image.ANTIALIAS)
              img.save(Form1.background_filename[Form1.contBG])        
            
            
              imageFile=Form1.background_filename[Form1.contBG]
              im1 = Image.open(imageFile)
              jpg1 = wx.Image(imageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
              wx.StaticBitmap(self, -1, jpg1, (380,40), (jpg1.GetWidth(),  jpg1.GetHeight()), style=wx.SIMPLE_BORDER)
                                
              Form1.background_filename=Form1.background_filename_start
              Form1.contBG=Form1.contBG+1
              self.Refresh() 
              if len(Form1.listMapsPng)==Form1.contBG:
                Form1.contBG=0      
                self.Refresh() 
              #______________________________________________________________________________________________________________ 
        if event.GetId()==11:   
          if Form1.chebin==True:
            if  Form1.formcalculate=="Single":
              createBinarios_single(Form1.mapa_entrada)
            else:
              
              if Form1.prepareBIODIM:
                Form1.ListMapsGroupCalc=grass.list_grouped ('rast', pattern=Form1.RegularExp) ['userbase']
              else:
                Form1.ListMapsGroupCalc=grass.list_grouped ('rast', pattern=Form1.RegularExp) ['PERMANENT']                
              
              createBinarios(Form1.ListMapsGroupCalc)
          
          
        
        
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
          Form1.RegularExp=event.GetString() 
          
        if event.GetId()==191:
          Form1.escala_frag_con=event.GetString()
          
        if event.GetId()==192:
          Form1.escala_ED=event.GetString()    
          
        if event.GetId()==193:
          list_habitat=event.GetString()
          Form1.list_habitat_classes=list_habitat.split(',')
          #Form1.list_habitat_classes=[int(i) for i in list_habitat.split(',')] # we do not have to transform in integers - command run already in strings, for passing it to GRASS

    #______________________________________________________________________________________________________
    def EvtCheckBox(self, event):
        #self.logger.AppendText('EvtCheckBox: %d\n' % event.Checked())
        if event.GetId()==95:
            if event.Checked()==1:
                Form1.Frag=True
                self.logger.AppendText('EvtCheckBox:\nMetric Selected: Frag \n')
            else:
                Form1.Frag=False
                self.logger.AppendText('EvtCheckBox: \nMetric Not Selected: Frag \n')
                
                
        if event.GetId()==96:
          if event.Checked()==1:
            Form1.Patch=True
            self.logger.AppendText('EvtCheckBox:\nMetric Selected: Patch \n')
          else:
            Form1.Patch=False
            self.logger.AppendText('EvtCheckBox:\nMetric Not Selected: Patch \n')
                   
            
        if event.GetId()==97:
          if event.Checked()==1:
            Form1.Cone=True
            self.logger.AppendText('EvtCheckBox:\nMetric Selected: Connectivity \n')
          else:
            Form1.Cone=False
            self.logger.AppendText('EvtCheckBox:\nMetric Not Selected: Connectivity \n')
                         
        
        if event.GetId()==98: #criando txtx de statitiscas
          if int(event.Checked())==1: 
            Form1.calcStatistics=True           
            self.logger.AppendText('EvtCheckBox:\nCalculate connectivity statistics: '+`Form1.calcStatistics`+' \n')
            
            
            
        if event.GetId()==99: #criando mapa de distancia 
          if int(event.Checked())==1:
            Form1.Dist=True
            self.logger.AppendText('EvtCheckBox:\n Create Distance map: '+`Form1.Dist`+' \n')
            
        if event.GetId()==100:
          if int(event.Checked())==1:
            Form1.Habmat=True
            self.logger.AppendText('EvtCheckBox:\nCreate Habitat Map '+`Form1.Dist`+' \n')
        
            
        if event.GetId()==150: #check EDGE
          if int(event.Checked())==1:
            Form1.checEDGE=True
            self.logger.AppendText('EvtCheckBox:\nMetric Selected: Edge \n')
          else:
            Form1.checEDGE=False
            self.logger.AppendText('EvtCheckBox:\nMetric Not Selected: Edge \n')
            
        ################
        # CRIAR UM BOTAO E UM EVENTO DESSES AQUI, PARA O MAPA DE DIST (mesmo que ele so seja usado para o biodim)
         
            
    #______________________________________________________________________________________________________
    def OnExit(self, event):
        d= wx.MessageDialog( self, " Thanks for using LS Connectivity! \n"
                            " ","Good bye", wx.OK)
                            # Create a message dialog box
        d.ShowModal() # Shows it
        d.Destroy() # finally destroy it when finished.
        frame.Close(True)  # Close the frame. 

#----------------------------------------------------------------------
#......................................................................
#----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.PySimpleApp()
    frame = wx.Frame(None, -1, " ", size=(870,550))
    Form1(frame,-1)
    frame.Show(1)
    
    app.MainLoop()
