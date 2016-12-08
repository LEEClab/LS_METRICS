#!/c/Python25 python
#---------------------------------------------------------------------------------------
"""
 LS Connectivity - Landscape connectivity calculator
 Version 0.9
 
 John W. Ribeiro - jw.ribeiro.rc@gmail.com
 Bernardo B. S. Niebuhr - bernardo_brandaum@yahoo.com.br
 Milton C. Ribeiro - mcr@rc.unesp.br
 
 Laboratorio de Ecologia Espacial e Conservacao
 Universidade Estadual Paulista - UNESP
 Rio Claro - SP - Brasil
 
 Aqui podemos colocar mais comentarios sobre o funcionamento do LS Con...
"""
#---------------------------------------------------------------------------------------

import sys, os, numpy #sys, os, PIL, numpy, Image, ImageEnhance
import grass.script as grass
from PIL import Image
import wx
import random
import re
import time
import math
#from rpy2 import robjects
from datetime import tzinfo, timedelta, datetime
import win32gui
from win32com.shell import shell, shellcon

ID_ABOUT=101
ID_IBMCFG=102
ID_EXIT=110

########################
# 1) que estranho!!! o patch da mais manchas que o frag!! sera que eh porque perdemos manchas pequenas?
# Resposta: Sim pq o frag elimina corredores, com isso algumas manchas acabam sumindo eh normal.
# ao mesmo tempo, separamos manchas que antes estavam juntas, o que pode aumentar...
# 2) entender bem o patch!!



# ideia: transformar o pid patch e pid frag, reclass em 1 e 0; e ai comparar ambos...
# 3) funcao createtxt
# tres botoes: (tem que transformar em botoes) 
# - joga o trash fora ou nao (talvez nao pecise ser um botao...) - para deletar rasters auxiliares criados
#     concordo

# - statistics: gera arquivos de texto com as estatisticas ou nao
# - biodim: prepara arquivos para o biodim (como PIDs, varias areas etc ou nao)

# ver duvida sobre as funcoes de escala - tem diff? Sim tem sim.

# pensar em mudar o nome dos arquivos finais - podemos colocar so um conjunto de renames, ou usar nomes diferentes mesmo no fim
# pra bater com o biodim e pra ficar mais facil de entender
# qual eh o melhor padrao de nome?

# -adicionar funcao para dist edge OK
# -arrumar script R para gerar as figuras que queremos
# como conversa o R com o grass? da pra rodar o script R em BATCH mode?

#----------------------------------------------------------------------------------
# Output for statistics
 
class GrassFunctions(object):
  def __init__(self):
    
    #---------- Variable function of creating txt-------------------
    self.maps=''
    self.dirs=''
    self.outname=False
    #---------- ----------------------------------------------------
    
    def createtxt(self):
      """
      This function creates a text file with:
      - Values of area, in hectares, for edge, interior and core areas (for EDGE metrics)
      - Calues of area, in hectares, for each patch (for PATCH, FRAG and CON metrics)
      Juliana+Ber teste
      """
      x=grass.read_command('r.stats',flags='a',input=self.maps)
      y=x.split('\n')
      os.chdir(self.dirs)
      if self.outname:
        txtsaida=self.outname+'.txt'
      else:
        txtsaida=self.maps+'.txt'
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

def selecdirectori():
  """
  This function opens a window for the user to select a folder or file
  """
  mydocs_pidl = shell.SHGetFolderLocation (0, shellcon.CSIDL_DESKTOP, 0, 0)
  pidl, display_name, image_list = shell.SHBrowseForFolder (
    win32gui.GetDesktopWindow (),
    mydocs_pidl,
    "Select a file or folder",
    shellcon.BIF_BROWSEINCLUDEFILES,
    None,
    None
  )
  
  if (pidl, display_name, image_list) == (None, None, None):
    print "Nothing selected"
  else:
    path = shell.SHGetPathFromIDList (pidl)
    #print "Opening", #path
    a=(path)
  
  return a

def createBinarios_single(ListMapBins):
  """
  This function reclassify an input map into a binary map, according to reclassification rules passed by
  a text file
  """
  readtxt=selecdirectori()
  grass.run_command('g.region',rast=ListMapBins)
  grass.run_command('g.region',rast=ListMapBins)
  grass.run_command('r.reclass',input=ListMapBins,output=ListMapBins+'_bin',rules=readtxt, overwrite = True)
  Form1.speciesList=grass.mlist_grouped ('rast', pattern='(*)') ['PERMANENT']
  return readtxt
  
def createBinarios(ListMapBins):
  """
  This function reclassify a series of input maps into binary maps, according to reclassification rules passed by
  a text file
  """
  readtxt=selecdirectori()
  for i in ListMapBins:
    grass.run_command('g.region',rast=i)
    grass.run_command('g.region',rast=i)
    grass.run_command('r.reclass',input=i,output=i+'_bin',rules=readtxt, overwrite = True)
    Form1.speciesList=grass.mlist_grouped ('rast', pattern='(*)') ['PERMANENT']
    return readtxt

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

# precisa das duas?
# na pratica as escala_frag ta sendo usada para FRAG (com parm Form1.escala_frag) e para EDGE (com parm Form1.escala_ed)
# Sim essa escala funciona para os dois, acho que podemos renomear essa funcao.

# e escala_con esta sendo usada para CON (mas com parm Form1.escala_frag)
# eh isso mesmo?!!?
def escala_con(mapa,esc):
  """
  This function separates the input for functional connectivity maps (CON), separatins scales (distances)
  which will be used to generate the maps. Also, it defines the numbers of pixels to consider, besides distances
  ############# EH ISSO?
  """
  esclist=esc.split(',')
  res=grass.read_command('g.region',rast=mapa,flags='m')
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
  res=grass.read_command('g.region',rast=mapa,flags='m')
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
# Metrics for fragmented (excluding edges) views of landscapes (FRAG)

def areaFragSingle(ListmapsFrag):
  """
  Function for a single map
  This function fragments patches (FRAG), excluding corridors and edges given input scales (distances), and:
  - generates and exports maps with Patch ID and Area of each "fragmented" patch
  - generatics statistics - Area per patch (if Form1.calcStatistics == True)
  """
  grass.run_command('g.region',rast=ListmapsFrag)
  Lista_escalafragM,listmeters=escala_frag(ListmapsFrag,Form1.escala_frag)
  x=0
  for a in Lista_escalafragM:
    meters=int(listmeters[x])  
    #print escalafragM
    grass.run_command('r.neighbors',input=ListmapsFrag,output=ListmapsFrag+"_ero_"+`meters`+'m',method='minimum',size=a,overwrite = True)
    grass.run_command('r.neighbors',input=ListmapsFrag+"_ero_"+`meters`+'m',output=ListmapsFrag+"_dila_"+`meters`+'m',method='maximum',size=a,overwrite = True)
    expressao1=ListmapsFrag+"_FRAG"+`meters`+"m_mata=if("+ListmapsFrag+"_dila_"+`meters`+'m'+">0,"+ListmapsFrag+"_dila_"+`meters`+'m'+",null())"
    grass.mapcalc(expressao1, overwrite = True, quiet = True)
    expressao2=ListmapsFrag+"_FRAG"+`meters`+"m_mata_lpo=if("+ListmapsFrag+">=0,"+ListmapsFrag+"_FRAG"+`meters`+"m_mata,null())"
    grass.mapcalc(expressao2, overwrite = True, quiet = True)
    grass.run_command('r.clump',input=ListmapsFrag+"_FRAG"+`meters`+"m_mata_lpo",output=ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump",overwrite = True)
    
    grass.run_command('g.region',rast=ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump")
    nametxtreclass=rulesreclass(ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump",Form1.dirout)
    grass.run_command('r.reclass',input=ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump",output=ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_AreaHA",rules=nametxtreclass, overwrite = True)    
    grass.run_command('g.region',rast=ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_AreaHA")
    grass.run_command('r.out.gdal',input=ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_AreaHA",out=ListmapsFrag+"_FRAG"+`meters`+"m_AreaHA.tif")
    #### no biodim isso eh ...AREApix.tif... devemos mudar aqui ou la? devemos mudar os nomes internos aqui tb? acho que sim...
    if Form1.prepareBIODIM:
      grass.run_command('r.out.gdal',input=ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump",out=ListmapsFrag+"_FRAG"+`meters`+"m_PID.tif")
    os.remove(nametxtreclass)
    
    if Form1.calcStatistics:
      createtxt(ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump", Form1.dirout, ListmapsFrag+"_FRAG"+`meters`+"m_AreaHA")        
    
    if Form1.removeTrash:
      if Form1.prepareBIODIM:
        txts = [ListmapsFrag+"_ero_"+`meters`+'m', ListmapsFrag+"_dila_"+`meters`+'m', ListmapsFrag+"_FRAG"+`meters`+"m_mata", ListmapsFrag+"_FRAG"+`meters`+"m_mata_lpo"]
      else:
        txts = [ListmapsFrag+"_ero_"+`meters`+'m', ListmapsFrag+"_dila_"+`meters`+'m', ListmapsFrag+"_FRAG"+`meters`+"m_mata", ListmapsFrag+"_FRAG"+`meters`+"m_mata_lpo", ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump"]
      for txt in txts:
        grass.run_command('g.remove', rast=txt, flags = "f")
    x=x+1

def areaFrag(ListmapsFrag):
  """
  Function for a series of maps
  This function fragments patches (FRAG), excluding corridors and edges given input scales (distances), and:
  - generates and exports maps with Patch ID and Area of each "fragmented" patch
  - generatics statistics - Area per patch (if Form1.calcStatistics == True)
  """

  #erodindo
  for i in ListmapsFrag:
    grass.run_command('g.region',rast=i)
    Lista_escalafragM,listmeters=escala_frag(i,Form1.escala_frag)
        #print escalafragM
    x=0
    for a in Lista_escalafragM:
      meters=int(listmeters[x])
      #print a
      grass.run_command('r.neighbors',input=i,output=i+"_ero_"+`meters`+'m',method='minimum',size=a,overwrite = True)
      grass.run_command('r.neighbors',input=i+"_ero_"+`meters`+'m',output=i+"_dila_"+`meters`+'m',method='maximum',size=a,overwrite = True)
      expressao1=i+"_FRAG"+`meters`+"m_mata=if("+i+"_dila_"+`meters`+'m'+">0,"+i+"_dila_"+`meters`+'m'+",null())"
      grass.mapcalc(expressao1, overwrite = True, quiet = True)
      expressao2=i+"_FRAG"+`meters`+"m_mata_lpo=if("+i+">=0,"+i+"_FRAG"+`meters`+"m_mata,null())"
      grass.mapcalc(expressao2, overwrite = True, quiet = True)      
      grass.run_command('r.clump',input=i+"_FRAG"+`meters`+"m_mata_lpo",output=i+"_FRAG"+`meters`+"m_mata_clump",overwrite = True)
      grass.run_command('g.region',rast=i+"_FRAG"+`meters`+"m_mata_clump")
      nametxtreclass=rulesreclass(i+"_FRAG"+`meters`+"m_mata_clump",Form1.dirout)
      grass.run_command('r.reclass',input=i+"_FRAG"+`meters`+"m_mata_clump",output=i+"_FRAG"+`meters`+"m_mata_clump_AreaHA",rules=nametxtreclass, overwrite = True)    
      grass.run_command('g.region',rast=i+"_FRAG"+`meters`+"m_mata_clump_AreaHA")
      grass.run_command('r.out.gdal',input=i+"_FRAG"+`meters`+"m_mata_clump_AreaHA",out=i+"_FRAG"+`meters`+"m_AreaHA.tif")
      if Form1.prepareBIODIM:    
        grass.run_command('r.out.gdal',input=i+"_FRAG"+`meters`+"m_mata_clump",out=i+"_FRAG"+`meters`+"m_PID.tif")
      os.remove(nametxtreclass)
      
      if Form1.calcStatistics:      
        createtxt(i+"_FRAG"+`meters`+"m_mata_clump", Form1.dirout, i+"_FRAG"+`meters`+"m_AreaHA")
      
      if Form1.removeTrash:
        if Form1.prepareBIODIM:
          txts = [i+"_ero_"+`meters`+'m', i+"_dila_"+`meters`+'m', i+"_FRAG"+`meters`+"m_mata", i+"_FRAG"+`meters`+"m_mata_lpo"]
        else:        
          txts = [i+"_ero_"+`meters`+'m', i+"_dila_"+`meters`+'m', i+"_FRAG"+`meters`+"m_mata", i+"_FRAG"+`meters`+"m_mata_lpo", i+"_FRAG"+`meters`+"m_mata_clump"]
        for txt in txts:
          grass.run_command('g.remove', rast=txt, flags = "f")
      x=x+1

#----------------------------------------------------------------------------------
# Metrics for patch size/area/ID (PATCH)

def patchSingle(Listmapspatch):
  """
  Function for a single map
  This function calculates area per patch in a map (PATCH), considering structural connectivity 
  (no fragmentation or dilatation):
  - generates and exports maps with Patch ID and Area of each patch
  - generatics statistics - Area per patch (if Form1.calcStatistics == True)
  """
  
  #print Listmapspatch
  #expression1="MapaBinario="+Listmapspatch
  #grass.mapcalc(expression1, overwrite = True, quiet = True)    
  #grass.run_command('g.region',rast="MapaBinario")
  #expression2="A=MapaBinario"
  #grass.mapcalc(expression2, overwrite = True, quiet = True)
  
  ###r.colors map=A color=wave
  #grass.run_command('g.region',rast="MapaBinario")
  #expression3="MapaBinario_A=if(A[0,0]==0 && A[0,-1]==1 && A[1,-1]==0 && A[1,0]==1,1,A)"
  #grass.mapcalc(expression3, overwrite = True, quiet = True)
  #expression4="A=MapaBinario_A"
  #grass.mapcalc(expression4, overwrite = True, quiet = True)
  #expression5="MapaBinario_AB=if(A[0,0]==0 && A[-1,0]==1 && A[-1,1]==0 && A[0,1]==1,1,A)"
  #grass.mapcalc(expression5, overwrite = True, quiet = True) 
  #expression6="A=MapaBinario_AB"
  #grass.mapcalc(expression6, overwrite = True, quiet = True)
  #expression7="MapaBinario_ABC=if(A[0,0]==0 && A[0,1]==1 && A[1,1]==0 && A[1,0]==1,1,A)"
  #grass.mapcalc(expression7, overwrite = True, quiet = True)
  #expression8="A=MapaBinario_ABC"
  #grass.mapcalc(expression8, overwrite = True, quiet = True)
  #expression9="MapaBinario_ABCD=if(A[0,0]==0 && A[1,0]==1 && A[1,1]==0 && A[0,1]==1,1,A)"
  #grass.mapcalc(expression9, overwrite = True, quiet = True)
  #expression10="A=MapaBinario_ABCD"
  #grass.mapcalc(expression10, overwrite = True, quiet = True)
  #expression11=Listmapspatch+"_patch=A"
  #grass.mapcalc(expression11, overwrite = True, quiet = True)
  ##r.colors map=$i"_patch" color=random
  grass.run_command('g.region',rast=Listmapspatch)
  grass.run_command('r.clump',input=Listmapspatch,output=Listmapspatch+"_patch_clump",overwrite = True)
  ########## essa proxima linha muda algo?? clump * mata/nao-mata  
  expression12=Listmapspatch+"_patch_clump_mata="+Listmapspatch+"_patch_clump*"+Listmapspatch
  grass.mapcalc(expression12, overwrite = True, quiet = True)
  expression13=Listmapspatch+"_patch_clump_mata_limpa=if("+Listmapspatch+"_patch_clump_mata>0,"+Listmapspatch+"_patch_clump_mata,null())"
  grass.mapcalc(expression13, overwrite = True, quiet = True)
  ##r.colors map=$i"_patch_clump_mata_limpa" color=random
  nametxtreclass=rulesreclass(Listmapspatch+"_patch_clump_mata_limpa",Form1.dirout)
  grass.run_command('r.reclass',input=Listmapspatch+"_patch_clump_mata_limpa",output=Listmapspatch+"_patch_clump_mata_limpa_AreaHA",rules=nametxtreclass,overwrite = True)
  #grass.run_command('g.remove',flags='f',rast='A,MapaBinario,MapaBinario_A,MapaBinario_AB,MapaBinario_ABC,MapaBinario_ABCD')
  grass.run_command('g.region',rast=Listmapspatch+"_patch_clump_mata_limpa_AreaHA")
  grass.run_command('r.out.gdal',input=Listmapspatch+"_patch_clump_mata_limpa_AreaHA",out=Listmapspatch+"_patch_AreaHA.tif")
  ############## no biodim esta como ...HABMAT_grassclump_AREApix.tif devemos mudar??
  if Form1.prepareBIODIM:
    grass.run_command('r.out.gdal',input=Listmapspatch+"_patch_clump_mata_limpa",out=Listmapspatch+"_patch_PID.tif")
  ############## no biodim esta como ...HABMAT_grassclump_PID.tif devemos mudar?? 
  os.remove(nametxtreclass)
  
  if Form1.calcStatistics:
    createtxt(Listmapspatch+"_patch_clump_mata_limpa", Form1.dirout, Listmapspatch+"_patch_AreaHA")
  
  if Form1.removeTrash:
    if Form1.prepareBIODIM:
      txts = [Listmapspatch+"_patch_clump", Listmapspatch+"_patch_clump_mata"]
    else:
      txts = [Listmapspatch+"_patch_clump", Listmapspatch+"_patch_clump_mata", Listmapspatch+"_patch_clump_mata_limpa"]
    for txt in txts:
      grass.run_command('g.remove', rast=txt, flags = "f")
  
def Patch(Listmapspatch):
  """
  Function for a series of maps
  This function calculates area per patch in a map (PATCH), considering structural connectivity 
  (no fragmentation or dilatation):
  - generates and exports maps with Patch ID and Area of each patch
  - generatics statistics - Area per patch (if Form1.calcStatistics == True)
  """
  
  for i in Listmapspatch:
    grass.run_command('g.region',rast=i)
    #expression1="MapaBinario="+i
    #grass.mapcalc(expression1, overwrite = True, quiet = True)    
   
    #expression2="A=MapaBinario"
    #grass.mapcalc(expression2, overwrite = True, quiet = True)
    
    ##r.colors map=A color=wave
    #expression3="MapaBinario_A=if(A[0,0]==0 && A[0,-1]==1 && A[1,-1]==0 && A[1,0]==1,1,A)"
    #grass.mapcalc(expression3, overwrite = True, quiet = True)
    #expression4="A=MapaBinario_A"
    #grass.mapcalc(expression4, overwrite = True, quiet = True)
    #expression5="MapaBinario_AB=if(A[0,0]==0 && A[-1,0]==1 && A[-1,1]==0 && A[0,1]==1,1,A)"
    #grass.mapcalc(expression5, overwrite = True, quiet = True) 
    #expression6="A=MapaBinario_AB"
    #grass.mapcalc(expression6, overwrite = True, quiet = True)
    #expression7="MapaBinario_ABC=if(A[0,0]==0 && A[0,1]==1 && A[1,1]==0 && A[1,0]==1,1,A)"
    #grass.mapcalc(expression7, overwrite = True, quiet = True)
    #expression8="A=MapaBinario_ABC"
    #grass.mapcalc(expression8, overwrite = True, quiet = True)
    #expression9="MapaBinario_ABCD=if(A[0,0]==0 && A[1,0]==1 && A[1,1]==0 && A[0,1]==1,1,A)"
    #grass.mapcalc(expression9, overwrite = True, quiet = True)
    #expression10="A=MapaBinario_ABCD"
    #grass.mapcalc(expression10, overwrite = True, quiet = True)
    #expression11=i+"_patch=A"
    #grass.mapcalc(expression11, overwrite = True, quiet = True)
    #r.colors map=$i"_patch" color=random
    grass.run_command('r.clump',input=i,output=i+"_patch_clump",overwrite = True)
    expression12=i+"_patch_clump_mata="+i+"_patch_clump*"+i
    grass.mapcalc(expression12, overwrite = True, quiet = True)
    expression13=i+"_patch_clump_mata_limpa=if("+i+"_patch_clump_mata>0,"+i+"_patch_clump_mata,null())"
    grass.mapcalc(expression13, overwrite = True, quiet = True)
    #r.colors map=$i"_patch_clump_mata_limpa" color=random
    nametxtreclass=rulesreclass(i+"_patch_clump_mata_limpa",Form1.dirout)
    grass.run_command('r.reclass',input=i+"_patch_clump_mata_limpa",output=i+"_patch_clump_mata_limpa_AreaHA",rules=nametxtreclass,overwrite = True)
    #grass.run_command('g.remove',flags='f',rast='A,MapaBinario,MapaBinario_A,MapaBinario_AB,MapaBinario_ABC,MapaBinario_ABCD')
    grass.run_command('g.region',rast=i+"_patch_clump_mata_limpa_AreaHA")
    grass.run_command('r.out.gdal',input=i+"_patch_clump_mata_limpa_AreaHA",out=i+"_patch_AreaHA.tif")
    if Form1.prepareBIODIM:
      grass.run_command('r.out.gdal',input=i+"_patch_clump_mata_limpa",out=i+"_patch_PID.tif")
    ############## no biodim esta como ...HABMAT_grassclump_PID.tif devemos mudar??
    os.remove(nametxtreclass)
    
    if Form1.calcStatistics:
      createtxt(i+"_patch_clump_mata_limpa", Form1.dirout, i+"_patch_AreaHA")
    
    if Form1.removeTrash:
      if Form1.prepareBIODIM:
        txts = [i+"_patch_clump", i+"_patch_clump_mata"]
      else:
        txts = [i+"_patch_clump", i+"_patch_clump_mata", i+"_patch_clump_mata_limpa"]
      for txt in txts:
        grass.run_command('g.remove', rast=txt, flags = "f")
    
  return Listmapspatch

#----------------------------------------------------------------------------------
# Metrics for functional connectivity area/ID (CON)

def areaconSingle(Listmapspatch):
  """
  Function for a single map
  This function calculates functional patch area in a map (CON), considering functional connectivity 
  (dilatation of edges given input scales/distances), and:
  - generates and exports maps with Patch ID and Area of each patch
  - generatics statistics - Area per patch (if Form1.calcStatistics == True)
  """
  
  listescalafconM,listmeters=escala_con(Listmapspatch,Form1.escala_con)
  x=0
  for a in listescalafconM:
    meters=listmeters[x]
    grass.run_command('r.neighbors',input=Listmapspatch,output=Listmapspatch+"_dila_"+`meters`+'m_orig',method='maximum',size=a,overwrite = True)
    grass.run_command('r.clump',input=Listmapspatch+"_dila_"+`meters`+'m_orig',output=Listmapspatch+"_dila_"+`meters`+'m_orig_clump',overwrite = True)
    espressiao1=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata='+Listmapspatch+'*'+Listmapspatch+"_dila_"+`meters`+'m_orig_clump'
    grass.mapcalc(espressiao1, overwrite = True, quiet = True)
    espressiao2=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa=if('+Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata>0,'+Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata,null())'
    grass.mapcalc(espressiao2, overwrite = True, quiet = True)
    nametxtreclass=rulesreclass(Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa',Form1.dirout)
    grass.run_command('r.reclass',input=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa',output=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_AreaHA',rules=nametxtreclass,overwrite = True)
    grass.run_command('r.out.gdal',input=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_AreaHA',out=Listmapspatch+"_dila_"+`meters`+'m_clean_AreaHA.tif')     
    os.remove(nametxtreclass)
    ############## no biodim eh HABMAT_grassclump_dila01_clean_AREApix.tif (ou complete, abaixo)
    ######### exportando o PID clean
    if Form1.prepareBIODIM:
      grass.run_command('r.out.gdal',input=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa',out=Listmapspatch+"_dila_"+`meters`+'m_clean_PID.tif')
      ########### calculando o area complete, exportanto ele e tb PID complete - precisa tambem gerar um area complete mesmo?
      nametxtreclass=rulesreclass(Listmapspatch+"_dila_"+`meters`+'m_orig_clump',Form1.dirout)
      grass.run_command('r.reclass',input=Listmapspatch+"_dila_"+`meters`+'m_orig_clump',output=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_complete_AreaHA', rules=nametxtreclass, overwrite = True)
      grass.run_command('r.out.gdal',input=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_complete_AreaHA',out=Listmapspatch+"_dila_"+`meters`+'m_complete_AreaHA.tif')  
      os.remove(nametxtreclass)      
      grass.run_command('r.out.gdal',input=Listmapspatch+"_dila_"+`meters`+'m_orig_clump',out=Listmapspatch+"_dila_"+`meters`+'m_complete_PID.tif')
    
    
    
    if Form1.calcStatistics:
      createtxt(Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa', Form1.dirout, Listmapspatch+"_dila_"+`meters`+"m_clean_AreaHA") # clean
      createtxt(Listmapspatch+"_dila_"+`meters`+'m_orig_clump', Form1.dirout, Listmapspatch+"_dila_"+`meters`+"m_complete_AreaHA") # complete
    ############
    # Na hora de exportar, eles ficaram com o mesmo numero de manchas, mas com areas diferentes!!! eh isso mesmo?!
    # faz sentido, afinal no completo ele conta a area fora das manchas, enquanto que no clean ele conta somente a area dentro
    # qual area conta para que? vamos usar a area do complete pra algo??
      
    if Form1.removeTrash:
      if Form1.prepareBIODIM:
        txts = [Listmapspatch+"_dila_"+`meters`+'m_orig', Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata']
      else:
        txts = [Listmapspatch+"_dila_"+`meters`+'m_orig', Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata', Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa']
      for txt in txts:
        grass.run_command('g.remove', rast=txt, flags = "f")
           
    
    x=x+1

def areacon(Listmapspatch):
  """
  Function for a series of maps
  This function calculates functional patch area in a map (CON), considering functional connectivity 
  (dilatation of edges given input scales/distances), and:
  - generates and exports maps with Patch ID and Area of each patch
  - generatics statistics - Area per patch (if Form1.calcStatistics == True)
  """
  
  for i in Listmapspatch:
    listescalafconM,listmeters=escala_con(i,Form1.escala_con)
    grass.run_command('g.region',rast=i)
    x=0
    for a in listescalafconM:
      meters=listmeters[x]    
      grass.run_command('r.neighbors',input=i,output=i+"_dila_"+`meters`+'m_orig',method='maximum',size=a,overwrite = True)
      grass.run_command('r.clump',input=i+"_dila_"+`meters`+'m_orig',output=i+"_dila_"+`meters`+'m_orig_clump',overwrite = True)
      espressiao1=i+"_dila_"+`meters`+'m_orig_clump_mata='+i+'*'+i+"_dila_"+`meters`+'m_orig_clump'
      grass.mapcalc(espressiao1, overwrite = True, quiet = True)
      espressiao2=i+"_dila_"+`meters`+'m_orig_clump_mata_limpa=if('+i+"_dila_"+`meters`+'m_orig_clump_mata>0,'+i+"_dila_"+`meters`+'m_orig_clump_mata,null())'
      grass.mapcalc(espressiao2, overwrite = True, quiet = True)
      nametxtreclass=rulesreclass(i+"_dila_"+`meters`+'m_orig_clump_mata_limpa',Form1.dirout)
      grass.run_command('r.reclass',input=i+"_dila_"+`meters`+'m_orig_clump_mata_limpa',output=i+"_dila_"+`meters`+'m_orig_clump_mata_limpa_AreaHA',rules=nametxtreclass,overwrite = True)
      grass.run_command('r.out.gdal',input=i+"_dila_"+`meters`+'m_orig_clump_mata_limpa_AreaHA',out=i+"_dila_"+`meters`+'m_clean_AreaHA.tif')  
      os.remove(nametxtreclass)
      ############### no biodim eh HABMAT_grassclump_dila01_clean_AREApix.tif (ou complete, abaixo)
      ########## exportando o PID clean
      if Form1.prepareBIODIM:
        grass.run_command('r.out.gdal',input=i+"_dila_"+`meters`+'m_orig_clump_mata_limpa',out=i+"_dila_"+`meters`+'m_clean_PID.tif')
        ########### calculando o area complete, exportanto ele e tb PID complete - precisa tambem gerar um area complete mesmo?
        #####nao lembro rs
        nametxtreclass=rulesreclass(i+"_dila_"+`meters`+'m_orig_clump',Form1.dirout)
        grass.run_command('r.reclass',input=i+"_dila_"+`meters`+'m_orig_clump',output=i+"_dila_"+`meters`+'m_orig_clump_complete_AreaHA', rules=nametxtreclass, overwrite = True)
        grass.run_command('r.out.gdal',input=i+"_dila_"+`meters`+'m_orig_clump_complete_AreaHA',out=i+"_dila_"+`meters`+'m_complete_AreaHA.tif')  
        os.remove(nametxtreclass)      
        grass.run_command('r.out.gdal',input=i+"_dila_"+`meters`+'m_orig_clump',out=i+"_dila_"+`meters`+'m_complete_PID.tif')
      
       
      
      if Form1.calcStatistics:
        createtxt(i+"_dila_"+`meters`+'m_orig_clump_mata_limpa', Form1.dirout, i+"_dila_"+`meters`+"m_clean_AreaHA")
        createtxt(i+"_dila_"+`meters`+'m_orig_clump', Form1.dirout, i+"_dila_"+`meters`+"m_complete_AreaHA")
      
      if Form1.removeTrash:
        if Form1.prepareBIODIM:
          txts = [i+"_dila_"+`meters`+'m_orig', i+"_dila_"+`meters`+'m_orig_clump_mata']
        else:
          txts = [i+"_dila_"+`meters`+'m_orig', i+"_dila_"+`meters`+'m_orig_clump_mata', i+"_dila_"+`meters`+'m_orig_clump_mata_limpa']
        for txt in txts:
          grass.run_command('g.remove', rast=txt, flags = "f")
          
      x=x+1

#----------------------------------------------------------------------------------
# Metrics for edge area (EDGE)

##############################
# por que uma funcao so pra isso para o ED? nao precisa
# cara eu fiz isso pq comecou dar pau quando eu colocava tudo junto, mas podemos tentar juntar

def mapcalcED(expressao):
  grass.mapcalc(expressao, overwrite = True, quiet = True)        

def create_EDGE_single(ListmapsED,escale_ed,dirs):
  """
  Function for a single map
  This function separates habitat area into edge and interior/core regions, given a scale/distance defined as edge, and:
  - generates and exports maps with each region
  - generatics statistics - Area per region (matrix/edge/core) (if Form1.calcStatistics == True)
  """  
  grass.run_command('g.region',rast=ListmapsED)
  listsize,listapoioname=escala_frag(ListmapsED, escale_ed)
  x=0
  for i in listsize:
    apoioname=listapoioname[x]  
    grass.run_command('r.neighbors',input=ListmapsED,output=ListmapsED+"_eroED_"+`apoioname`+'m',method='minimum',size=i,overwrite = True)
    inputs=ListmapsED+"_eroED_"+`apoioname`+'m,'+ListmapsED
    out=ListmapsED+'_EDGE'+`apoioname`+'m'
    grass.run_command('r.series',input=inputs,out=out,method='sum',overwrite = True)
    espressaoEd=ListmapsED+'_EDGE'+`apoioname`+'m_FINAL=int('+ListmapsED+'_EDGE'+`apoioname`+'m)'
    mapcalcED(espressaoEd)
    espressaoclip=ListmapsED+'_EDGE'+`apoioname`+'m_FINAL2=if('+ListmapsED+'>=0,'+ListmapsED+'_EDGE'+`apoioname`+'m_FINAL,null())'
    mapcalcED(espressaoclip)    
     
    grass.run_command('r.out.gdal',input=ListmapsED+'_EDGE'+`apoioname`+'m_FINAL2',out=ListmapsED+'_EDGE'+`apoioname`+'m.tif') 
    
    if Form1.calcStatistics:
      createtxt(out+'_FINAL2', dirs, out)
      
    if Form1.removeTrash:
      grass.run_command('g.remove',flags='f',rast=ListmapsED+"_eroED_"+`apoioname`+'m,'+ListmapsED+'_EDGE'+`apoioname`+'m,'+ListmapsED+'_EDGE'+`apoioname`+'m_FINAL')
    
    x=x+1
    
def create_EDGE(ListmapsED,escale_ed,dirs):
  """
  Function for a series of maps
  This function separates habitat area into edge and interior/core regions, given a scale/distance defined as edge, and:
  - generates and exports maps with each region
  - generatics statistics - Area per region (matrix/edge/core) (if Form1.calcStatistics == True)
  """
  for i in ListmapsED:
    grass.run_command('g.region',rast=i)
    listsize,listapoioname=escala_frag(i,escale_ed)
    x=0
    for a in listsize:
      apoioname=listapoioname[x]
      grass.run_command('r.neighbors',input=i,output=i+"_eroED_"+`apoioname`+'m',method='minimum',size=a,overwrite = True)
      inputs=i+"_eroED_"+`apoioname`+'m,'+i
      out=i+'_EDGE'+`apoioname`+'m'
      grass.run_command('r.series',input=inputs,out=out,method='sum',overwrite = True)
      espressaoEd=i+'_EDGE'+`apoioname`+'m_FINAL=int('+i+'_EDGE'+`apoioname`+'m)'
      mapcalcED(espressaoEd)
      espressaoclip=i+'_EDGE'+`apoioname`+'m_FINAL2=if('+i+'>=0,'+i+'_EDGE'+`apoioname`+'m_FINAL,null())'
      mapcalcED(espressaoclip)
      grass.run_command('r.out.gdal',input=i+'_EDGE'+`apoioname`+'m_FINAL2',out=i+'_EDGE'+`apoioname`+'m.tif')     
      
      if Form1.calcStatistics:
        createtxt(i+'_EDGE'+`apoioname`+'m_FINAL2', dirs, i+'_EDGE'+`apoioname`+'m')
      
      if Form1.removeTrash:
        grass.run_command('g.remove',flags='f',rast=i+"_eroED_"+`apoioname`+'m,'+i+'_EDGE'+`apoioname`+'m,'+i+'_EDGE'+`apoioname`+'m_FINAL')
      
      x=x+1

#----------------------------------------------------------------------------------
# Metrics for distance to edges
    
def dist_edge_Single(Listmapsdist):
  """
  Function for a single map
  This function calculates the distance of each pixel to habitat edges, considering
  negative values (inside patches) and positive values (into the matrix). Also:
  - generates and exports maps of distance to edge (DIST)
  """  
  grass.run_command('g.region', rast=Listmapsdist)
  expression1=Listmapsdist+'_invert=if('+Listmapsdist+'==0,1,null())'
  grass.mapcalc(expression1, overwrite = True, quiet = True)
  grass.run_command('r.grow.distance', input=Listmapsdist+'_invert', distance=Listmapsdist+'_invert_forest_neg_eucldist')
  expression2=Listmapsdist+'_invert_matrix=if('+Listmapsdist+'==0,null(),1)'
  grass.mapcalc(expression2, overwrite = True, quiet = True)
  grass.run_command('r.grow.distance', input=Listmapsdist+'_invert_matrix', distance=Listmapsdist+'_invert_matrix_pos_eucldist')
  expression3=Listmapsdist+'_invert_eucldist_edge='+Listmapsdist+'_invert_matrix_pos_eucldist-'+Listmapsdist+'_invert_forest_neg_eucldist'
  grass.mapcalc(expression3, overwrite = True, quiet = True)
  
  grass.run_command('r.out.gdal', input=Listmapsdist+'_invert_eucldist_edge', out=Listmapsdist+'_DIST.tif')

def dist_edge(Listmapsdist):
  """
  Function for a series of maps
  This function calculates the distance of each pixel to habitat edges, considering
  negative values (inside patches) and positive values (into the matrix). Also:
  - generates and exports maps of distance to edge (DIST)
  """
  for i in Listmapsdist:
    grass.run_command('g.region', rast=i)
    expression1=i+'_invert=if('+i+'==0,1,null())'
    grass.mapcalc(expression1, overwrite = True, quiet = True)
    grass.run_command('r.grow.distance', input=i+'_invert', distance=i+'_invert_forest_neg_eucldist')
    expression2=i+'_invert_matrix=if('+i+'==0,null(),1)'
    grass.mapcalc(expression2, overwrite = True, quiet = True)
    grass.run_command('r.grow.distance', input=i+'_invert_matrix', distance=i+'_invert_matrix_pos_eucldist')
    expression3=i+'_invert_eucldist_edge='+i+'_invert_matrix_pos_eucldist-'+i+'_invert_forest_neg_eucldist'
    grass.mapcalc(expression3, overwrite = True, quiet = True)
    
    grass.run_command('r.out.gdal', input=i+'_invert_eucldist_edge', out=i+'_DIST.tif')

#----------------------------------------------------------------------------------
# GUI

class Form1(wx.Panel,GrassFunctions):
    def __init__(self, parent, id):
        GrassFunctions.__init__(self)
        wx.Panel.__init__(self, parent, id)
        
        #variavels_______________________________________
        Form1.mapa_entrada=''
        Form1.Patch=False
        Form1.Frag=False
        Form1.Cone=False
        Form1.background_filename=[]
        
        ###########################
        Form1.removeTrash=True
        Form1.prepareBIODIM=True
        Form1.calcStatistics=True
        
        Form1.size = 450
        Form1.hsize = 450
        
        Form1.formcalculate='Multiple'
        Form1.species_profile_group=''
        Form1.speciesList=[]
        Form1.species_profile=''
        Form1.petternmaps=''
        Form1.start_raio=0
        
        Form1.label_prefix=''
        Form1.RedularExp=''
        Form1.listMapsPng=[]
        Form1.listMapsPngAux=[]
        Form1.contBG=0
        Form1.plotmaps=0
        Form1.lenlistpng=0  
        
        Form1.ListmapsPatch=[]
        Form1.ListMapsGroupCalc=[]
        Form1.escala_frag=''
        Form1.escala_ED=''
        Form1.dirout=''
        Form1.chebin=''
        Form1.checEDGE=''
        
        
        
        
        #________________________________________________

        Form1.speciesList=grass.mlist_grouped ('rast', pattern='(*)') ['PERMANENT']
        
        #____________________________________________________________________________
        


        Form1.dirout=selecdirectori()

        
        Form1.output_prefix2='Nome do arquivo + ext '

        self.quote = wx.StaticText(self, id=-1, label="Connectivity Index",pos=wx.Point(20, 20))
        
        font = wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD)
        self.quote.SetForegroundColour("blue")
        self.quote.SetFont(font)

        #____________________________________________________________________________
        
        # A multiline TextCtrl - This is here to show how the events work in this program, don't pay too much attention to it
        #caixa de mensagem
        self.logger = wx.TextCtrl(self,5, '',wx.Point(20,330), wx.Size(340,120),wx.TE_MULTILINE | wx.TE_READONLY)
        
        self.editname = wx.TextCtrl(self, 190, '', wx.Point(180, 82), wx.Size(100,-1)) #Regular expression
        self.editname = wx.TextCtrl(self, 191, '', wx.Point(270,200), wx.Size(80,-1)) #escala
        self.editname = wx.TextCtrl(self, 192, '', wx.Point(260,225), wx.Size(90,-1)) #borda
        
        wx.EVT_TEXT(self, 190, self.EvtText)
        wx.EVT_TEXT(self, 191, self.EvtText)
        wx.EVT_TEXT(self, 192, self.EvtText)
        #____________________________________________________________________________
        # A button
        self.button =wx.Button(self, 10, "START CALCULATIONS", wx.Point(20, 480))
        wx.EVT_BUTTON(self, 10, self.OnClick)
        self.button =wx.Button(self, 8, "EXIT", wx.Point(270, 480))
        wx.EVT_BUTTON(self, 8, self.OnExit)        
        self.button =wx.Button(self, 9, "change Map", wx.Point(280, 295))
        wx.EVT_BUTTON(self, 9, self.OnClick) 
        
        self.button =wx.Button(self, 11, "TXT RULES", wx.Point(283,260))
        wx.EVT_BUTTON(self,11, self.OnClick)        

        #____________________________________________________________________________
        ##------------ LElab_logo
        imageFile = 'logo_lab.png'
        im1 = Image.open(imageFile)
        jpg1 = wx.Image(imageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        wx.StaticBitmap(self, -1, jpg1, (20,190), (jpg1.GetWidth(), jpg1.GetHeight()), style=wx.SUNKEN_BORDER)
        
       

       #______________________________________________________________________________________________________________
       #static text
        
        self.SelecMetrcis = wx.StaticText(self,-1,"Choose Metric:",wx.Point(20,150))
        
        
        self.SelecMetrcis = wx.StaticText(self,-1,"Show Maps List:",wx.Point(180,300))
        self.SelecMetrcis = wx.StaticText(self,-1,"Regular Expression:",wx.Point(182, 62))
        self.SelecMetrcis = wx.StaticText(self,-1,"List Scale Unit(m):",wx.Point(180,200))
        self.SelecMetrcis = wx.StaticText(self,-1,"List Ed. Unit(m):",wx.Point(180,228))
        wx.EVT_TEXT(self, 185, self.EvtText)
        
        
        #______________________________________________________________________________________________________________
        
        
        #______________________________________________________________________________________________________________
        # Checkbox

        self.insure = wx.CheckBox(self, 96, "AH Patch.",wx.Point(90,150))
        wx.EVT_CHECKBOX(self, 96,   self.EvtCheckBox)     
        
        self.insure = wx.CheckBox(self, 95, "AH Frag.",wx.Point(160,150))
        wx.EVT_CHECKBOX(self, 95,   self.EvtCheckBox)   
        
       
        
        self.insure = wx.CheckBox(self, 97, "AH Con.",wx.Point(230,150))
        wx.EVT_CHECKBOX(self, 97,   self.EvtCheckBox)  
        
        self.insure = wx.CheckBox(self, 150, "EDGE.",wx.Point(295,150))
        wx.EVT_CHECKBOX(self, 150,   self.EvtCheckBox)        
        
        
        self.insure = wx.CheckBox(self, 98, "",wx.Point(260,300))
        wx.EVT_CHECKBOX(self, 98,   self.EvtCheckBox)  
        
        self.insure = wx.CheckBox(self, 99, "Create Bin.",wx.Point(180,265))
        wx.EVT_CHECKBOX(self, 99,   self.EvtCheckBox)        
        
        #______________________________________________________________________________________________________________
        #Radio Boxes
        self.dispersiveList = ['Multiple', 'Single',          ]
        rb = wx.RadioBox(self, 92, "Choose form calculate", wx.Point(20, 62), wx.DefaultSize,
                        self.dispersiveList, 2, wx.RA_SPECIFY_COLS)
        wx.EVT_RADIOBOX(self, 92, self.EvtRadioBox)
        
        
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
            self.logger.AppendText('EvtComboBox: NEED TO BE SPECIFYED' )
            
            


        
    #______________________________________________________________________________________________________   
    def OnClick(self,event):
        #self.logger.AppendText(" Click on object with Id %d\n" %event.GetId())
        
        #______________________________________________________________________________________________________________ 
        if event.GetId()==10:   #10==START
          if Form1.formcalculate=="Single":
            if Form1.Patch==True:   
              patchSingle(Form1.mapa_entrada)
            if Form1.Frag==True:
              areaFragSingle(Form1.mapa_entrada)
            if Form1.Cone==True:
              areaconSingle(Form1.mapa_entrada)
            if Form1.checEDGE==True:
              create_EDGE_single(Form1.mapa_entrada,Form1.escala_ED,Form1.dirout)
          else:
            Form1.ListMapsGroupCalc=grass.mlist_grouped ('rast', pattern=Form1.RedularExp) ['PERMANENT']
            if Form1.Patch==True:
              Form1.ListmapsPatch=Patch(Form1.ListMapsGroupCalc)
            
            if Form1.Frag==True:
              areaFrag(Form1.ListMapsGroupCalc)
            if Form1.Cone==True:
              areacon(Form1.ListMapsGroupCalc) 
            if Form1.checEDGE==True:
              create_EDGE(Form1.ListMapsGroupCalc,Form1.escala_ED,Form1.dirout)
            
        
        
        
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
              Form1.ListMapsGroupCalc=grass.mlist_grouped ('rast', pattern=Form1.RedularExp) ['PERMANENT']
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
        if event.GetId()==20: #20=output_prefix
            Form1.output_prefix=event.GetString()
            
        if event.GetId()==30: #30=popsize
            not_int=0
            try: 
                int(event.GetString())
            except ValueError:
                not_int=1
                
            if not_int==1:
                Form1.start_popsize=0
            else:
                Form1.start_popsize=int(event.GetString())
        
           
        if event.GetId()==190:
          Form1.RedularExp=event.GetString() 
          
        if event.GetId()==191:
          Form1.escala_frag=event.GetString()
          
        if event.GetId()==192:
          Form1.escala_ED=event.GetString()        
        

    #______________________________________________________________________________________________________
    def EvtCheckBox(self, event):
        #self.logger.AppendText('EvtCheckBox: %d\n' % event.Checked())
        if event.GetId()==95:
            if event.Checked()==1:
                Form1.Frag=True
                self.logger.AppendText('EvtCheckBox:\nSelected Metric: Frag \n')
                
                
            else:
                Form1.Frag=False
                self.logger.AppendText('EvtCheckBox: \nNot Selected Metric: Frag \n')
                

        if event.GetId()==96:
          if event.Checked()==1:
            Form1.Patch=True
          else:
            Form1.Patch=False
                   
            
        if event.GetId()==97:
          if event.Checked()==1:
            Form1.Cone=True
          else:
            Form1.Cone=False
                         
        
        
        if event.GetId()==98: #Form1.plotmaps
          if int(event.Checked())==1: 
            Form1.plotmaps=1
            Form1.listMapsPngAux=grass.mlist_grouped ('rast', pattern=Form1.RedularExp) ['PERMANENT']
            Form1.listMapsPng=exportPNG(Form1.listMapsPngAux)
            self.Refresh()             

          else:
            Form1.plotmaps=0
            self.logger.AppendText('   Plot maps: %s\n' % str(Form1.plotmaps))             
            
            
        if event.GetId()==99:
          if int(event.Checked())==1:
            Form1.chebin=True
            
        if event.GetId()==150: #check EDGE
          if int(event.Checked())==1:
            Form1.checEDGE=True
          else:
            Form1.checEDGE=False
        
            
         
            
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
