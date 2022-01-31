#---------------------------------------------------------------------------------------
"""
 LSMetrics - Ecologically Scaled Landscape Metrics
 Version 0.9.2
 
 Milton C. Ribeiro - mcr@rc.unesp.br
 John W. Ribeiro - jw.ribeiro.rc@gmail.com
 Bernardo B. S. Niebuhr - bernardo_brandaum@yahoo.com.br
 Mauricio H. Vancine - mauricio.vancine@gmail.com
 
 Laboratorio de Ecologia Espacial e Conservacao (LEEC)
 Universidade Estadual Paulista - UNESP
 Rio Claro - SP - Brazil
 
 LSMetrics is a package designed to calculate landscape metrics and
 landscape statistics and generate maps of landscape connectivity.
 Also, the software is designed to prepare maps and enviroment for running 
 BioDIM, an individual-based model of animal movement in fragmented landscapes.
 The software runs in a GRASS GIS environment and uses raster images as input.

 To run LSMetrics:
 
 python LSMetrics_v0_9_2.py
 
 Copyright (C) 2015-2021 by Milton C. Ribeiro, John W. Ribeiro, Bernardo B. S. Niebuhr, and Mauricio H. Vancine.

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
#from PIL import Image
import wx
import numpy as np
import collections
import warnings
import subprocess

# Platform in which LSMetrics is being run
CURRENT_OS = platform.system()

# LSMetrics Version:
VERSION = 'v.0.9.2'

# Current script folder
script_folder = os.getcwd()

#----------------------------------------------------------------------------------
def reclass_frag_cor(mappidfrag, dirs):
  '''
  essa funcao abre o txt cross separa os de transicao validos
  reclassifica o mapa de pidfrag onde 1
  '''
  
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
    txt_rules.write(str(i)+'='+str(temp)+'\n')
  txt_rules.close() 
  grass.run_command('r.reclass',input=mappidfrag,output=mappidfrag+'_reclass',rules='table_cross_reclass_rules.txt', overwrite = True)


#----------------------------------------------------------------------------------
# Auxiliary functions

#-------------------------------
# Function selectdirectory
def selectdirectory():
  '''
  Function selectdirectory
  
  This function opens a dialog box in the GUI and asks the user to select the output folder
  for saving files. It then returns the path to this folder as a string.
  '''
  
  # Create a dialog box asking for the output folder
  dialog = wx.DirDialog(None, "Select the folder where the output files will be saved:",
                        style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
  
  # After selected, the box closes and the path to the chosen folder is returned
  if dialog.ShowModal() == wx.ID_OK:
    #print ">>..................",dialog.GetPath()
    return dialog.GetPath()

#-------------------------------
# Function create_TXTinputBIODIM
def create_TXTinputBIODIM(list_maps, outputfolder, filename):
  '''
  Function create_TXTinputBIODIM
  
  This function creates the output text files that BioDIM package need to the names of the maps
  within the GRASS GIS location and read them.
  
  Input:
  list_maps: list with strings; a python list of map names generated within the GRASS GIS location.
  outputfolder: string; a folder where the output text files will be saved/written.
  filename: string; the name of the file to be created.
  
  Output:
  A file with the names of the maps within GRASS GIS.
  '''
  
  # Open a file in the output folder
  txtMap = open(outputfolder+"/"+filename+".txt", "w")

  # For each map in the list of maps, it writes a line
  for i in list_maps:
    txtMap.write(i+'\n')
    
  txtMap.close() # Close the file
    
#-------------------------------
# Function createtxt
def createtxt(input_map, outputfolder, filename = ''):
  '''
  Function createtxt
  
  This function creates text files with statistics (area, percentage) regarding the classes within maps
  generated by a function in LSMetrics.
  
  Input:
  input_map: string; the name of the input map the user wants statistics from
  outputfolder: string; a folder where the output text files will be saved/written.
  filename: string; the name of the file to be created.
  
  Output:
  This function creates a text file with:
  - Values of area, in hectares, for edge, interior and core areas (for EDGE metrics)
  - Values of area, in hectares, for each patch (for PATCH, FRAG and CON metrics)
  '''
  
  # Define region
  grass.run_command('g.region', rast=input_map)  
  # Calculate area and percentage statistics for the input map using r.stats
  x = grass.read_command('r.stats', flags = 'ap', input = input_map)
  
  # Separating values by line
  y = x.split('\n')
  
  # Change to the output folder and select the name of the output text file
  os.chdir(outputfolder)
  if filename != '': 
    name = filename+'.txt'
  else:
    name = input_map+'.txt' # If no specific name is given, call it 'input_map'
  
  # Initialize arrays
  idd = []
  areas = []
  
  if len(y) != 0:
    # For each element in the list of values
    for i in y:
      if i != '':
        ##print i
        # Split by space
        f = i.split(' ')
        
        # In the last line we may have *; stop in this case
        if '*' in f :
          break
        # If it is not the last line
        else:
          ##print f
          # Get id (raster value)
          ids = f[0]
          ids = int(ids)
          idd.append(ids)
          ##print ids
          # Get area in m2 and transforms to hectares
          ha = f[1]
          ha = float(ha)
          haint = float(ha)
          haint = haint/10000+1
          areas.append(haint)
          ##print haint
          
    # Calculate the percentage
    percentages = [float(i)/sum(areas) for i in areas]
    
    # Open output file
    txt_file = open(name, 'w')
    
    # Write header
    txt_file.write('CODE'+','+'AREA_HA'+','+'PROPORTION\n')    

    # For each element
    for i in range(len(idd)):
      # Write line in the output file
      txt_file.write(str(idd[i])+','+str(areas[i])+','+str(percentages[i])+'\n')
          
    # Close the output file
    txt_file.close()
    
#-------------------------------
# Function rulesreclass
def rulesreclass(input_map, outputfolder):
  '''
  Function rulesreclass
  
  This function sets the rules for area reclassification for patch ID, using stats -a for each patch.
  The output is a text file with such rules. 
  
  Input:
  input_map: string; the name of the input map the user wants statistics from
  outputfolder: string; a folder where the output text files will be saved/written.
  
  Output:
  This function creates a text file area values for each patch ID, used to reclassify and 
  generate maps area maps. It returns the name of the text files with reclassification rules
  '''
  
  # Define region
  grass.run_command('g.region', rast=input_map)  
  # Calculate area and percentage statistics for the input map using r.stat  
  x = grass.read_command('r.stats', flags='a', input=input_map)
  
  # Separating values by line
  y=x.split('\n')
 
  # Change to the output folder and select the name of the output text file
  os.chdir(outputfolder)
  txt_file_name = input_map+'_rules.txt'
    
  if len(y) != 0:
    
    # Open output file 
    txtreclass = open(txt_file_name, 'w')
    
    # For each element in the list of values
    for i in y:
      if i != '':
        ##print i
        # Split by space
        f=i.split(' ')
        
        # In the last line we may have *; stop in this case
        if '*' in f or 'L' in f :
          break
        # If it is not the last line
        else:
          ##print f
          # Get id (raster value)
          ids=f[0]
          ids=int(ids)
          ##print ids
          # Get area in m2 and transforms to hectares
          ha=f[1]
          ha=float(ha)
          haint=float(round(ha))
          haint2=haint/10000+1
          
          # Write line in the output file
          txtreclass.write(str(ids)+'='+str(haint2)+ '\n')
          
    txtreclass.close()
    
  # Return the name of the reclass file generated
  return txt_file_name

#----------------------------------------------------------------------------------
# Leading with scales, lengths, and pixel sizes - organization

#-------------------------------
# Function connectivity_scales
def connectivity_scales(input_map, list_gap_crossing):
  '''
  Function connectivity_scales
  
  This function calculates the size(s) and number of pixels corresponding to the scales maps will be dilatated
  to be integrated by gap crossing distances.
  If the gap crossing distance is 120m for example, maps are dilatated by 60m (half of it), so that patches
  distant less that 120m are considered functionally connected. Then, this half-distance is returned, and its
  equivalent in number of pixels.
  
  Input:
  input_map: string; name of the input map (from where the resolution is assessed).
  list_gap_crossing: python list with float numbers; list of gap crossing distances, in meters, to be considered.
  
  Output:
  The number of pixels and distance by which habitat patches must be dilatated to assess functional connectivity
  of habitat patches.
  '''
  
  # Assess the resolution of the input map
  map_info = grass.parse_command('g.region', rast = input_map, flags = 'm')
  res = float(map_info['ewres'])
  
  # Initialize list of edge depth in meters and corridor width in pixels
  list_gap_crossing_meters = []
  list_gap_crossing_pixels = []
  
  # For each value in the list of edge depths
  for i in list_gap_crossing:
    
    # Trasform into float
    cross = float(i)
    # Number of pixels that corresponds to each gap crossing distance
    fine_scale = cross/res
    # Gap crossing is devided by two, since this is the scale that will be dilatated in maps
    gap_crossing_pixels = fine_scale/2
    
    gap_crossing_pixels = int(round(gap_crossing_pixels, ndigits=0))

    # Rounding to an integer odd number of pixels
    # If the number is even, we sum 1 to have an odd number of pixel to the moving window    
    if gap_crossing_pixels %2 == 0:
      gap_crossing_pixels = int(gap_crossing_pixels)
      gap_crossing_pixels = 2*gap_crossing_pixels + 1
      list_gap_crossing_meters.append(int(cross/2)) # append the gap crossing in meters to the list
      list_gap_crossing_pixels.append(gap_crossing_pixels) # append the gap crossing in pixels to the list
      
    # If the number is already odd, it is ok    
    else:
      gap_crossing_pixels = int(round(gap_crossing_pixels, ndigits=0))
      gap_crossing_pixels = 2*gap_crossing_pixels + 1
      list_gap_crossing_meters.append(int(cross/2)) # append the gap crossing in meters to the list
      list_gap_crossing_pixels.append(gap_crossing_pixels) # append the gap crossing in pixels to the list
        
  # Return both lists
  return list_gap_crossing_meters, list_gap_crossing_pixels

#-------------------------------
# Function frag_scales 
def frag_scales(input_map, list_edge_depths):
  '''
  Function frag_scales
  
  This function calculates the size(s) and number of pixels corresponding to
  to corridor width to be removed from fragment size maps, based on a (list of) value(s) of edge depth.
  The size of corridors to be removed is considered as twice the edge depth.
  
  Input:
  input_map: string; name of the input map (from where the resolution is assessed).
  list_edge_depths: python list with float numbers; list of edge depths, in meters, to be considered.
  
  Output:
  The number of pixels which correspond to the width of the corridors to be excluded from habitat patch maps - 
  corridor width is considered as twice the edge depth.
  As this values in pixels are used in the GRASS GIS function as the size of the moving window in r.neighbors, 
  remind that this size must be always odd, and the function already does that.
  '''
  
  # Assess the resolution of the input map
  map_info = grass.parse_command('g.region', rast = input_map, flags='m')
  res = float(map_info['ewres'])

  # Initialize list of edge depth in meters and corridor width in pixels
  list_edge_depths_meters = []
  list_corridor_width_pixels =[]
  
  # For each value in the list of edge depths
  for i in list_edge_depths:
    
    depth = float(i)
    # Number of pixels that corresponds to each edge depth
    fine_scale = depth/res
    # Corridor width is considered as twice the edge depth
    corridor_width_pix = fine_scale * 2
    
    # Rounding to an integer number of pixels
    # If the number is even, we sum 1 to have an odd number of pixel to the moving window
    if int(corridor_width_pix) %2 == 0:
      corridor_width_pix = int(corridor_width_pix)
      corridor_width_pix = corridor_width_pix + 1
      list_edge_depths_meters.append(int(depth)) # append the edge depth to the list
      list_corridor_width_pixels.append(corridor_width_pix) # append the corridor width to the list
      
    # If the number is already odd, it is ok
    else:
      corridor_width_pix = int(round(corridor_width_pix, ndigits=0))
      list_edge_depths_meters.append(int(depth)) # append the edge depth to the list
      list_corridor_width_pixels.append(corridor_width_pix) # append the corridor width to the list
      
  # Return both lists
  return list_edge_depths_meters, list_corridor_width_pixels


#------------------------------- 
# Function get_size_pixels
def get_size_pixels(input_map, scale_in_meters):
  '''
  Function get_size_pixels
  
  This function uses the scale difined by the user and the pixel size to 
  return the number of pixels that correspond to the scale
  (to define the size of the moving window)
  
  Input:
  input_map: string; name of the input map, from which the resolution/pixel size will be taken.
  scale_in_meters: float or integer; size of the moving window in meters.
  
  Output:
  The number of pixels which correspond to the size of the moving window, to be used in a GRASS GIS
  function such as r.neighbors. Remind that this size must be always odd, and the function already does that.
  '''
  
  # Assess the resolution of the input map
  map_info = grass.parse_command('g.region', rast = input_map, flags = 'm')      
  res = float(map_info['ewres'])
  #######################################
  #scale_in_pixels = (float(scale_in_meters)*2)/res # should we really multiply it by 2????
  scale_in_pixels = (float(scale_in_meters))/res # should we really multiply it by 2????
  
  # Checking if number of pixels of moving window is integer and even
  # and correcting it if necessary
  if int(scale_in_pixels)%2 == 0: # If the number of pixels is even, add 1
    scale_in_pixels = int(scale_in_pixels)
    scale_in_pixels = scale_in_pixels + 1 
  else: # If the number of pixels is odd, it is ok
    scale_in_pixels = int(scale_in_pixels)
  
  # Returns the scale in number of pixels
  return scale_in_pixels

#----------------------------------------------------------------------------------
# Functions of Landscape Metrics

#-------------------------------
# Function create_binary
def create_binary(list_maps, 
                  list_habitat_classes, 
                  zero = True,
                  prepare_biodim = False, 
                  calc_statistics = False, 
                  prefix = '', 
                  add_counter_name = False, 
                  export = False, 
                  dirout = ''):
  '''
  Function create_binary
  
  This function reclassify a (series of) input map(s) into a (series of) binary map(s), with values
  1/0 or 1/null. This is done by considering a list of values which represent a given type of habitat 
  or environment, which will be reclassified as 1 in the output; all the other values in the map 
  will be set to zero/null value.
  
  Input:
  list_maps: list with strings; a python list with maps loaded in the GRASS GIS location.
  list_habitat_classes: list with strings or integers; a python list of values that correspond to habitat in the input raster maps, and will be considered as 1 in the output.
  zero: (True/False) logical; if True, non-habitat values are set to zero; otherwise, they are set as null values.
  prepare_biodim: (True/False) logical; if True, maps and input text files for running BioDIM package are prepared.
  calc_statistics: (True/False) logical; if True, statistics are calculated and saved as an output text file.
  prefix: string; a prefix to be appended in the beginning of the output map names.
  add_counter_name: (True/False) logical; if True, a number is attached to the beginning of each outputmap name, in the order of the input, following 0001, 0002, 0003 ...
  export: (True/False) logical; if True, the maps are exported from GRASS.
  dirout: string; folder where the output maps will be saved when exported from GRASS. If '', the output maps are generated but are not exported from GRASS.
  
  Output:
  A binary map where all the map pixels in 'list_habitat_classes' are set to 1 and all the other pixels are
  set to zero (if zero == True, or null if zero == False).
  The function returns a python list with the names of the binary class maps created.
  If prepare_biodim == True, a file with binary maps to run BioDIM is generated.
  If calc_statistics == True, a file with the area/proportion of each class (habitat/non-habitat) is generated.
  '''
  
  # If we ask to export something but we do not provide an output folder, it shows a warning
  if (export or prepare_biodim or calc_statistics) and dirout == '':
    warnings.warn("You are trying to export files from GRASS but we did not set an output folder.")
  
  # A list of map names is initialized, to be returned
  list_maps_habmat = []
   
  # Initialize counter, in case the user wants to add a number to the map name
  cont = 1
  
  # For each map in the list of input maps
  for i_in in list_maps:
    
    # Putting (or not) a prefix in the beginning of the output map name
    if not add_counter_name:
      pre_numb = ''
    else: # adding numbers in case of multiple maps
      pre_numb = '00000'+str(cont)+'_'
      pre_numb = pre_numb[-5:]
    
    # Check if the list of classes is greater than zero
    if len(list_habitat_classes) > 0:
      
      conditional = ''
      cc = 0
      # Creates a condition for all habitat classes being considered as 1
      for j in list_habitat_classes:
        if cc > 0:
          conditional = conditional+' || '
        conditional = conditional+i_in+' == '+str(j)
        cc += 1
      
      # Prefix of the output
      i = prefix+pre_numb+i_in
      
      if zero == True:
      # Calculating binary map with 1/0
        expression = i+'_HABMAT = if('+conditional+', 1, 0)'
      else:
        # Calculating binary map with 1/0
        expression = i+'_HABMAT = if('+conditional+', 1, null())'        

      # Define region and run reclassification using r.mapcalc
      grass.run_command('g.region', rast=i_in)
      grass.mapcalc(expression, overwrite = True, quiet = True)
    
    else: # If the list of habitat values is not > 0, it gives an error.
      raise Exception('You did not type which class is habitat! Map not generated.\n')
    
    # The list of map names is updated
    list_maps_habmat.append(i+'_HABMAT')
    
    # If export == True and dirout == '', the map is not exported; in other cases, the map is exported in this folder
    if export == True and dirout != '':
      os.chdir(dirout)
      grass.run_command('g.region', rast=i+'_HABMAT')
      grass.run_command('r.out.gdal', flags = 'c', input=i+'_HABMAT', out=i+'_HABMAT.tif', createopt = "TFW=YES,COMPRESS=DEFLATE", overwrite = True)
  
    # If calc_statistics == True, the stats of this metric are calculated and exported
    if calc_statistics and dirout != '':
      createtxt(i+'_HABMAT', dirout, i+'_HABMAT')
    
    # Update counter of the map number
    cont += 1
      
  # If prepare_biodim == True, use the list of output map names to create a text file and export it
  if prepare_biodim:
    create_TXTinputBIODIM(list_maps_habmat, dirout, "simulados_HABMAT")
    
  return list_maps_habmat

   
#-------------------------------
# Function patch_size
def patch_size(input_maps, 
               zero = False, 
               diagonal = True,
               prepare_biodim = False, 
               calc_statistics = False, 
               remove_trash = True,
               prefix = '', 
               add_counter_name = False, 
               export = False, 
               export_pid = False, 
               dirout = ''):
  '''
  Function patch_size
  
  This function calculates patch area, considering all pixels that are continuous as a single patch.
  Areas are calculated in hectares, assuming that input map projection is in meters.
  
  Input:
  input_maps: list with strings; a python list with maps loaded in the GRASS GIS location. Must be binary class maps (e.g. maps of habitat-non habitat).
  zero: (True/False) logical; if True, non-habitat values are set to zero; otherwise, they are set as null values.
  diagonal: (True/False) logical; if True, cells are clumped also in the diagonal for estimating patch size.
  prepare_biodim: (True/False) logical; if True, maps and input text files for running BioDIM package are prepared.
  calc_statistics: (True/False) logical; if True, statistics are calculated and saved as an output text file.
  remove_trash: (True/False) logical; if True, maps generated in the middle of the calculation are deleted; otherwise they are kept within GRASS.
  prefix: string; a prefix to be appended in the beginning of the output map names.
  add_counter_name: (True/False) logical; if True, a number is attached to the beginning of each outputmap name, in the order of the input, following 0001, 0002, 0003 ...
  export: (True/False) logical; if True, the maps are exported from GRASS.
  export_pid: (True/False) logical; if True, the patch ID (pid) maps are exported from GRASS.
  dirout: string; folder where the output maps will be saved when exported from GRASS. If '', the output maps are generated but are not exported from GRASS.
  
  Output:
  Maps with Patch ID and Area of each patch (considering non-habitat as 0 if zero == True or null if zero == False).
  If prepare_biodim == True, a file with patch size maps to run BioDIM is generated.
  If calc_statistics == True, a file with area per patch in hectares is generated.
  '''
  
  # If we ask to export something but we do not provide an output folder, it shows a warning
  if (export or prepare_biodim or calc_statistics) and dirout == '':
    warnings.warn("You are trying to export files from GRASS but we did not set an output folder.")  
  
  # The lists of map names of Patch ID and area are initialized
  lista_maps_pid = []
  lista_maps_area = []  

  # Initialize counter, in case the user wants to add a number to the map name
  cont = 1
  
  # For each map in the list of input maps
  for i_in in input_maps:
    
    # Putting (or not) a prefix in the beginning of the output map name
    if not add_counter_name:
      pre_numb = ''
    else: # adding numbers in case of multiple maps
      pre_numb = '00000'+str(cont)+'_'
      pre_numb = pre_numb[-5:]
      
    # Prefix of the output
    i = prefix+pre_numb+i_in

    # Define the region
    grass.run_command('g.region', rast = i_in)
    
    # Clump pixels that are contiguous in the same patch ID
    if diagonal: # whether or not to clump pixels considering diagonals
      grass.run_command('r.clump', input=i_in, output=i+'_patch_clump', overwrite = True, flags = 'd')
    else:
      grass.run_command('r.clump', input=i_in, output=i+'_patch_clump', overwrite = True)
      
    # Takes only what is habitat
    expression1 = i+"_patch_clump_hab = "+i+"_patch_clump * "+i_in
    grass.mapcalc(expression1, overwrite = True, quiet = True)
    # Transforms non-habitat cells into null cells - this is the Patch ID map
    expression2 = i+"_pid = if("+i+"_patch_clump_hab > 0, "+i+"_patch_clump_hab, null())"
    grass.mapcalc(expression2, overwrite = True, quiet = True)
    
    # Reclass pixel id values by calculating the area in hectares
    
    if dirout != '':
      os.chdir(dirout) # folder to save temp reclass file
    # If zero == False (non-habitat cells are considered null)
    if zero == False:
      nametxtreclass = rulesreclass(input_map = i+"_pid", outputfolder = '.')
      grass.run_command('r.reclass', input = i+"_pid", output = i+"_patch_AreaHA", rules=nametxtreclass, overwrite = True)
      os.remove(nametxtreclass)
      # We could also use r.area
      # area - number of pixels
      #grass.run_command("r.area", input = i+"_pid", output = i+"_numpix", overwrite = True)
      # area in hectares
      # Code for taking the area of a pixel in hectares - pixel_size
      #ex = i+"_AreaHA = "+i+"_pid * pixel_size"
      #grass.mapcalc(ex, overwrite = True)
    else: # If zero == True (non-habitat cells are considered as zeros)
      nametxtreclass = rulesreclass(input_map = i+"_pid", outputfolder = '.')
      grass.run_command('r.reclass', input = i+"_pid", output = i+"_patch_AreaHA_aux", rules=nametxtreclass, overwrite = True)
      os.remove(nametxtreclass)      

      # Transforms what is 1 in the binary map into the patch size
      expression3 = i+'_patch_AreaHA = if('+i_in+' == 0, 0, '+i+'_patch_AreaHA_aux)'
      grass.mapcalc(expression3, overwrite = True)    
    
    # The list of map names is updated
    lista_maps_pid.append(i+"_pid")
    lista_maps_area.append(i+"_patch_AreaHA")
     
    # If export == True and dirout == '', the map is not exported; in other cases, the map is exported in this folder
    if export == True and dirout != '':
      os.chdir(dirout)
      grass.run_command('g.region', rast = i+"_patch_AreaHA")
      grass.run_command('r.out.gdal', flags = 'c', input = i+"_patch_AreaHA", out = i+"_patch_AreaHA.tif", createopt = "TFW=YES,COMPRESS=DEFLATE", overwrite = True)
    # If export_pid == True, the patch ID map is exported in this folder
    if export_pid == True and dirout != '':
      os.chdir(dirout)
      grass.run_command('g.region', rast = i+"_pid")
      grass.run_command('r.out.gdal', flags = 'c', input = i+"_pid", out = i+"_pid.tif", createopt = "TFW=YES,COMPRESS=DEFLATE", overwrite = True)
          
    # If calc_statistics == True, the stats of this metric are calculated and exported
    if calc_statistics:
      createtxt(i+"_pid", dirout, i+"_patch_AreaHA")
    
    # If remove_trash == True, the intermediate maps created in the calculation of patch size are removed
    if remove_trash:
      # Define list of maps
      if zero:
        txts = [i+"_patch_clump", i+"_patch_clump_hab", i+"_patch_AreaHA_aux"]
      else:
        txts = [i+"_patch_clump", i+"_patch_clump_hab"]
      # Remove maps from GRASS GIS location
      for txt in txts:
        grass.run_command('g.remove', type="raster", name=txt, flags='f')
    
    # Update counter of the map number    
    cont += 1
        
  # If prepare_biodim == True, use the list of output map names to create a text file and export it
  if prepare_biodim:
    create_TXTinputBIODIM(lista_maps_pid, dirout, "simulados_HABMAT_grassclump_PID")
    create_TXTinputBIODIM(lista_maps_area, dirout, "simulados_HABMAT_grassclump_AREApix")  # Review these names later on!!
    
  # Return a list of maps of Patch ID and Patch area
  return lista_maps_pid, lista_maps_area


#-------------------------------
# Function fragment_area
def fragment_area(input_maps, 
                  list_edge_depths,
                  zero = False, 
                  diagonal = True, 
                  diagonal_neighbors = True,
                  struct_connec = False, 
                  patch_size_map_names = [],
                  prepare_biodim = False, 
                  calc_statistics = False, 
                  remove_trash = True,
                  prefix = '', 
                  add_counter_name = False, 
                  export = False, 
                  export_fid = False, 
                  export_struct_connec = True, 
                  dirout = ''):

  # check that - other parameters used list_meco, check_func_edge,
  '''
  Function fragment_area
  
  This function fragments habitat patches (FRAG), excluding corridors and edges,
  given input habitat maps and scales that correspond to edge depths. The habitatcorridors 
  that are excluded from habitat patch to habitat fragment maps have a width corresponding to 
  two the edge depth passed as input.
  
  Input:
  input_maps: list with strings; a python list with maps loaded in the GRASS GIS location. Must be binary class maps (e.g. maps of habitat-non habitat).
  list_edge_depths: list with numbers; each value correpond to an edge depth; the function excludes corridors with width = 2*(edge depth) to calculate fragment size.
  zero: (True/False) logical; if True, non-habitat values are set to zero; otherwise, they are set as null values.
  diagonal: (True/False) logical; if True, cells are clumped also in the diagonal for estimating patch size, in r.clump. The default is True.
  diagonal_neighbors: (True/False) logical; if True, diagonal cells are considering when compressing and dilatating patches with r.neighbors. The default is True.
  struct_connec: (True/False) logical; if True, a structural connectivity map is also calculated. In this case, a (list of) map(s) of pactch size must be also provided.
  patch_size_map_names: list with strings; a python list with the names of the patch size maps created using the function patch_size, corresponding to the patch size maps to be used to calculate structural connectivity maps.
  prepare_biodim: (True/False) logical; if True, maps and input text files for running BioDIM package are prepared.
  calc_statistics: (True/False) logical; if True, statistics are calculated and saved as an output text file.
  remove_trash: (True/False) logical; if True, maps generated in the middle of the calculation are deleted; otherwise they are kept within GRASS.
  prefix: string; a prefix to be appended in the beginning of the output map names.
  add_counter_name: (True/False) logical; if True, a number is attached to the beginning of each outputmap name, in the order of the input, following 0001, 0002, 0003 ...
  export: (True/False) logical; if True, the maps are exported from GRASS.
  export_fid: (True/False) logical; if True, the fragment ID (fid) maps are exported from GRASS.
  dirout: string; folder where the output maps will be saved when exported from GRASS. If '', the output maps are generated but are not exported from GRASS.
  
  Output:
  Maps with Fragment ID and Area in hectares of each fragment (considering non-habitat as 0 if zero == True or null if zero == False).
  Fragments are equal to habitat patches but exclude corridors and branches with width equals 2*(edge depth).
  If prepare_biodim == True, a file with fragment size maps to run BioDIM is generated.
  If calc_statistics == True, a file with area per fragment in hectares is generated.
  '''

  # If we ask to export something but we do not provide an output folder, it shows a warning
  if (export or prepare_biodim or calc_statistics) and dirout == '':
    warnings.warn("You are trying to export files from GRASS but we did not set an output folder.")
    
  if (struct_connec and (len(patch_size_map_names) == 0 or len(patch_size_map_names) != len(input_maps))):
    raise Warning('A list of names of patch size maps must be provided, and its length must be equal to number of input maps.')

  # If prepare_biodim == True, lists of map names of Fragment ID and area are initialized
  # Theses lists here are matrices with input maps in rows and edge depths in columns
  if prepare_biodim:
    lista_maps_fid = np.empty((len(input_maps), len(list_edge_depths)), dtype=np.dtype('a200'))
    lista_maps_farea = np.empty((len(input_maps), len(list_edge_depths)), dtype=np.dtype('a200'))
  
  # Initialize counter of map name for lists of map names
  z = 0 
  
  # Initialize counter, in case the user wants to add a number to the map name
  cont = 1
  list_ssbc_maps=[] ###################
  
  # For each map in the list of input maps
  for i_in in input_maps:
    
    # Putting (or not) a prefix in the beginning of the output map name
    if not add_counter_name:
      pre_numb = ''
    else: # adding numbers in case of multiple maps
      pre_numb = '00000'+str(cont)+'_'
      pre_numb = pre_numb[-5:]
      
    # Prefix of the output
    i = prefix+pre_numb+i_in
    
    # Define the region      
    grass.run_command('g.region', rast=i_in)
    
    # Calculate edge depths and corridor widths to be subtracted from connections between patches
    edge_depths, list_corridor_width_pixels = frag_scales(i_in, list_edge_depths)
    
    # Initialize counter of edge depth value for lists of map names
    x = 0
    
    lista_maps_CSSB=[] ################

    # For each value in the list of corridor widths
    for a in list_corridor_width_pixels:
      meters = int(edge_depths[x]) # should we use the input list_edge_depths instead? only list_edge_depths[x]
      
      # Prefix for map names regarding scale
      format_escale_name = '0000'+str(meters)
      format_escale_name = format_escale_name[-4:]
      
      if diagonal_neighbors:
        flag_neighbors = '' # considers diagonals
      else:
        flag_neighbors = 'c' # considers circular moving window
      
      # Uses a moving window to erodes habitat patches, by considering the minimum value within a window
      grass.run_command('r.neighbors', input = i_in, output = i+"_ero_"+format_escale_name+'m', method = 'minimum', size = a, overwrite = True, flags = flag_neighbors)
      
      # This is followed by dilatating the patches again (but not the corridors), by considering the maximum value within a moving window
      grass.run_command('r.neighbors', input=i+"_ero_"+format_escale_name+'m', output = i+"_dila_"+format_escale_name+'m', method = 'maximum', size = a, overwrite = True, flags = flag_neighbors)
      
      # Taking only positive values
      expression1 = i+"_FRAG_"+format_escale_name+"m_pos = if("+i+"_dila_"+format_escale_name+'m'+" > 0, "+i+"_dila_"+format_escale_name+'m'+", null())"
      grass.mapcalc(expression1, overwrite = True, quiet = True)
      expression2 = i+"_FRAG_"+format_escale_name+"m_pos_habitat = if("+i_in+" > 0, "+i+"_FRAG_"+format_escale_name+"m_pos, null())"
      grass.mapcalc(expression2, overwrite = True, quiet = True)
      
      # Clump pixels that are contiguous in the same fragment ID
      if diagonal: # whether or not to clump pixels considering diagonals
        grass.run_command('r.clump', input = i+"_FRAG_"+format_escale_name+"m_pos_habitat", output = i+"_"+format_escale_name+"m_fid", overwrite = True, flags = 'd')
      else:
        grass.run_command('r.clump', input = i+"_FRAG_"+format_escale_name+"m_pos_habitat", output = i+"_"+format_escale_name+"m_fid", overwrite = True)      
      
      # Reclass pixel id values by calculating the area in hectares
        
      if dirout != '':
        os.chdir(dirout) # folder to save temp reclass file
      # Define region
      grass.run_command('g.region', rast = i+"_"+format_escale_name+"m_fid")
      
      # If zero == False (non-habitat cells are considered null)
      if zero == False:      
        nametxtreclass = rulesreclass(i+"_"+format_escale_name+"m_fid", outputfolder = '.')
        grass.run_command('r.reclass', input = i+"_"+format_escale_name+"m_fid", output = i+"_"+format_escale_name+"m_fragment_AreaHA", rules=nametxtreclass, overwrite = True)   
        os.remove(nametxtreclass)
      else: # If zero == True (non-habitat cells are considered as zeros)
        nametxtreclass = rulesreclass(i+"_"+format_escale_name+"m_fid", outputfolder = '.')
        grass.run_command('r.reclass', input = i+"_"+format_escale_name+"m_fid", output = i+"_"+format_escale_name+"m_fragment_AreaHA_aux", rules=nametxtreclass, overwrite = True)   
        os.remove(nametxtreclass)
        
        # Transforms what is 1 in the binary map into the patch size
        expression3 = i+'_'+format_escale_name+'m_fragment_AreaHA = if('+i_in+' == 0, 0, '+i+'_'+format_escale_name+'m_fragment_AreaHA_aux)'
        grass.mapcalc(expression3, overwrite = True)
        
      # Calculates structural connectivity
      if struct_connec:
        expression4 = i+'_'+format_escale_name+'m_structural_connectivity = '+patch_size_map_names[z]+' - '+i+'_'+format_escale_name+'m_fragment_AreaHA'
        grass.mapcalc(expression4, overwrite = True)
      
      ## identificando branch tampulins e corredores
      #expression3='temp_BSSC=if(isnull('+i+"_FRAG"+format_escale_name+"m_mata_clump_AreaHA"+'),'+i_in+')'
      #grass.mapcalc(expression3, overwrite = True, quiet = True)    
      
      #expression1="MapaBinario=temp_BSSC"
      #grass.mapcalc(expression1, overwrite = True, quiet = True)    
      #grass.run_command('g.region',rast="MapaBinario")
      #expression2="A=MapaBinario"
      #grass.mapcalc(expression2, overwrite = True, quiet = True)
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
      
      #expression4='MapaBinario_ABCD1=if(MapaBinario_ABCD==0,null(),1)'
      #grass.mapcalc(expression4, overwrite = True, quiet = True)    
      #grass.run_command('r.clump', input='MapaBinario_ABCD1', output="MapaBinario_ABCD1_pid", overwrite = True)
      
      #grass.run_command('r.neighbors', input='MapaBinario_ABCD1_pid', output='MapaBinario_ABCD1_pid_mode', method='mode', size=3, overwrite = True)
      #grass.run_command('r.cross', input=i+"_FRAG"+format_escale_name+'m_mata_clump_pid,MapaBinario_ABCD1_pid_mode',out=i+"_FRAG"+format_escale_name+'m_mata_clump_pid_cross_corredor',overwrite = True)
      #cross_TB = grass.read_command('r.stats', input=i+"_FRAG"+format_escale_name+'m_mata_clump_pid_cross_corredor', flags='l')  # pegando a resolucao
      #print cross_TB 
      #txt=open("table_cross.txt",'w')
      #txt.write(cross_TB)
      #txt.close()
      
      #reclass_frag_cor('MapaBinario_ABCD1_pid', dirout) 
      #expression10='MapaBinario_ABCD1_pid_reclass_sttepings=if(isnull(MapaBinario_ABCD1_pid_reclass)&&temp_BSSC==1,3,MapaBinario_ABCD1_pid_reclass)'
      #grass.mapcalc(expression10, overwrite = True, quiet = True)  
      
      #outputmapSCB=i_in+'_SSCB_deph_'+format_escale_name
      #expression11=outputmapSCB+'=if(temp_BSSC==1,MapaBinario_ABCD1_pid_reclass_sttepings,null())'
      #grass.mapcalc(expression11, overwrite = True, quiet = True) 
      #list_ssbc_maps.append(outputmapSCB)
      
      # If prepare_biodim == True, the list of map names is updated
      if prepare_biodim:
        lista_maps_fid[z,x] = i+"_"+format_escale_name+"m_fid"
        lista_maps_farea[z,x] = i+'_'+format_escale_name+'m_fragment_AreaHA'

      # If export == True and dirout == '', the map is not exported; in other cases, the map is exported in this folder
      if export == True and dirout != '':
        os.chdir(dirout)
        grass.run_command('g.region', rast = i+'_'+format_escale_name+'m_fragment_AreaHA')
        grass.run_command('r.out.gdal', flags = 'c', input = i+'_'+format_escale_name+'m_fragment_AreaHA', output = i+'_'+format_escale_name+'m_fragment_AreaHA.tif', createopt = "TFW=YES,COMPRESS=DEFLATE", overwrite = True)
      # If export_fid == True, the fragment ID map is exported in this folder
      if export_fid == True and dirout != '':
        os.chdir(dirout)
        grass.run_command('g.region', rast = i+"_"+format_escale_name+"m_fid")
        grass.run_command('r.out.gdal', flags = 'c', input = i+"_"+format_escale_name+"m_fid", output = i+"_"+format_escale_name+'m_fid.tif', createopt = "TFW=YES,COMPRESS=DEFLATE", overwrite = True)
      if struct_connec and export_struct_connec:
        os.chdir(dirout)
        grass.run_command('g.region', rast = i+'_'+format_escale_name+'m_structural_connectivity')
        grass.run_command('r.out.gdal', flags = 'c', input = i+'_'+format_escale_name+'m_structural_connectivity', output = i+'_'+format_escale_name+'m_structural_connectivity.tif', createopt = "TFW=YES,COMPRESS=DEFLATE", overwrite = True)        
      
      # If calc_statistics == True, the stats of this metric are calculated and exported
      if calc_statistics:      
        createtxt(i+"_"+format_escale_name+"m_fid", dirout, i+'_'+format_escale_name+'m_fragment_AreaHA')      
      
      # If remove_trash == True, the intermediate maps created in the calculation of patch size are removed
      if remove_trash:
        # Define list of maps
        if zero:
          txts = [i+"_ero_"+format_escale_name+'m', i+"_dila_"+format_escale_name+'m', i+"_FRAG_"+format_escale_name+"m_pos", i+"_FRAG_"+format_escale_name+"m_pos_habitat", i+'_'+format_escale_name+'m_fragment_AreaHA_aux', 'MapaBinario_ABCD1_pid','MapaBinario_ABCD1_pid_reclass','MapaBinario_ABCD1_pid_reclass_sttepings2', 'temp_BSSC','MapaBinario','A','MapaBinario_A','MapaBinario_AB','MapaBinario_ABC','MapaBinario_ABCD','MapaBinario_ABCD1','MapaBinario_ABCD1_pid','MapaBinario_ABCD1_pid_mode', i+'_FRAG'+str(meters)+'m_mata_clump_pid_cross_corredor','MapaBinario_ABCD1_pid_reclass_sttepings']
        else:        
          txts = [i+"_ero_"+format_escale_name+'m', i+"_dila_"+format_escale_name+'m', i+"_FRAG_"+format_escale_name+"m_pos", i+"_FRAG_"+format_escale_name+"m_pos_habitat", 'MapaBinario_ABCD1_pid','MapaBinario_ABCD1_pid_reclass','MapaBinario_ABCD1_pid_reclass_sttepings2', 'temp_BSSC','MapaBinario','A','MapaBinario_A','MapaBinario_AB','MapaBinario_ABC','MapaBinario_ABCD','MapaBinario_ABCD1','MapaBinario_ABCD1_pid','MapaBinario_ABCD1_pid_mode',i+"_FRAG"+str(meters)+'m_mata_clump_pid_cross_corredor','MapaBinario_ABCD1_pid_reclass_sttepings']
        # Remove maps from GRASS GIS location        
        for txt in txts:
          grass.run_command('g.remove', type="raster", name=txt, flags='f')
          
      # Update counter columns (edge depths)
      x = x + 1
    
    # Update counter rows (map names)
    z = z + 1
    
    # Update counter for map names
    cont += 1
 
  #if check_func_edge:
    #cont=0
    #for i in list_ssbc_maps:
      
      #meters=int(edge_depths[cont])  # lista de escalas em metros
      #format_escale_name='0000'+str(meters)
      #format_escale_name=format_escale_name[-4:]   
      #nameaux=i[0:len(input_maps)]
      #outputname=nameaux+'_SSCCB_deph_'+format_escale_name
      #inpmaps=i+','+list_meco[cont]
      
      
      #grass.run_command('r.patch',input=inpmaps,out=outputname,overwrite = True)
      #cont+=1
      
  # If prepare_biodim == True, use the list of output map names to create a text file and export it, for each scale
  if prepare_biodim:
    # For each value in the list of edge depths
    for i in range(len(list_edge_depths)):
      # Create a text file as BioDIM input
      mm = int(list_edge_depths[i])
      create_TXTinputBIODIM(lista_maps_fid[:,i].tolist(), outputfolder = dirout, filename = "simulados_HABMAT_FRAC_"+str(mm)+"m_PID")
      create_TXTinputBIODIM(lista_maps_farea[:,i].tolist(), outputfolder = dirout, filename = "simulados_HABMAT_FRAC_"+str(mm)+"m_AREApix")              


#-------------------------------
# Function percentage
def percentage(input_maps, 
  scale_list, 
  method = 'average',
  append_name = '',
  diagonal_neighbors = True, 
  result_float = False,
  remove_trash = True, 
  export = False, 
  dirout = ''):
  '''
  Function percentage
  
  This function calculates the percentage of a certain variable using a neighborhood analysis.
  Given a list of window sizes, a moving window is applied to the binary input maps and the percentage
  of the variable around the focal pixel is calculated.
  
  Input:
  input_maps: list with strings; each input map corresponds to a binary map (1/0 and NOT 1/null!!) that represents a certain variable.
  scale_list: list with numbers (float or integer); each value correponds to a size for the moving window, in meters, in which the percentage will be calculated.
  method: string; the method calculation performed inside the moving window. For percentages in general the method 'average' is used (stardard), but ir may be set to other values depending on the kind of input variable.
  append_name: string; name to be appended in the output map name. It may be used to distinguish between edge, core, and habitat percentage, for example.
  diagonal_neighbors: (True/False) logical; if True, the moving window in a square and considers diagonals of the central pixel; otherwise, the moving window is a circle (according to r.neighbors rules).
  result_float: (True/False) logical; if True, percentage maps are present floating point (real) numbers; if False (default), percentage maps present integer values.
  remove_trash: (True/False) logical; if True, maps generated in the middle of the calculation are deleted; otherwise they are kept within GRASS.
  export: (True/False) logical; if True, the maps are exported from GRASS.
  dirout: string; folder where the output maps will be saved when exported from GRASS. If '', the output maps are generated but are not exported from GRASS.
               
  Output:
  A map in which each pixel is the percentage of the input variable in a window around it. The size of the window
  is given by the scale provided as input.
  '''
  
  #calc_statistics = False for landscape level?, 
  
  # If we ask to export something but we do not provide an output folder, it shows a warning
  if export and dirout == '':
    warnings.warn("You are trying to export files from GRASS but we did not set an output folder.")  
  
  # For each map in the input list
  for in_map in input_maps: 
    
    # For each scale in the scale list
    for i in scale_list:
    
      # Transform the scale into an integer
      scale = int(i)
      
      # Defines the output name
      # The variable append_name is used to define different percentages, such as habitat, edge, or core percentage
      outputname = in_map+append_name+"_pct_"+str(scale)+"m"
      
      # Define the window size in pixels
      windowsize = get_size_pixels(input_map = in_map, scale_in_meters = scale)
      
      # Define the region
      grass.run_command('g.region', rast = in_map)
      
      # Calculate average value based on the average value (or other method of r.neighbors) of moving window
      if diagonal_neighbors:
        grass.run_command('r.neighbors', input = in_map, select = in_map, output = "temp_PCT", method = method, size = windowsize, overwrite = True)
      else:
        grass.run_command('r.neighbors', input = in_map, select = in_map, output = "temp_PCT", method = method, size = windowsize, overwrite = True, flags = 'c')
      
      # Multiplying by 100 to get a value between 0 and 100%
      if result_float:
        expression1 = outputname+' = temp_PCT * 100' # float values
      else:
        expression1 = outputname+' = int(temp_PCT * 100)' # integer values
        
      grass.mapcalc(expression1, overwrite = True, quiet = True)
      
      # If export == True, export the resulting map
      if export == True and dirout != '':
        os.chdir(dirout)      
        grass.run_command('r.out.gdal', flags = 'c', input = outputname, out = outputname+'.tif', createopt = "TFW=YES,COMPRESS=DEFLATE", overwrite = True)
        
      # If remove_trash == True, remove the maps generated in the process
      if remove_trash:
        grass.run_command('g.remove', type = "raster", name = 'temp_PCT', flags = 'f')


#-------------------------------
# Function functional_connectivity
def functional_connectivity(input_maps, 
                            list_gap_crossing,
                            zero = False, 
                            diagonal = True, 
                            diagonal_neighbors = True,
                            functional_connec = False,
                            functional_area_complete = False,
                            prepare_biodim = False, 
                            calc_statistics = False, 
                            remove_trash = True,
                            prefix = '', 
                            add_counter_name = False, 
                            export = False, 
                            export_pid = False, 
                            dirout = ''):  
  '''
  Function functional_connectivity
  
  This function uses input maps and values of gaps an organism can cross to calculate maps of functional
  connected area, complete functional connected area (if functional_area_complete == True), 
  and functional connectivity (if functional_connec == True). All values are in hectares,
  given the projection uses meters. The default is to calculate only functionally connected area maps.
  - Funtional connected area: each habitat pixel presents a value equals to the sum of all area of all patches
  functionally connected to it.
  - Complete funtional connected area: each habitat pixel presents a value equals to the sum of all area of all patches
  functionally connected to it, plus the surrounding distance in the matrix, defined by the gap crossing distance.
  - Functional connectivity: each habitat pixel presents a value equals to the sum of all area of all patches
  functionally connected to it, minus the size of the habitat patch it is part of.
  It is the same as the map of functionally connected area minus the map of patch size.
  
  Input:
  input_maps: list with strings; a python list with maps loaded in the GRASS GIS location. Must be binary class maps (e.g. maps of habitat-non habitat).
  list_gap_crossing: list with numbers; each value correpond to a distance an organism can cross in the matrix; all habitat patches whose distance is <= this gap crossing distance are considered functionally connected.
  zero: (True/False) logical; if True, non-habitat values are set to zero; otherwise, they are set as null values.
  diagonal: (True/False) logical; if True, cells are clumped also in the diagonal for estimating patch size.
  diagonal_neighbors: (True/False) logical; if True, the moving window in a square and considers diagonals of the central pixel; otherwise, the moving window is a circle (according to r.neighbors rules).
  functional_connec: (True/False) logical; if True, the functional connectivity map is calculated. If gap crossing == 0 is not present in the list of gap crossings, it is added to generate these functional connectivity maps
  functional_area_complete: (True/False) logical; if True, maps of complete functional connectivity area are also generated.
  prepare_biodim: (True/False) logical; if True, maps and input text files for running BioDIM package are prepared.
  calc_statistics: (True/False) logical; if True, statistics are calculated and saved as an output text file.
  remove_trash: (True/False) logical; if True, maps generated in the middle of the calculation are deleted; otherwise they are kept within GRASS.
  prefix: string; a prefix to be appended in the beginning of the output map names.
  add_counter_name: (True/False) logical; if True, a number is attached to the beginning of each outputmap name, in the order of the input, following 0001, 0002, 0003 ...
  export: (True/False) logical; if True, the maps are exported from GRASS.
  export_pid: (True/False) logical; if True, the fragment ID (fid) maps are exported from GRASS.
  dirout: string; folder where the output maps will be saved when exported from GRASS. If '', the output maps are generated but are not exported from GRASS.

  Output:
  For default, only functionally connected area maps are calculated. 
  If functional_connec == True, functional connectivity maps are also calculated. 
  If functional_area_complete, maps of complete functionally connected area are also calculated.
  If prepare_biodim == True, a file with fragment size maps to run BioDIM is generated.
  If calc_statistics == True, a file with area per functionally connected patch in hectares is generated.
  ''' 
  
  # If we ask to export something but we do not provide an output folder, it shows a warning
  if (export or prepare_biodim or calc_statistics) and dirout == '':
    warnings.warn("You are trying to export files from GRASS but we did not set an output folder.")
  
  # If we want to calculate functional connectivity, we need a map for gap crossing = 0
  # Check if 0 is in the the list; if not or if it is but not in the beginning, add it to the beginning
  list_gap_cross = [float(i) for i in list_gap_crossing] # making sure values are float
  if functional_connec:
    if 0 in list_gap_cross and list_gap_cross[0] != 0:
      list_gap_cross.remove(0)
      list_gap_cross.insert(0, 0)
    elif not (0 in list_gap_cross):
      list_gap_cross.insert(0, 0)
  
  # If prepare_biodim == True, lists of map names of Fragment ID and area are initialized
  # Theses lists here are matrices with input maps in rows and edge depths in columns  
  if prepare_biodim:
    # Functional connected area (clean) maps are always saved
    lista_maps_pid_clean = np.empty((len(input_maps), len(list_gap_cross)), dtype=np.dtype('a200'))
    lista_maps_area_clean = np.empty((len(input_maps), len(list_gap_cross)), dtype=np.dtype('a200'))
    
    # If functional_area_complete == True, these maps are also saved as BioDIM input
    if functional_area_complete:
      lista_maps_pid_comp = np.empty((len(input_maps), len(list_gap_cross)), dtype=np.dtype('a200'))
      lista_maps_area_comp = np.empty((len(input_maps), len(list_gap_cross)), dtype=np.dtype('a200'))      
  
  # Initialize counter of map name for lists of map names
  z = 0
  
  # Initialize counter, in case the user wants to add a number to the map name
  cont = 1
  
  # For each map in the list of input maps
  for i_in in input_maps:
    
    # Putting (or not) a prefix in the beginning of the output map name
    if not add_counter_name:
      pre_numb = ''
    else: # adding numbers in case of multiple maps
      pre_numb = '00000'+str(cont)+'_'
      pre_numb = pre_numb[-5:]
      
    # Prefix of the output
    i = prefix+pre_numb+i_in
    
    # Define the region
    grass.run_command('g.region', rast = i_in)
    
    # Calculate gap crossing distances in number of pixels, based on input values in meters
    list_dilatate_meters, list_dilatate_pixels = connectivity_scales(input_map = i_in, list_gap_crossing = list_gap_cross)
    
    # Initialize counter of gap crossing value for lists of map names
    x = 0
    
    # For each value in the list of gap crossing distances
    for a in list_dilatate_pixels:
      
      meters = int(2*list_dilatate_meters[x])  # should we use the input list_gap_cross instead? only list_gap_cross[x]  
      
      # Prefix for map names regarding scale
      format_escale_name = '0000'+str(meters)
      format_escale_name = format_escale_name[-4:]
        
      # Whether or not to consider diagonal when dilatating pixels
      if diagonal_neighbors:
        flags_neighbors = ''
      else:
        flags_neighbors = 'c'
        
      # Uses a moving window to dilatate/enlarge habitat patches, by considering the maximum value within a window
      grass.run_command('r.neighbors', input = i_in, output = i+"_dila_"+format_escale_name+'m_orig', method = 'maximum', size = a, overwrite = True, flags = flags_neighbors)
      
      # Set zero values as null
      expression1 = i+"_dila_"+format_escale_name+'m_orig_temp = if('+i+"_dila_"+format_escale_name+'m_orig == 0, null(), '+i+"_dila_"+format_escale_name+'m_orig)'
      grass.mapcalc(expression1, overwrite = True, quiet = True)
      
      # Clump pixels that are contiguous in the same functionally connected patch ID - the complete PID with matrix pixels
      if diagonal:
        grass.run_command('r.clump', input = i+"_dila_"+format_escale_name+'m_orig_temp', output = i+"_"+format_escale_name+'m_func_connect_complete_pid', overwrite = True, flags = 'd')
      else:
        grass.run_command('r.clump', input = i+"_dila_"+format_escale_name+'m_orig_temp', output = i+"_"+format_escale_name+'m_func_connect_complete_pid', overwrite = True)
      
      # Take only values within the original habitat
      expression2 = i+"_"+format_escale_name+'m_func_connect_complete_pid_habitat = '+i_in+'*'+i+"_"+format_escale_name+'m_func_connect_complete_pid'
      grass.mapcalc(expression2, overwrite = True, quiet = True)
      
      # Transform no habitat values in null() - this is the clean patch ID for functionally connected patches
      expression3 = i+"_"+format_escale_name+'m_func_connect_pid = if('+i+"_"+format_escale_name+'m_func_connect_complete_pid_habitat > 0, '+i+"_"+format_escale_name+'m_func_connect_complete_pid_habitat, null())'
      grass.mapcalc(expression3, overwrite = True, quiet = True)
      
      # Reclass pixel id values by calculating the area in hectares
      if dirout != '':
        os.chdir(dirout) # folder to save temp reclass file
      # Define region
      grass.run_command('g.region', rast = i+"_"+format_escale_name+'m_func_connect_pid')      
      
      # If zero == False (non-habitat cells are considered null)
      if zero == False:        
        nametxtreclass = rulesreclass(i+"_"+format_escale_name+'m_func_connect_pid', outputfolder = '.')
        grass.run_command('r.reclass', input = i+"_"+format_escale_name+'m_func_connect_pid', output = i+"_"+format_escale_name+'m_func_connect_AreaHA', rules = nametxtreclass, overwrite = True)
        
        # If functional_area_complete == True, the area of complete maps (dilatated maps, considering the matrix pixels) is also calculated - their area is equal to the functionally connected area maps
        if functional_area_complete and list_gap_cross[x] != 0:       
          grass.run_command('r.reclass', input = i+"_"+format_escale_name+'m_func_connect_complete_pid', output=i+"_"+format_escale_name+'m_func_connect_complete_AreaHA', rules=nametxtreclass, overwrite = True)
          
        # Remove reclass file
        os.remove(nametxtreclass)
        
      # If zero == True (non-habitat cells are considered as zeros)
      else: 
        nametxtreclass = rulesreclass(i+"_"+format_escale_name+'m_func_connect_pid', outputfolder = '.')
        grass.run_command('r.reclass', input = i+"_"+format_escale_name+'m_func_connect_pid', output = i+"_"+format_escale_name+'m_func_connect_AreaHA_aux', rules = nametxtreclass, overwrite = True)
        
        # Transforms what is 1 in the binary map into the patch size
        expression4 = i+"_"+format_escale_name+'m_func_connect_AreaHA = if('+i_in+' == 0, 0, '+i+'_'+format_escale_name+'m_func_connect_AreaHA_aux)'
        grass.mapcalc(expression4, overwrite = True)
        
        # If functional_area_complete == True, the area of complete maps (dilatated maps, considering the matrix pixels) is also calculated - their area is equal to the functionally connected area maps
        if functional_area_complete and list_gap_cross[x] != 0:        
          grass.run_command('r.reclass', input = i+"_"+format_escale_name+'m_func_connect_complete_pid', output=i+"_"+format_escale_name+'m_func_connect_complete_AreaHA_aux', rules=nametxtreclass, overwrite = True)
      
          # Transforms what is 1 in the binary map into the patch size
          expression5 = i+"_"+format_escale_name+'m_func_connect_complete_AreaHA = if('+i_in+' == 0, 0, '+i+"_"+format_escale_name+'m_func_connect_complete_AreaHA_aux)'
          grass.mapcalc(expression5, overwrite = True)
        
        # Remove reclass file
        os.remove(nametxtreclass)
        
      
      # Save the name of the functional area map in case the gap crossing == 0:
      if list_gap_cross[x] == 0:
        name_map_gap_crossing_0 = i+"_"+format_escale_name+'m_func_connect_AreaHA'
        
      ## If functional_area_complete == True, the area of complete maps (dilatated maps, considering the matrix pixels) is also calculated
      #if functional_area_complete and list_gap_cross[x] != 0:
        
        ## If zero == False (non-habitat cells are considered null)
        #if zero == False:          
          #nametxtreclass = rulesreclass(i+"_"+format_escale_name+'m_func_connect_complete_pid', '.')
          #grass.run_command('r.reclass', input = i+"_"+format_escale_name+'m_func_connect_complete_pid', output=i+"_"+format_escale_name+'m_func_connect_complete_AreaHA', rules=nametxtreclass, overwrite = True)
          #os.remove(nametxtreclass)
        #else: # If zero == True (non-habitat cells are considered as zeros)
          #nametxtreclass = rulesreclass(i+"_"+format_escale_name+'m_func_connect_complete_pid', '.')
          #grass.run_command('r.reclass', input = i+"_"+format_escale_name+'m_func_connect_complete_pid', output=i+"_"+format_escale_name+'m_func_connect_complete_AreaHA_aux', rules=nametxtreclass, overwrite = True)
          #os.remove(nametxtreclass)
      
          ## Transforms what is 1 in the binary map into the patch size
          #expression5 = i+"_"+format_escale_name+'m_func_connect_complete_AreaHA = if('+i_in+' == 0, 0, '+i+"_"+format_escale_name+'m_func_connect_complete_AreaHA_aux)'
          #grass.mapcalc(expression5, overwrite = True)      
      
      # If functional_connect == True, calculate map of functional connectivity
      # This map equals functional_area - funcional_area(gap_crossing == 0)
      if functional_connec and list_gap_cross[x] != 0:
        
        # Should we check here or somewhere if the map for gap crossing == 0 was really generated?
        expression6 = i+'_'+format_escale_name+'m_functional_connectivity = '+i+'_'+format_escale_name+'m_func_connect_AreaHA - '+name_map_gap_crossing_0
        grass.mapcalc(expression6, overwrite = True)         
      
      # If prepare_biodim == True, the list of map names is updated
      if prepare_biodim:
        lista_maps_pid_clean[z,x] = i+"_"+format_escale_name+'m_func_connect_pid'
        lista_maps_area_clean[z,x] = i+"_"+format_escale_name+'m_func_connect_AreaHA'        
        
        # If functional_area_complete == True, these maps are also saved as BioDIM input
        if functional_area_complete:
            lista_maps_pid_comp[z,x] = i+"_"+format_escale_name+'m_func_connect_complete_pid'
            lista_maps_area_comp[z,x] = i+"_"+format_escale_name+'m_func_connect_complete_AreaHA'            
  
      # If export == True and dirout == '', the map is not exported; in other cases, the map is exported in this folder
      # For gap crossing == 0, maps are not exported
      if export == True and dirout != '' and list_gap_cross[x] != 0:
        os.chdir(dirout) 
        grass.run_command('g.region', rast = i+"_"+format_escale_name+'m_func_connect_AreaHA')
        grass.run_command('r.out.gdal', flags = 'c', input = i+"_"+format_escale_name+'m_func_connect_AreaHA', output = i+"_"+format_escale_name+'m_func_connect_AreaHA.tif', createopt = "TFW=YES,COMPRESS=DEFLATE", overwrite = True)
        
        # If functional_area_complete == True, these maps are also exported
        if functional_area_complete:        
          grass.run_command('r.out.gdal', flags = 'c', input = i+"_"+format_escale_name+'m_func_connect_complete_AreaHA', output = i+"_"+format_escale_name+'m_func_connect_complete_AreaHA.tif', createopt = "TFW=YES,COMPRESS=DEFLATE", overwrite = True)
          
        # If functional_connec == True, the functional connectivity maps are also exported
        if functional_connec:
          grass.run_command('r.out.gdal', flags = 'c', input = i+'_'+format_escale_name+'m_functional_connectivity', output = i+'_'+format_escale_name+'m_functional_connectivity.tif', createopt = "TFW=YES,COMPRESS=DEFLATE", overwrite = True)
      
      # If export_fid == True, the fragment ID map is exported in this folder
      if export_pid == True and dirout != '' and list_gap_cross[x] != 0:
        os.chdir(dirout)
        grass.run_command('g.region', rast = i+"_"+format_escale_name+'m_func_connect_pid')
        grass.run_command('r.out.gdal', flags = 'c', input = i+"_"+format_escale_name+'m_func_connect_pid', output = i+"_"+format_escale_name+'m_func_connect_pid.tif', createopt = "TFW=YES,COMPRESS=DEFLATE", overwrite = True)
        
        # If functional_area_complete == True, these maps are also exported
        if functional_area_complete and list_gap_cross[x] != 0:        
          grass.run_command('r.out.gdal', flags = 'c', input = i+"_"+format_escale_name+'m_func_connect_complete_pid', output = i+"_"+format_escale_name+'m_func_connect_complete_pid.tif', createopt = "TFW=YES,COMPRESS=DEFLATE", overwrite = True)
            
      # If calc_statistics == True, the stats of this metric are calculated and exported
      if calc_statistics and list_gap_cross[x] != 0:
        createtxt(i+"_"+format_escale_name+'m_func_connect_pid', outputfolder = dirout, filename = i+"_"+format_escale_name+'m_func_connect_AreaHA')
        # If functional_area_complete == True, these statistics are also calculated
        if functional_area_complete:          
          createtxt(i+"_"+format_escale_name+'m_func_connect_complete_pid', outputfolder = dirout, filename = i+"_"+format_escale_name+'m_func_connect_complete_AreaHA')
      
      # If remove_trash == True, the intermediate maps created in the calculation of patch size are removed
      if remove_trash:
        # Define list of maps
        if functional_area_complete and list_gap_cross[x] != 0:
          txts = [i+"_dila_"+format_escale_name+'m_orig', i+"_dila_"+format_escale_name+'m_orig_temp', i+"_"+format_escale_name+'m_func_connect_complete_pid_habitat']
        else:
          txts = [i+"_dila_"+format_escale_name+'m_orig', i+"_dila_"+format_escale_name+'m_orig_temp', i+"_"+format_escale_name+'m_func_connect_complete_pid', i+"_"+format_escale_name+'m_func_connect_complete_pid_habitat'] #, i+"_"+format_escale_name+'m_func_connect_pid']
        if zero == True:
          txts.append(i+"_"+format_escale_name+'m_func_connect_AreaHA_aux')
          if functional_area_complete and list_gap_cross[x] != 0:
            txts.append(i+"_"+format_escale_name+'m_func_connect_complete_AreaHA_aux')
        if functional_connec and a == list_dilatate_pixels[-1]:
          format_escale_name = '000000'
          format_escale_name = format_escale_name[-4:]          
          txts = txts + [i+"_"+format_escale_name+'m_func_connect_AreaHA', i+"_"+format_escale_name+'m_func_connect_pid']
        # Remove maps from GRASS GIS location     
        for txt in txts:
          grass.run_command('g.remove', type='raster', name=txt, flags='f')
      
      # Update counter columns (gap crossing values)    
      x = x + 1
    
    # Update counter rows (map names)  
    z = z + 1
    
    # Update counter for map names
    cont += 1
    
  # If prepare_biodim == True, use the list of output map names to create a text file and export it, for each scale
  if prepare_biodim:
    # For each value in the list of gap crossing
    for i in range(len(list_gap_cross)):
      # Create a text file as BioDIM input
      mm = int(list_gap_cross[i])
      if mm != 0: # Do not export for gap crossing == 0
        create_TXTinputBIODIM(lista_maps_pid_clean[:,i].tolist(), outputfolder = dirout, filename = "simulados_HABMAT_grassclump_dila_"+str(mm)+"m_clean_PID")
        create_TXTinputBIODIM(lista_maps_area_clean[:,i].tolist(), outputfolder = dirout, filename = "simulados_HABMAT_grassclump_dila_"+str(mm)+"m_clean_AREApix")
        # If functional_area_complete == True, these statistics are also calculated
        if functional_area_complete:
          create_TXTinputBIODIM(lista_maps_pid_comp[:,i].tolist(), outputfolder = dirout, filename = "simulados_HABMAT_grassclump_dila_"+str(mm)+"m_complete_PID")
          create_TXTinputBIODIM(lista_maps_area_comp[:,i].tolist(), outputfolder = dirout, filename = "simulados_HABMAT_grassclump_dila_"+str(mm)+"m_complete_AREApix")                      
      
      
#----------------------------------------------------------------------------------
# Metrics for habiat edges

#-------------------------------
# Function edge_core
def edge_core(input_maps, 
              list_edge_depths,
              diagonal = True, 
              diagonal_neighbors = True,
              calc_edge_core_area = False,
              calc_percentage = False, 
              window_size = [], 
              method_percentage = 'average',
              calc_statistics = False, 
              remove_trash = True,
              prefix = '', 
              add_counter_name = False, 
              export = False, 
              export_pid = False, 
              dirout = ''):
  '''
  Function edge_core
  
  This function separates habitat area into edge and interior/core regions, given a scale/distance defined 
  as edge depth. Then, it generates a matrix-edge-core (MECO) map, a binary edge/non-edge map, and a
  binary core/non-core map. It may also generate a map of edge and core clump areas (if calc_edge_core_area == True), 
  and calculate the percentage of edge and core within a window around each pixel, given the size of this window.
  
  Input:
  input_maps: list with strings; a python list with maps loaded in the GRASS GIS location. Must be binary class maps (e.g. maps of habitat-non habitat).
  list_edge_depths: list with numbers; each value correpond to an edge depth; it is used to classify pixels distant less than this depth from the edges and edge pixels.
  diagonal: (True/False) logical; if True, clumps of edge and core areas are made considering the diagonal (in r.clump).
  diagonal_nieghbors: (True/False) logical; if True, neighborhood analysis for identifying edges include the diagonal of central pixels.
  calc_edge_core_area: (True/False) logical; if True, the area of edge and core clumps, after identified, is also calculated. Patch IDs for each clump are also identified.
  calc_percentage: (True/False) logical; if True, the maps of edge and core are used to calculate the proportion of edge and core around each pixel, given a moving window size for the analysis. The percentage analysis is performed by the function percentage().
  window_size: list with numbers; each value correpond to a size for the moving window used to calculate proportion of edge and core; values are given in meters.
  method_percentage: string; method used to calculate the proportion of edge and core. The default is 'average'.
  calc_statistics: (True/False) logical; if True, statistics are calculated and saved as an output text file.
  remove_trash: (True/False) logical; if True, maps generated in the middle of the calculation are deleted; otherwise they are kept within GRASS.
  prefix: string; a prefix to be appended in the beginning of the output map names.
  add_counter_name: (True/False) logical; if True, a number is attached to the beginning of each outputmap name, in the order of the input, following 0001, 0002, 0003 ...
  export: (True/False) logical; if True, the maps are exported from GRASS.
  export_pid: (True/False) logical; if True, and if calc_edge_core_area, the ID of each clump of edge and core maps are exported from GRASS.
  dirout: string; folder where the output maps will be saved when exported from GRASS. If '', the output maps are generated but are not exported from GRASS.
  
  Output:
  The default output is three output maps per input map and per edge depth value:
  - MECO: map identifying matrix-edge-core; matrix = 0, edge = 4, and core = 5.
  - EDGE: binary map identifying edges; edge = 1, non-edge = 0.
  - CORE: binary map identifying core areas; core = 1, non-core = 0.
  If calc_edge_core_area == True, the function also clumps contiguous pixels of edge and core in "patches" of
  edge and core, and generates Patch ID and Area (in hectares) maps for edge and core clumps. 
  One map of patch ID and area is generated for each input map and each edge depth value.
  If calc_percentage == True, binary EDGE and CORE maps are used to calculate maps of proportion of edge and core
  around each pixel, given a window size of analysis.
  One map of edge/core proportion is generated for each input map, each edge depth value, and each window size.
  If calc_statistics == True, files with statistics are generated. The dafault is to calculate the area of matrix (0),
  edge (4), and core (5) in each input landscape.
  If calc_edge_core_area == True, the area of each edge and core clump is also calculated.
  '''
  
  # If we ask to export something but we do not provide an output folder, it shows a warning
  if (export or calc_statistics) and dirout == '':
    warnings.warn("You are trying to export files from GRASS but we did not set an output folder.")
    
  # If the list of window sizes is empty and the user wants to calculate proportion of edge/core
  if calc_percentage and len(window_size) == 0:
    raise Warning('At least one value of window size should be provided to calculate proportion of edge/core.')
  
  # Initialize counter, in case the user wants to add a number to the map name
  cont = 1
  
  ##############################
  # will we use that?
  list_meco = [] # list of matrix-edge-core map names

  # For each map in the list of input maps
  for i_in in input_maps:
    
    # Putting (or not) a prefix in the beginning of the output map name
    if not add_counter_name:
      pre_numb = ''
    else: # adding numbers in case of multiple maps
      pre_numb = '00000'+str(cont)+'_'
      pre_numb = pre_numb[-5:]
    
    # Prefix of the output    
    i = prefix+pre_numb+i_in
    
    # Define the region    
    grass.run_command('g.region', rast = i_in)
    
    # Calculate edge depths and corridor widths to be subtracted from connections between patches
    edge_depths, list_corridor_width_pixels = frag_scales(i_in, list_edge_depths)    
    
    # Initialize counter of edge depth value
    cont_scale = 0
    
    # For each value in the list of corridor widths
    for size in list_corridor_width_pixels:
      meters = int(edge_depths[cont_scale]) # edge depth in meters
      
      # Prefix for map names regarding scale
      format_escale_name = '0000'+str(meters)
      format_escale_name = format_escale_name[-4:]
      
      # Defining output names for classification maps
      outputname_meco = i+'_MECO_'+format_escale_name+'m' # name of the matrix-edge-core map
      outputname_core = i+'_CORE_'+format_escale_name+'m' # name of the core map
      outputname_edge = i+'_EDGE_'+format_escale_name+'m' # name of the edge map
      
      # Defining output names for PID and area maps
      core_pid_mapname = i+'_CORE_'+format_escale_name+'m_pid'
      core_area_mapname = i+'_CORE_'+format_escale_name+'m_AreaHA'
      edge_pid_mapname = i+'_EDGE_'+format_escale_name+'m_pid'
      edge_area_mapname = i+'_EDGE_'+format_escale_name+'m_AreaHA'
      
      # Append matriz-edge-core map name to the list
      list_meco.append(outputname_meco)
      
      # Degrading map by edge depth
      if diagonal_neighbors:
        grass.run_command('r.neighbors', input = i_in, output = i+"_eroED_"+format_escale_name+'m', method = 'minimum', size = size, overwrite = True)
      else:
        grass.run_command('r.neighbors', input = i_in, output = i+"_eroED_"+format_escale_name+'m', method = 'minimum', size = size, overwrite = True, flags = 'c')
      
      # Input for gathering maps for r.series - input map (1/0) and degraded map
      inputs = i+"_eroED_"+format_escale_name+'m,'+i_in
      outputs = i+'_EDGE_'+format_escale_name+'m_temp1' # First output
      outputs2 = i+'_EDGE_'+format_escale_name+'m_temp2' # Second output
      
      # Summing values. In the output, 0 = matrix, 1 = edge, and 2 = core
      grass.run_command('r.series', input = inputs, output = outputs, method = 'sum', overwrite = True)
      
      # Transforming the result in only integer values (is it necessary?)
      #espressaoEd=i+'_EDGE'+str(format_escale_name)+'m_temp2 = int('+i+'_EDGE_'+str(format_escale_name)+'m_temp1)' # criando uma mapa inteiro
      #grass.mapcalc(espressaoEd, overwrite = True, quiet = True)
           
      # Maintaining only values in which we had positive values in the input map. This is necessary because r.neighbors dilatates the map extension
      expression_clip = outputs2+' = if('+i_in+' >= 0, '+outputs+', null())'
      grass.mapcalc(expression_clip, overwrite = True, quiet = True)  
      
      # Generating the matrix-edge-core map. In the output, 0 = matrix, 4 = edge, and 5 = core
      expression_meco = outputname_meco+' = if('+outputs2+' == 0, 0) | if('+outputs2+' == 1, 4) | if('+outputs2+' == 2, 5)'
      grass.mapcalc(expression_meco, overwrite = True, quiet = True)
      
      # Generating core map. In the output, 1 = core, 0 = non-core.
      expression_core = outputname_core+' = if('+outputs2+' == 2, 1, 0)'
      grass.mapcalc(expression_core, overwrite = True, quiet = True)     
      
      # Generating edge map. In the output, 1 = edge, 0 = non-edge.
      expression_edge = outputname_edge+' = if('+outputs2+' == 1, 1, 0)'
      grass.mapcalc(expression_edge, overwrite = True, quiet = True)  
      
      # Calculating edge and core area
      if calc_edge_core_area:
        
        # Folder for saving reclass files
        if dirout != '':
          os.chdir(dirout)
          
        # Define region
        grass.run_command('g.region', rast = outputname_core)        
        
        if diagonal:
          flags_clump = 'd'
        else:
          flags_clump = ''
        
        # core pid
        expression1 = outputname_core+'_1_null = if('+outputname_core+' >= 1, '+outputname_core+', null())'
        grass.mapcalc(expression1, overwrite = True, quiet = True)
        # clump
        grass.run_command('r.clump', input = outputname_core+'_1_null', output = core_pid_mapname, overwrite = True, flags = flags_clump)
        
        # core area
        nametxtreclass = rulesreclass(core_pid_mapname, outputfolder = '.')
        grass.run_command('r.reclass', input = core_pid_mapname, output = core_area_mapname, rules=nametxtreclass, overwrite = True)   
        os.remove(nametxtreclass)
        
        # edge pid
        expression1 = outputname_edge+'_1_null = if('+outputname_edge+' >= 1, '+outputname_edge+', null())'
        grass.mapcalc(expression1, overwrite = True, quiet = True)
        # clump
        grass.run_command('r.clump', input = outputname_edge+'_1_null', output = edge_pid_mapname, overwrite = True, flags = flags_clump)
        
        # edge area
        nametxtreclass = rulesreclass(edge_pid_mapname, outputfolder = '.')
        grass.run_command('r.reclass', input = edge_pid_mapname, output = edge_area_mapname, rules=nametxtreclass, overwrite = True)   
        os.remove(nametxtreclass)
        
      # If export == True and dirout == '', the maps are not exported; in other cases, the map are exported in this folder
      if export == True and dirout != '':
        os.chdir(dirout)
        # Export matrix-edge-core map
        grass.run_command('r.out.gdal', flags = 'c', input = outputname_meco, output = outputname_meco+'.tif', createopt = "TFW=YES,COMPRESS=DEFLATE", overwrite = True) 
        # Export edge map
        grass.run_command('r.out.gdal', flags = 'c', input = outputname_edge, output = outputname_edge+'.tif', createopt = "TFW=YES,COMPRESS=DEFLATE", overwrite = True)
        # Export core map
        grass.run_command('r.out.gdal', flags = 'c', input = outputname_core, output = outputname_core+'.tif', createopt = "TFW=YES,COMPRESS=DEFLATE", overwrite = True)
        
        # If the areas were calculated, export them too
        if calc_edge_core_area:
          # Export edge area clumps
          grass.run_command('r.out.gdal', flags = 'c', input = edge_area_mapname, output = edge_area_mapname+'.tif', createopt = "TFW=YES,COMPRESS=DEFLATE", overwrite = True)          
          # Export core area clumps
          grass.run_command('r.out.gdal', flags = 'c', input = core_area_mapname, output = core_area_mapname+'.tif', createopt = "TFW=YES,COMPRESS=DEFLATE", overwrite = True)
          
          # If export_pid == True, export pid maps too
          if export_pid:
            # Export edge pid
            grass.run_command('r.out.gdal', flags = 'c', input = edge_pid_mapname, output = edge_pid_mapname+'.tif', createopt = "TFW=YES,COMPRESS=DEFLATE", overwrite = True)          
            # Export core pid
            grass.run_command('r.out.gdal', flags = 'c', input = core_pid_mapname, output = core_pid_mapname+'.tif', createopt = "TFW=YES,COMPRESS=DEFLATE", overwrite = True)            
        
      # If calc_percentage == True, calculate proportion of core and edge according to the input window sizes
      if calc_percentage and len(window_size) >= 1:
        
        # edge proportion
        percentage(input_maps = [outputname_edge], scale_list = window_size, method = method_percentage, append_name = '', diagonal_neighbors = diagonal_neighbors,
                   remove_trash = remove_trash, export = export, dirout = dirout)
        # core proportion
        percentage(input_maps = [outputname_core], scale_list = window_size, method = method_percentage, append_name = '', diagonal_neighbors = diagonal_neighbors,
                   remove_trash = remove_trash, export = export, dirout = dirout)           
            
      # If calc_statistics == True, the stats of this metric are calculated and exported
      if calc_statistics:
        createtxt(outputname_meco, dirout, i+'_MATRIX_EDGE_CORE_'+format_escale_name+'m')
        
        # calc_edge_core_area == True, calculate also for clumps of edges and cores
        if calc_edge_core_area:
          # edge area
          createtxt(edge_pid_mapname, dirout, edge_area_mapname)
          # core area
          createtxt(core_pid_mapname, dirout, core_area_mapname)

      # If remove_trash == True, the intermediate maps created in the calculation of patch size are removed
      if remove_trash:
        txts = [i+"_eroED_"+format_escale_name+'m', outputs, outputs2]
        if calc_edge_core_area:
          txts = txts + [outputname_core+'_1_null', outputname_edge+'_1_null']
        grass.run_command('g.remove', type = 'raster', name = ','.join(str(e) for e in txts), flags = 'f')
      
      # Update counter for edge depths
      cont_scale +=1
      
    # Update counter for map names
    cont += 1
    
  # Return the list of matrix-edge-core map names
  return list_meco


#-------------------------------
# Function dist_edge
def dist_edge(input_maps,
              classify_edge_as_zero = False,
              prepare_biodim = False, 
              remove_trash = True,
              prefix = '', 
              add_counter_name = False, 
              export = False, 
              dirout = ''):
  '''
  Function dist_edge
  
  This function calculates the distance of each pixel to the nearest habitat edges, considering
  negative values (inside patches) and positive values (into the matrix). It 
  generates and exports maps of distance to edge (if export == True), and prepare files for BioDIM
  (if premore_biodim)
  
  Input:
  input_maps: list with strings; a python list with maps loaded in the GRASS GIS location. Must be binary class maps (e.g. maps of habitat-non habitat).
  classify_edge_as_zero: (True/False) logical; if True, distant from edge = 0 for pixels within habitat and adjacent to the edge; otherwise, their distance equals pixel size.
  prepare_biodim: (True/False) logical; if True, maps and input text files for running BioDIM package are prepared.
  remove_trash: (True/False) logical; if True, maps generated in the middle of the calculation are deleted; otherwise they are kept within GRASS.
  prefix: string; a prefix to be appended in the beginning of the output map names.
  add_counter_name: (True/False) logical; if True, a number is attached to the beginning of each outputmap name, in the order of the input, following 0001, 0002, 0003 ...
  export: (True/False) logical; if True, the maps are exported from GRASS.
  dirout: string; folder where the output maps will be saved when exported from GRASS. If '', the output maps are generated but are not exported from GRASS.
  
  Output:
  Maps distance to the nearest edge, in map units (preferentially in meters). Positive values are matrix,
  negative values are within habitat. If classify_edge_as_zero == True, the edge values are zero.
  If prepare_biodim == True, a file with map names of distance to edges to run BioDIM is generated.
  '''
  
  # If we ask to export something but we do not provide an output folder, it shows a warning
  if (export or prepare_biodim) and dirout == '':
    warnings.warn("You are trying to export files from GRASS but we did not set an output folder.")  
  
  # If prepare_biodim == True, a list of map names of distance to habitat edge is created
  if prepare_biodim:
    list_maps_dist = []    
  
  # Initialize counter, in case the user wants to add a number to the map name
  cont = 1
  
  # For each map in the list of input maps
  for i_in in input_maps:
    
    # Putting (or not) a prefix in the beginning of the output map name
    if not add_counter_name:
      pre_numb = ''
    else: # adding numbers in case of multiple maps
      pre_numb = '00000'+str(cont)+'_'
      pre_numb = pre_numb[-5:]

    # Prefix of the output
    i = prefix+pre_numb+i_in

    # Define region
    grass.run_command('g.region', rast=i_in)
    
    # Based on the input habitat map, identify what is not habitat and set the habitat to null()
    expression1 = i+'_invert = if('+i_in+' == 0, 1, null())'
    grass.mapcalc(expression1, overwrite = True, quiet = True)
    
    # If classify_edge_as_zero == False, simply calculate distance from edge
    if classify_edge_as_zero == False:
      # Calculate distance from pixels in the habitat cells to the nearest habitat edges
      grass.run_command('r.grow.distance', input = i+'_invert', distance = i+'_invert_habitat_neg_eucldist', overwrite = True)
    
    # If classify_edge_as_zero == True, decrease the distance values within habitat by the pixel size, so that 
    # values in the edge are zero
    else:
      # Calculate distance from pixels in the habitat cells to the nearest habitat edges
      grass.run_command('r.grow.distance', input = i+'_invert', distance = i+'_invert_habitat_neg_eucldist_aux', overwrite = True)      
      
      # Take only positive values of distance within habitat
      expression1_1 = i+'_invert_habitat_neg_eucldist_positive_vals = if('+i+'_invert_habitat_neg_eucldist_aux > 0, '+i+'_invert_habitat_neg_eucldist_aux, null())'
      grass.mapcalc(expression1_1, overwrite = True, quiet = True)
      
      # Get minimum value of distance (should be equal or very similar to the pixel size)
      within_hab_dist_info = grass.read_command('r.univar', map = i+'_invert_habitat_neg_eucldist_positive_vals')
      min_text = filter(lambda x: 'minimum' in x, within_hab_dist_info.split('\n'))[0]
      min_float = float(min_text.replace('minimum:',''))
      
      # Decrease all distance values by the minimum value
      expression1_2 = i+'_invert_habitat_neg_eucldist = if('+i+'_invert_habitat_neg_eucldist_aux <= '+str(min_float)+', 0, '+i+'_invert_habitat_neg_eucldist_aux - '+str(min_float)+')'
      grass.mapcalc(expression1_2, overwrite = True, quiet = True)           
    
    # Based on the input habitat map, identify what is habitat and set the matrix to null()
    expression2 = i+'_invert_matrix = if('+i_in+' == 0, null(), 1)'
    grass.mapcalc(expression2, overwrite = True, quiet = True)
    
    # Calculate distance from pixels in the non-habitat cells to the nearest habitat edges
    grass.run_command('r.grow.distance', input=i+'_invert_matrix', distance=i+'_invert_matrix_pos_eucldist',overwrite = True)
    
    # Final distance to edge = positive distance in the matrix - negative distance within habitat
    expression3 = i+'_edge_dist = '+i+'_invert_matrix_pos_eucldist - '+i+'_invert_habitat_neg_eucldist'
    grass.mapcalc(expression3, overwrite = True, quiet = True)

    # Final distance to edge = positive distance in the matrix - negative distance within habitat
    expression4 = i+'_edge_dist = if(isnull('+i+'), null(), '+i+'_edge_dist)'
    grass.mapcalc(expression4, overwrite = True, quiet = True)

    expression5 = i+'_edge_dist_inside = if('+i+'_edge_dist <= 0, '+i+'_edge_dist, null())'
    grass.mapcalc(expression5, overwrite = True, quiet = True)

    expression6 = i+'_edge_dist_outside = if('+i+'_edge_dist > 0, '+i+'_edge_dist, null())'
    grass.mapcalc(expression6, overwrite = True, quiet = True)

    # Define colors for the map
    grass.run_command('r.colors', map = i+'_edge_dist', color = 'viridis')
    grass.run_command('r.colors', map = i+'_edge_dist_inside', color = 'viridis')
    grass.run_command('r.colors', map = i+'_edge_dist_outside', color = 'viridis')
  
    # If biodim_prepare == True,  the list of map names is updated
    if prepare_biodim:
      list_maps_dist.append(i+'_edge_dist')
      
    # If export == True and dirout == '', the map is not exported; in other cases, the map is exported in this folder
    if export == True and dirout != '':
      os.chdir(dirout)
      grass.run_command('r.out.gdal', flags = 'c', input = i+'_edge_dist', out = i+'_EDGE_DIST.tif', createopt = "TFW=YES,COMPRESS=DEFLATE", overwrite = True)
      grass.run_command('r.out.gdal', flags = 'c', input = i+'_edge_dist_inside', out = i+'_EDGE_DIST_INSIDE.tif', createopt = "TFW=YES,COMPRESS=DEFLATE", overwrite = True)
      grass.run_command('r.out.gdal', flags = 'c', input = i+'_edge_dist_outside', out = i+'_EDGE_DIST_OUTSIDE.tif', createopt = "TFW=YES,COMPRESS=DEFLATE", overwrite = True)
      
    # If remove_trash == True, the intermediate maps created in the calculation of patch size are removed
    if remove_trash:
      # Define list of maps
      txts = [i+'_invert', i+'_invert_habitat_neg_eucldist', i+'_invert_matrix', i+'_invert_matrix_pos_eucldist']
      if classify_edge_as_zero:
        txts = txts + [i+'_invert_habitat_neg_eucldist_aux', i+'_invert_habitat_neg_eucldist_positive_vals']
      # Remove maps from GRASS GIS location
      for txt in txts:
        grass.run_command('g.remove', type = "raster", name = txt, flags = 'f')
    
    # Update counter of the map number
    cont += 1
    
  # If prepare_biodim == True, use the list of output map names to create a text file and export it
  if prepare_biodim:
    create_TXTinputBIODIM(list_maps_dist, dirout, "simulados_HABMAT_DIST")
    
    
#----------------------------------------------------------------------------------
# Metrics for landscape heterogeneity/diversity

#-------------------------------
# Function landscape_diversity
def landscape_diversity(input_maps, 
                        scale_list, 
                        method = ['simpson'], 
                        alpha = [],
                        append_name = '', 
                        current_mapset = 'PERMANENT',
                        export = False, 
                        dirout = ''):
  '''
  Function landscape_diversity
  
  This function calculates indexes of landscape diversity/heterogeneity using the GRASS addon
  r.diversity. For more information, type 'r.diversity --help'.
  To avoid problems downloading the addon, it is distributed together with the LSMetrics package.
  It produces one map of diversity for each input map, each size of the moving window (scale), each method,
  and each alpha value in case of Renyi diversity. Diagonals around the central pixel are always considered 
  when calculating landscape diversity (moving window is a square, not a circle).
  
  Input:
  input_maps: list with strings; each input map corresponds to a binary map (1/0 and NOT 1/null!!) that represents a certain variable.
  scale_list: list with numbers (float or integer); each value correponds to a size for the moving window, in meters, in which the landscape diversity will be calculated.
  method: list with strings; the methods/indexes performed inside the moving window for calculating diversity. It must be one of the following: 'simpson', 'shannon', 'pielou', 'renyi'.
  alpha: list with numbers; each value corresponds to a value of alpha used to calculate Renyi diversity. This parameter is ignored if the Renyi diversity is not selected by the user. Alpha values must be > 0.0 to be valid and different from 1.0 to be meaningfull.
  append_name: string; name to be appended in the output map name. The default is ''.
  current_mapset: string; the name of the current map set - it is used to assess the names of the maps generated by r.diversity.
  export: (True/False) logical; if True, the maps are exported from GRASS.
  dirout: string; folder where the output maps will be saved when exported from GRASS. If '', the output maps are generated but are not exported from GRASS.
               
  Output:
  A map of landscape diversity for each input map, each scale (size of the moving window), each method/index,
  and each alpha value (in case of Renyi index).
  For more information, see r.diversity GRASS addon.
  '''
  
  # If we ask to export something but we do not provide an output folder, it shows a warning
  if export and dirout == '':
    warnings.warn("You are trying to export files from GRASS but we did not set an output folder.")
    
  # Check if each map is binary and warns the user in this case
  for mm in input_maps:
    # Get values from the map
    #maps_vals_aux = grass.read_command('r.stats', input = mm).replace('*','').split('\n')
    maps_vals_aux = grass.read_command('r.category', map = mm).split('\n')
    # Remove absent values ''
    map_vals = [val for val in maps_vals_aux if val != '']#list(filter(lambda x: x != '', maps_vals_aux))
    # If the map has less than three values, the diversity values may be meaningless
    if len(map_vals) <= 2:
      warnings.warn('\nYour input map '+mm+' has only '+str(len(map_vals))+' categories.\nLandscape diversity may be meaningless for this map.') 
  
  # Check if the chosen method is valid for r.diversity
  possible_methods = ['simpson', 'shannon', 'pielou', 'renyi'] # list of possible methods for r.diversity
  # If no method was chosen, stop
  if len(method) == 0: 
    raise Exception('\nNo method was chosen for calculating landscape diversity. Please choose at least one of the methods below:\n'+', '.join(possible_methods))
  
  else:
    # for each method, check if it is valid
    for i in method:
      if not i in possible_methods:
        raise Exception('\nYou should choose a valid method for calculating landscape diversity. "'+str(i)+'" is not valid.')
  
      # or float(alpha) == 1.0
      # Check if alpha is valid if the method 'renyi' was chosen
      if i == 'renyi' and (len(alpha) == 0 or any([float(j) <= 0 for j in alpha])):
        raise Exception('You should choose a valid value of alpha for calculating landscape Renyi diversity. The following values are not valid: "'+' and '.join([str(j) for j in alpha if float(j) <= 0])+'"')
      # if method == renyi and alpha is valid, transform alpha into a float
      elif i == 'renyi':
        alpha_num = [float(j) for j in alpha]
      else:
        alpha_num = []
  
  # For each map in the input list
  for in_map in input_maps: 
        
    # For each scale in the scale list
    for i in scale_list:
        
      # Transform the scale into an integer
      scale = int(i)
      
      # Defines the output name
      # The variable append_name is used to define different percentages, such as habitat, edge, or core percentage
      outputname = in_map+append_name+"_diversity_"+str(scale)+"m"
          
      # Define the window size in pixels
      windowsize = get_size_pixels(input_map = in_map, scale_in_meters = scale)
          
      # Defining r.diversity parameters
      inputs = in_map
      prefixes = outputname
      alphas = ','.join([str(a) for a in alpha_num])
      sizes = str(windowsize)
      methods = ','.join(method)
      overwrite = ' --overwrite'
      
      # Run command line to call r.diversity via subprocess.call
      run_r_diveristy = 'python r_diversity.py input='+inputs+' prefix='+prefixes+' alpha='+alphas+' size='+sizes+' method='+methods+overwrite
      #print run_r_diveristy
      
      # Define the region
      grass.run_command('g.region', rast = in_map)      

      # Change to the folder where the script r_diversity is
      os.chdir(script_folder)
      
      # Run r.diversity
      subprocess.call(run_r_diveristy, shell=True) # runs and wait
      #subprocess.Popen(run_r_diveristy, shell=True) # runs in batch
          
      # If export == True, export the resulting map
      if export == True and dirout != '':
        os.chdir(dirout)
        map_names_to_export = grass.list_grouped ('rast', pattern = outputname+'*') [current_mapset]
        for map_name in map_names_to_export:
          grass.run_command('r.out.gdal', flags = 'c', input = map_name, out = map_name+'.tif', createopt = "TFW=YES,COMPRESS=DEFLATE", overwrite = True) 


#----------------------------------------------------------------------------------
# General function for running LSMetrics

#-------------------------------
# Function lsmetrics_run
def lsmetrics_run(input_maps,
                  outputdir = '', output_prefix = '', add_counter_name = False,
                  zero_bin = True, zero_metrics = False, use_calculated_bin = False,
                  calcstats = False, prepare_biodim = False, remove_trash = True, 
                  binary = False, list_habitat_classes = [], export_binary = False,
                  calc_patch_size = False, diagonal = True, export_patch_size = False, export_patch_id = False,
                  calc_frag_size = False, list_edge_depth_frag = [], diagonal_neighbors = True, export_frag_size = False, export_frag_id = False,
                  struct_connec = False, export_struct_connec = False,
                  percentage_habitat = False, list_window_size_habitat = [], result_float_percentage = False, method_percentage = 'average', export_percentage_habitat = False,
                  functional_connected_area = False, list_gap_crossing = [], export_func_con_area = False, export_func_con_pid = False,
                  functional_area_complete = False, functional_connectivity_map = False,
                  calc_edge_core = False, list_edge_depth_edgecore = [], export_edge_core = False,
                  calc_edge_core_area = False, export_edge_core_pid = False,
                  percentage_edge_core = False, window_size_edge_core = [],
                  edge_dist = False, classify_edge_as_dist_zero = False, export_edge_dist = False,
                  calc_diversity = False, list_window_size_div = [], method_div = [], alpha = [], export_diversity = False):
  '''
  Function lsmetrics_run
  
  This function calls the other functions for calculating landscape metrics and run all of them 
  (or all metrics which are set by the user, given as parameters) in a single function, given input maps
  and given the metrics are chosen and parameters are defined for each of them.
  
  Input:
  input_maps: list with strings; a python list with maps loaded in the GRASS GIS location and current mapset.
  outputdir: string; folder where the output maps will be saved when exported from GRASS. If '', the output maps are generated but are not exported from GRASS.
  output_prefix: string; a prefix to be appended in the beginning of the output map names.
  add_counter_name: (True/False) logical; if True, a number is attached to the beginning of each outputmap name, in the order of the input, following 0001, 0002, 0003 ...
  
  zero_bin: (True/False) logical; if True, non-habitat values are set to zero in the binary maps; otherwise, they are set as null values. The dafault is True (and we recommend this is not modified if the user is going to run other metrics).
  zero_metrics: (True/False) logical; if True, non-habitat values are set to zero in the metrics maps; otherwise, they are set as null values. The default is False.
  use_calculated_bin: (True/False) logical; if True and binary == True, the binary maps generated by create_binary function are used as input to run the other metrics selected.
  
  calcstats: (True/False) logical; if True, statistics are calculated and saved as an output text file for the metrics selected.
  prepare_biodim: (True/False) logical; if True, maps and input text files for running BioDIM package are prepared for the metrics selected.
  remove_trash: (True/False) logical; if True, maps generated in the middle of the calculation of the metrics are deleted; otherwise they are kept within GRASS, for debugging for example. 
  
  binary: (True/False) logical; if True, input maps are transformed into binary maps using the create_binary function.
  list_habitat_classes: list with strings or integers; a python list of values that correspond to habitat in the input raster maps, and will be considered as 1 in the output.
  export_binary: (True/False) logical; if True, the binary maps created by create_binary function are exported from GRASS.
  
  calc_patch_size: (True/False) logical; if True, patch size is calculated using the patch_size function.
  diagonal: (True/False) logical; if True, cells are clumped also in the diagonal for estimating patch size, in r.clump. The default is True.
  export_patch_size: (True/False) logical; if True, the patch size maps created by the patch_size function are exported from GRASS.
  export_patch_id: (True/False) logical; if True, the patch ID maps created by the patch_size function are exported from GRASS.
  
  calc_frag_size: (True/False) logical; if True, fragment size is calculated using the fragment_area function.
  list_edge_depth_frag: list with numbers; each value correpond to an edge depth; they are used by the fragment_area function to excludes corridors with width = 2*(edge depth) to calculate fragment size.
  diagonal_neighbors: (True/False) logical; if True, diagonal cells are considering when compressing and dilatating patches with r.neighbors. The default is True.
  export_frag_size: (True/False) logical; if True, the fragment size maps created by the fragment_area function are exported from GRASS.
  export_frag_id: (True/False) logical; if True, the fragment ID maps created by the fragment_area function are exported from GRASS.
  
  struct_connec:
  export_struct_connec: 
  
  

 
  '''
  
  # Assessing the name of the current mapset - this may be used within the metrics functions
  current_mapset = grass.read_command('g.mapset', flags = 'p').replace('\n','').replace('\r','')
  
  # Transform maps into binary class maps
  if binary:
                
    bin_map_list = create_binary(input_maps, list_habitat_classes, zero = zero_bin, 
                                 prepare_biodim = prepare_biodim, calc_statistics = calcstats, 
                                 prefix = output_prefix, add_counter_name = add_counter_name,
                                 export = export_binary, dirout = outputdir)

  # If binary maps were created and the user wants these maps to be used to calculate metric,
  # then the list is considered as these binary maps; otherwise, the input list of maps is considered
  if binary and use_calculated_bin:
    list_maps_metrics = bin_map_list
    output_prefix = '' # If using this maps, do not repeat the output prefix
    add_counter_name = False # If using this maps, do not add new numbers
  else:
    list_maps_metrics = input_maps
  
  # Metrics of structural connectivity
    
  # Patch size
  if calc_patch_size:
    
    list_patch_size_pid, list_patch_size_area = patch_size(input_maps = list_maps_metrics,
                                                           zero = zero_metrics, diagonal = diagonal, 
                                                           prepare_biodim = prepare_biodim, calc_statistics = calcstats, remove_trash = remove_trash,
                                                           prefix = output_prefix, add_counter_name = add_counter_name,
                                                           export = export_patch_size, export_pid = export_patch_id, dirout = outputdir)
  
  # Fragment size
  if calc_frag_size:
    
    # Checking whether patch size was calculated
    if calc_patch_size == False and struc_connec:
      raise Exeption('To calculate structural connectivity, you need to also calculate patch size.')
    
    fragment_area(input_maps = list_maps_metrics, list_edge_depths = list_edge_depth_frag,
                  zero = zero_metrics, diagonal = diagonal, diagonal_neighbors = diagonal_neighbors,
                  struct_connec = struct_connec, patch_size_map_names = list_patch_size_area,
                  prepare_biodim = prepare_biodim, calc_statistics = calcstats, remove_trash = remove_trash,
                  prefix = output_prefix, add_counter_name = add_counter_name, 
                  export = export_frag_size, export_fid = export_frag_id, export_struct_connec = export_struct_connec,
                  dirout = outputdir)
  
  # Percentage of habitat
  if percentage_habitat:
    
    if zero_bin == False:
      raise Warning('You set the binary map to value 1-null and asked for a percentage of habitat map; this may cause problems in the output!')
    
    percentage(input_maps = list_maps_metrics, scale_list = list_window_size_habitat, method = method_percentage, append_name = '_habitat', 
               diagonal_neighbors = diagonal_neighbors, result_float = result_float_percentage,
               remove_trash = remove_trash, export = export_percentage_habitat, dirout = outputdir)
    
  # Metrics of functional connectivity
  
  # Functional connected area, functional complete connected area, and functional connectivity
  if functional_connected_area or functional_connectivity_map:
    
    functional_connectivity(input_maps = list_maps_metrics, list_gap_crossing = list_gap_crossing,
                            zero = zero_metrics, diagonal = diagonal, diagonal_neighbors = diagonal_neighbors,
                            functional_connec = functional_connectivity_map,
                            functional_area_complete = functional_area_complete,
                            prepare_biodim = prepare_biodim, calc_statistics = calcstats, remove_trash = remove_trash,
                            prefix = output_prefix, add_counter_name = add_counter_name, 
                            export = export_func_con_area, export_pid = export_func_con_pid, dirout = outputdir)  
  
  # Metrics of Core/Edge
  
  # Distance from edges
  if edge_dist:
    
    dist_edge(input_maps = list_maps_metrics,
              classify_edge_as_zero = classify_edge_as_dist_zero,
              prepare_biodim = prepare_biodim, remove_trash = remove_trash,
              prefix = output_prefix, add_counter_name = add_counter_name, export = export_edge_dist, dirout = outputdir)
    
  # Classify edge/core, calculate edge/core proportion, and area of edge/core clumps
  if calc_edge_core:
    
    edge_core(input_maps = list_maps_metrics, list_edge_depths = list_edge_depth_edgecore,
              diagonal = diagonal, diagonal_neighbors = diagonal_neighbors,
              calc_edge_core_area = calc_edge_core_area,
              calc_percentage = percentage_edge_core, window_size = window_size_edge_core, 
              method_percentage = method_percentage,
              calc_statistics = calcstats, remove_trash = remove_trash,
              prefix = output_prefix, add_counter_name = add_counter_name, export = export_edge_core, 
              export_pid = export_edge_core_pid, dirout = outputdir)
  
  # Calculate landscape diversity
  if calc_diversity:
    
    landscape_diversity(input_maps = list_maps_metrics, scale_list = list_window_size_div, 
                        method = method_div, alpha = alpha,
                        append_name = '', current_mapset = current_mapset,
                        export = export_diversity, dirout = outputdir)



#----------------------------------------------------------------------------------
# LSMetrics is the main class, in which the software GUI is initialized and runs

class LSMetrics(wx.Panel):
    def __init__(self, parent, id):
        
        # Initializing GUI
        wx.Panel.__init__(self, parent, id)     
        
        # Takes the current mapset and looks for maps only inside it
        self.current_mapset = grass.read_command('g.mapset', flags = 'p').replace('\n','').replace('\r','')        
        
        # Parameters
        
        # Maps to be processed
        self.input_maps = [] # List of input maps
        
        # For output names
        self.outputdir = '' # path to the folder where output maps
        self.output_prefix = '' # prefix to be appended to output map names
        self.add_counter_name = False # whether or not to include a counter in the output map names
        
        # Options for outputs and processing
        # remove_trash: If True, maps generated in the middle of the processes for creating final maps are removed from GRASS location
        self.remove_trash = True
        # prepare_biodim: If True, the package is run to prepare input maps and files to run BioDIM individual-based model package
        self.prepare_biodim = False
        # calc_statistics: If True, statistics files of the maps are saved while creating them
        self.calc_statistics = True
        # calc_multiple: True in case of running metrics for multiple maps, and False if running for only one map
        self.calc_multiple = False
        
        ######## set false later
        self.export_pid_general = True
        
        # Metrics to be calculated
        self.binary = False # Option: Transform input maps into binary class maps
        self.calc_patch_size = False # Option: Patch area maps
        self.calc_frag_size = False # Option: Fragment area maps (removing corridors and branches)
        self.struct_connec = False # Option: Structural connectivity maps
        self.percentage_habitat = False # Option: Proportion of habitat
        self.functional_connected_area = False # Option: Functionally connected area maps
        self.functional_area_complete = False # Option: Complete functionally connected area maps
        self.functional_connectivity_map = False # Option: Functional connectivity maps
        self.calc_edge_core = False # Option: Edge/core/matrix maps
        self.calc_edge_core_area = False # Option: Edge/core clump area
        self.percentage_edge_core = False # Option: Proportion of edge/core
        self.calc_edge_dist = False # Option: Edge distance
        self.calc_diversity = False # Option: Diversity metrics
        #------
        # Classify all elements??
        
        # Options for each metric
        
        # For multiple
        self.zero_bin = True # whether the binary generated will be 1/0 (True) or 1/null (False). Default is True.
        self.zero_metrics = False # whether the metrics generated will have non habitat values as 0 (True) or null (False). Default is False.
        self.use_calculated_bin = False # whether binary maps generated will use be used for calculating the other metrics
        self.diagonal = True # whether or not to clump pixels using diagonal pixels (used for many functions). Default is True.
        self.diagonal_neighbors = True # whether or not to analyze neighborhoods using diagonal pixels (used for many functions). Default is True.
        # For binary maps
        self.list_habitat_classes = [] # list of values that correspond to habitat
        self.export_binary = False # whether or not to export generated binary maps
        # For patch size
        self.export_patch_size = False # whether or not to export generated patch size maps
        self.export_patch_id = self.export_pid_general # False # whether or not to export generated patch ID maps
        # For fragment size
        self.list_edge_depth_frag = [] # list of values of edge depth to be considered for fragmentation process
        self.export_frag_size = False # whether or not to export generated fragment size maps
        self.export_frag_id = self.export_pid_general # False # whether or not to export generated fragment ID maps
        # For structural connectivity
        self.export_struct_connec = False # whether or not to export generated structural connectivity maps
        # For percentage of habitat 
        self.list_window_size_habitat = [] # list of window sizes to be considered for proportion of habitat
        self.result_float_percentage = False # whether or not to produce float (or int if False) maps of percentage
        self.method_percentage = 'average' # method used in r.neighbors to calculate the proportion of habitat
        self.export_percentage_habitat = False # whether or not to export generated maps of proportion of habitat
        # Functional connectivity
        self.list_gap_crossing = [] # list of gap crossing distances to be considered for functional connectivity
        self.export_func_con_area = False # whether or not to export generated functional connectivity area maps
        self.export_func_con_pid = self.export_pid_general # False # whether or not to export generated functional connectivity patch ID maps
        # For edge/core
        self.list_edge_depth_edgecore = [] # list of values of edge depth to be considered for edge/core classification
        self.export_edge_core = False # whether or not to export generated edge/core/matrix maps
        self.export_edge_core_pid = self.export_pid_general # False # whether or not to export generated edge/core clump ID maps
        self.window_size_edge_core = [] # list of window sizes to be considered for proportion of edge/core
        # Edge distance
        self.classify_edge_as_dist_zero = False # whether or not to classify pixels of the edge as 0 distance from the edge
        self.export_edge_dist = False # whether or not to export generated edge distance maps
        # Diversity metrics
        self.list_window_size_div = [] # list of window sizes to be considered for diversity index
        self.method_div = [] # list of methods to be considered for diversity index ('simpson', 'shannon', 'pielou', 'renyi')
        self.alpha = [] # list of alpha values for method renyi, to be considered for diversity index
        self.export_diversity = False # whether or not to export generated landscape diversity maps       
        
        # classify all
        
        # generate statistics
        # export pids
        
        # GUI options
        
        # List of maps to be chosen inside a mapset, in GUI
        self.map_list = []
        # Chosen map to be shown in the list, within the GUI
        self.chosen_map = ''
        # Expression for looking at multiple input maps
        self.pattern_name = ''  
        
        ############ REMOVE?
        self.list_meco = ''
        
        #------------------------------------------------------#
        #---------------INITIALIZING GUI-----------------------#
        #------------------------------------------------------#
        
        ########### Find out the best way to set the pixel size in Windows and Linux
        # Adjusting width of GUI elements depending on the Operational System
        if CURRENT_OS == "Windows":
          self.add_width = 0
        elif CURRENT_OS == "Linux":
          self.add_width = 50
        elif CURRENT_OS == "Darwin": # For Mac
          self.add_width = 0
        else:
          self.add_width = 0
        
        # Listing maps within the mapset, to be displayed and select as input maps
        
        # If preparing maps for running BioDIM, the maps must be inside a mapset named 'userbase'
        if self.prepare_biodim: 
          self.map_list = grass.list_grouped ('rast') ['userbase']
        else:
          self.map_list = grass.list_grouped ('rast') [self.current_mapset]
          
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

        #self.imageFile0 = 'lsmetrics_logo.png'
        #im0 = Image.open(self.imageFile0)
        #jpg0 = wx.Image(self.imageFile0, wx.BITMAP_TYPE_ANY).Scale(200, 82).ConvertToBitmap()
        #wx.StaticBitmap(self, -1, jpg0, (100, 15), (jpg0.GetWidth(), jpg0.GetHeight()), style=wx.SUNKEN_BORDER)                  
        
        # LEEC lab logo
        #imageFile = 'logo_lab.png'
        #im1 = Image.open(imageFile)
        #jpg1 = wx.Image(imageFile, wx.BITMAP_TYPE_ANY).Scale(80, 70).ConvertToBitmap()
        #wx.StaticBitmap(self, -1, jpg1, (430 + self.add_width, 15), (jpg1.GetWidth(), jpg1.GetHeight()), style=wx.SUNKEN_BORDER)
        
        # A multiline TextCtrl - This is here to show how the events work in this program, don't pay too much attention to it
        #self.logger = wx.TextCtrl(self, 5, '', wx.Point(200, 560), wx.Size(290 + self.add_width, 150), wx.TE_MULTILINE | wx.TE_READONLY)        
        self.logger = wx.TextCtrl(self, 5, '', wx.Point(600, 750), wx.Size(290 + self.add_width, 150), wx.TE_MULTILINE | wx.TE_READONLY)        
        
        #---------------------------------------------#
        #-------------- RADIO BOXES ------------------#
        #---------------------------------------------#   
      
        # RadioBox - event 92 (single/multiple)
        # Calculate metrics for a single or multiple maps?
        self.single_multiple_maps = ['Single', 'Multiple']
        rb1 = wx.RadioBox(self, 92, "Single or multiple maps?", wx.Point(20, 117), wx.DefaultSize,
                          self.single_multiple_maps, 2, wx.RA_SPECIFY_ROWS)
        wx.EVT_RADIOBOX(self, 92, self.EvtRadioBox)
      
        # RadioBox - event 91 (prepare maps for BioDIM)
        # Prepare files and maps for running BioDIM individual-based model?
        self.BioDimChoice = ['No', 'Yes']
        rb2 = wx.RadioBox(self, 91, "Prepare maps for BioDIM?", wx.Point(20, 195), wx.DefaultSize,
                          self.BioDimChoice, 2, wx.RA_SPECIFY_COLS)
        wx.EVT_RADIOBOX(self, 91, self.EvtRadioBox)                   
        
        #---------------------------------------------#
        #-------------- MAP SELECTION ----------------#
        #---------------------------------------------#          
        
        # Static text
        self.SelectMap = wx.StaticText(self, -1, "Select input map:", wx.Point(250, 112))
        
        # ComboBox - event 93 (select an input map from a combo box)
        
        # Maps shown when selecting a single map to calculate metrics
        try: # Try to select the first map of the list of maps loaded in the GRASS GIS location
          self.chosen_map = self.map_list[0]
          self.input_maps = [self.map_list[0]]
        except: # If there are no maps loaded
          self.chosen_map = ''
        
        # ComboBox
        self.editmap_list = wx.ComboBox(self, 93, self.chosen_map, wx.Point(165 + self.add_width, 130), wx.Size(260, -1),
                                        self.map_list, wx.CB_DROPDOWN)
        wx.EVT_COMBOBOX(self, 93, self.EvtComboBox)
        ############### do we need that here???
        wx.EVT_TEXT(self, 93, self.EvtText)              
        
        # Static text
        self.SelectMetrics = wx.StaticText(self, -1, "Pattern:", wx.Point(165 + self.add_width, 165))
        
        # Text Control - event 190
        # Regular expression (pattern) for selecting multiple maps
        self.editname1 = wx.TextCtrl(self, 190, '', wx.Point(230 + self.add_width, 160), wx.Size(195,-1))
        self.editname1.Disable()
        wx.EVT_TEXT(self, 190, self.EvtText)
        
        #---------------------------------------------#
        #-------------- BINARY MAPS ------------------#
        #---------------------------------------------#        
        
        # Static text
        self.SelectMetrics = wx.StaticText(self, -1, "Create binary map:", wx.Point(20, 250)) # Or habitat map?
        
        # Check box - event 100 (creating binary class maps)
        self.insure1 = wx.CheckBox(self, 100, "", wx.Point(135 + self.add_width, 248))
        wx.EVT_CHECKBOX(self, 100,   self.EvtCheckBox)       

        # Static text
        self.SelectMetrics1 = wx.StaticText(self, -1, "Codes for habitat:", wx.Point(165 + self.add_width, 250))
        
        # Text Control - event 191
        # List of codes that represent habitat, for generating binary class maps
        self.editname2 = wx.TextCtrl(self, 191, '', wx.Point(300 + self.add_width, 248), wx.Size(120,-1)) 
        wx.EVT_TEXT(self, 191, self.EvtText)
        self.editname2.Disable()
        
        # Static text
        self.export_text1 = wx.StaticText(self, -1, "Export?", wx.Point(460 + self.add_width, 215))
        
        # Check Box - event 51 (export binary maps)
        self.insure2 = wx.CheckBox(self, 51, "", wx.Point(475 + self.add_width, 248))
        wx.EVT_CHECKBOX(self, 51, self.EvtCheckBox)
        self.insure2.Disable()
        
        # Check Box - event 71 (use binary maps calculated to calculate other landscape metrics)
        self.insure3 = wx.CheckBox(self, 71, 'Use binary maps to calculate other metrics?', wx.Point(20, 280))
        wx.EVT_CHECKBOX(self, 71, self.EvtCheckBox)
        self.insure3.Disable()
        
        #---------------------------------------------#
        #-------- STRUCTURAL CONNECTIVITY ------------#
        #---------------------------------------------#         
      
        # Static text
        self.SelectMetrics2 = wx.StaticText(self, -1, "Metrics of structural connectivity:", wx.Point(20, 310))
        
        #------------
        # Patch size
        
        # Static text
        self.SelectMetrics3 = wx.StaticText(self, -1, "Patch size map:", wx.Point(20, 340))
        
        # Check box - event 101 (check calculate patch size)
        self.insure4 = wx.CheckBox(self, 101, '', wx.Point(135 + self.add_width, 338))
        wx.EVT_CHECKBOX(self, 101, self.EvtCheckBox)
                
        # Check Box - event 52 (export patch size maps)
        self.insure5 = wx.CheckBox(self, 52, "", wx.Point(475 + self.add_width, 338))
        wx.EVT_CHECKBOX(self, 52, self.EvtCheckBox)
        self.insure5.Disable()
        
        #------------
        # Fragment size        
        
        # Static text
        self.SelectMetrics4 = wx.StaticText(self, -1, "Fragment size map:", wx.Point(20, 370))
                
        # Check box - event 102 (check calculate fragment size)
        self.insure6 = wx.CheckBox(self, 102, '', wx.Point(135 + self.add_width, 368))
        wx.EVT_CHECKBOX(self, 102, self.EvtCheckBox)         
        
        # Static text
        self.SelectMetrics5 = wx.StaticText(self, -1, "Edge depths (m):", wx.Point(165 + self.add_width, 370))
                
        # Text Control - event 192
        # List of edge depths for calculation fragment size maps
        self.editname3 = wx.TextCtrl(self, 192, '', wx.Point(300 + self.add_width, 368), wx.Size(120,-1)) 
        wx.EVT_TEXT(self, 192, self.EvtText)
        self.editname3.Disable()        
        
        # Check Box - event 53 (export fragment size maps)
        self.insure7 = wx.CheckBox(self, 53, "", wx.Point(475 + self.add_width, 368))
        wx.EVT_CHECKBOX(self, 53, self.EvtCheckBox)
        self.insure7.Disable()
        
        #------------
        # Structural connectivity
        
        # Static text
        self.SelectMetrics6 = wx.StaticText(self, -1, "Structural connectivity:", wx.Point(20, 400))
                        
        # Check box - event 103 (check calculate structural connectivity)
        self.insure8 = wx.CheckBox(self, 103, '', wx.Point(135 + self.add_width, 398))
        wx.EVT_CHECKBOX(self, 103, self.EvtCheckBox)
        self.insure8.Disable()
        
        # Check Box - event 54 (export structural connectivity maps)
        self.insure9 = wx.CheckBox(self, 54, "", wx.Point(475 + self.add_width, 398))
        wx.EVT_CHECKBOX(self, 54, self.EvtCheckBox)
        self.insure9.Disable()        
        
        #------------
        # Proportion of habitat
        
        # Static text
        self.SelectMetrics7 = wx.StaticText(self, -1, "Proportion of habitat:", wx.Point(20, 430))
                        
        # Check box - event 104 (check calculate proportion of habitat)
        self.insure10 = wx.CheckBox(self, 104, '', wx.Point(135 + self.add_width, 428))
        wx.EVT_CHECKBOX(self, 104, self.EvtCheckBox)         
                
        # Static text
        self.SelectMetrics8 = wx.StaticText(self, -1, "Window size (m):", wx.Point(165 + self.add_width, 430))
                        
        # Text Control - event 193
        # List of moving window sizes for calculating proportion of habitat
        self.editname4 = wx.TextCtrl(self, 193, '', wx.Point(300 + self.add_width, 428), wx.Size(120,-1)) 
        wx.EVT_TEXT(self, 193, self.EvtText)
        self.editname4.Disable()        
                
        # Check Box - event 55 (export proportion of habitat)
        self.insure11 = wx.CheckBox(self, 55, "", wx.Point(475 + self.add_width, 428))
        wx.EVT_CHECKBOX(self, 55, self.EvtCheckBox)
        self.insure11.Disable()
        
        #---------------------------------------------#
        #-------- FUNCTIONAL CONNECTIVITY ------------#
        #---------------------------------------------#         
             
        # Static text
        self.SelectMetrics9 = wx.StaticText(self, -1, "Metrics of functional connectivity:", wx.Point(20, 460))
        
        #------------
        # Functionally connected area
        
        # Static text
        self.SelectMetrics10 = wx.StaticText(self, -1, "Functionally connected area:", wx.Point(20, 490))
                        
        # Check box - event 105 (check calculate functionally connected area)
        self.insure12 = wx.CheckBox(self, 105, '', wx.Point(160 + self.add_width, 488))
        wx.EVT_CHECKBOX(self, 105, self.EvtCheckBox)         
                
        # Static text
        self.SelectMetrics11 = wx.StaticText(self, -1, "Crossing distance (m):", wx.Point(185 + self.add_width, 490))
        
        # Text Control - event 194
        # List of gap crossing distances for calculating functional connectivity
        self.editname5 = wx.TextCtrl(self, 194, '', wx.Point(340 + self.add_width, 488), wx.Size(120,-1)) 
        wx.EVT_TEXT(self, 194, self.EvtText)
        self.editname5.Disable()        
                
        # Check Box - event 56 (export maps of functionally connected area)
        self.insure13 = wx.CheckBox(self, 56, "", wx.Point(475 + self.add_width, 488))
        wx.EVT_CHECKBOX(self, 56, self.EvtCheckBox)
        self.insure13.Disable()         

        #------------
        # Functional connectivity
        
        # Check Box - event 106 (check calculate functional connectivity)
        self.insure14 = wx.CheckBox(self, 106, 'Functional connectivity', wx.Point(20, 520))
        wx.EVT_CHECKBOX(self, 106, self.EvtCheckBox)
        self.insure14.Disable()
        
        #------------
        # Complete functionally connected area        
      
        # Check Box - event 107 (check calculate complete functional connected area)
        self.insure15 = wx.CheckBox(self, 107, 'Complete funct. connected area', wx.Point(250 + self.add_width, 520))
        wx.EVT_CHECKBOX(self, 107, self.EvtCheckBox)
        self.insure15.Disable()           
        
        #---------------------------------------------#
        #------------ EDGE/CORE METRICS --------------#
        #---------------------------------------------#         
                     
        # Static text
        self.SelectMetrics12 = wx.StaticText(self, -1, "Metrics of edge:", wx.Point(20, 550))
        
        #------------
        # Maps of distance from edges
        
        # Check box - event 108 (check calculate distance from edges)
        self.insure16 = wx.CheckBox(self, 108, 'Map of distance from edges', wx.Point(150 + self.add_width, 548))
        wx.EVT_CHECKBOX(self, 108, self.EvtCheckBox)
        
        # Check Box - event 57 (export maps of distance from edges)
        self.insure16_5 = wx.CheckBox(self, 57, "", wx.Point(475 + self.add_width, 548))
        wx.EVT_CHECKBOX(self, 57, self.EvtCheckBox)
        self.insure16_5.Disable()        
                
        #------------
        # Maps of edge/core/matrix
                
        # Static text
        self.SelectMetrics13 = wx.StaticText(self, -1, "Classify edge/core/matrix:", wx.Point(20, 580))
                                
        # Check box - event 109 (check classify edge/core/matrix)
        self.insure17 = wx.CheckBox(self, 109, '', wx.Point(150 + self.add_width, 578))
        wx.EVT_CHECKBOX(self, 109, self.EvtCheckBox)         
        
        # Static text
        self.SelectMetrics14 = wx.StaticText(self, -1, "Edge depths (m):", wx.Point(185 + self.add_width, 580))
                
        # Text Control - event 195
        # List of edge depths for calculating edge/core maps
        self.editname6 = wx.TextCtrl(self, 195, '', wx.Point(340 + self.add_width, 578), wx.Size(120,-1)) 
        wx.EVT_TEXT(self, 195, self.EvtText)
        self.editname6.Disable()       
                        
        # Check Box - event 58 (export maps of edge/core/matrix)
        self.insure18 = wx.CheckBox(self, 58, "", wx.Point(475 + self.add_width, 578))
        wx.EVT_CHECKBOX(self, 58, self.EvtCheckBox)
        self.insure18.Disable()
        
        #------------
        # Proportion of edge/core
                
        # Static text
        self.SelectMetrics15 = wx.StaticText(self, -1, "Proportion of edge/core:", wx.Point(20, 610))
                                
        # Check box - event 110 (check calculate proportion of edge/core)
        self.insure19 = wx.CheckBox(self, 110, '', wx.Point(140 + self.add_width, 608))
        wx.EVT_CHECKBOX(self, 110, self.EvtCheckBox)
        self.insure19.Disable()
                        
        # Static text
        self.SelectMetrics16 = wx.StaticText(self, -1, "Window size (m):", wx.Point(165 + self.add_width, 610))
                                
        # Text Control - event 196
        # List of moving window sizes for calculating proportion of edge/core
        self.editname7 = wx.TextCtrl(self, 196, '', wx.Point(300 + self.add_width, 608), wx.Size(120,-1)) 
        wx.EVT_TEXT(self, 196, self.EvtText)
        self.editname7.Disable()                

        #------------
        # Area of edge/core clumps
              
        # Check Box - event 111 (check calculate area of edge/core clumps)
        self.insure20 = wx.CheckBox(self, 111, 'Calculate area of edge/core clumps?', wx.Point(20, 640))
        wx.EVT_CHECKBOX(self, 111, self.EvtCheckBox)
        self.insure20.Disable()
        
        #---------------------------------------------#
        #------------ DIVERSITY METRICS --------------#
        #---------------------------------------------#         
                             
        # Static text
        #self.SelectMetrics16 = wx.StaticText(self, -1, "Metrics of landscape diversity:", wx.Point(20, 670))
                        
        #------------
        # Maps of edge/core/matrix
                        
        # Static text
        self.SelectMetrics16 = wx.StaticText(self, -1, "Landscape diversity:", wx.Point(20, 670))
                                        
        # Check box - event 112 (check calculate diversity metrics)
        self.insure21 = wx.CheckBox(self, 112, '', wx.Point(135 + self.add_width, 668))
        wx.EVT_CHECKBOX(self, 112, self.EvtCheckBox)         
                
        # Static text
        self.SelectMetrics17 = wx.StaticText(self, -1, "Window size (m):", wx.Point(165 + self.add_width, 670))
        
        # Text Control - event 197
        # List of window sizes for calculating diversity maps
        self.editname8 = wx.TextCtrl(self, 197, '', wx.Point(340 + self.add_width, 668), wx.Size(120,-1)) 
        wx.EVT_TEXT(self, 197, self.EvtText)
        self.editname8.Disable()       
        
        # Check Box - event 59 (export maps of diversity)
        self.insure22 = wx.CheckBox(self, 59, "", wx.Point(475 + self.add_width, 668))
        wx.EVT_CHECKBOX(self, 59, self.EvtCheckBox)
        self.insure22.Disable()
        
        # Static text
        self.SelectMetrics18 = wx.StaticText(self, -1, "Index:", wx.Point(20, 700))
        
        # Check box - event 130 (check method for diversity metrics - Shannon)
        self.insure23 = wx.CheckBox(self, 130, 'Shannon', wx.Point(60 + self.add_width, 699))
        wx.EVT_CHECKBOX(self, 130, self.EvtCheckBox)
        
        # Check box - event 131 (check method for diversity metrics - Simpson)
        self.insure24 = wx.CheckBox(self, 131, 'Simpson', wx.Point(150 + self.add_width, 699))
        wx.EVT_CHECKBOX(self, 131, self.EvtCheckBox)        

        # Check box - event 132 (check method for diversity metrics - Pielou)
        self.insure25 = wx.CheckBox(self, 132, 'Pielou', wx.Point(240 + self.add_width, 699))
        wx.EVT_CHECKBOX(self, 132, self.EvtCheckBox)

        # Check box - event 133 (check method for diversity metrics - Renyi)
        self.insure26 = wx.CheckBox(self, 133, 'Renyi', wx.Point(330 + self.add_width, 699))
        wx.EVT_CHECKBOX(self, 133, self.EvtCheckBox)
        
        # Static text
        self.SelectMetrics19 = wx.StaticText(self, -1, "Alpha:", wx.Point(400 + self.add_width, 700))
                
        # Text Control - event 198
        # List of alpha values for landscape diversity index Renyi
        self.editname9 = wx.TextCtrl(self, 198, '', wx.Point(445 + self.add_width, 698), wx.Size(60,-1)) 
        wx.EVT_TEXT(self, 198, self.EvtText)
        self.editname9.Disable()        
        
        ## Static text
        #self.SelectMetrics = wx.StaticText(self, -1,"Calculate Statistics:", wx.Point(20, 600))
        
        # export PID maps        
        
        ## Static text
        #self.SelectMetrics = wx.StaticText(self, -1,"Export: Hab/Edge/Matrix", wx.Point(20, 600))
        #self.SelectMetrics = wx.StaticText(self, -1,"| Corridor/Branch/SS", wx.Point(170, 600))
        
        
        
        #---------------------------------------------#
        #-------------- BUTTONS ----------------------#
        #---------------------------------------------#        
        
        # Button - event 10 - Start calculations
        self.button = wx.Button(self, 10, "START CALCULATIONS", wx.Point(20, 730))
        wx.EVT_BUTTON(self, 10, self.OnClick)
        
        # Button - event 8 - Exit LSMetrics
        self.button = wx.Button(self, 8, "EXIT", wx.Point(270, 730))
        wx.EVT_BUTTON(self, 8, self.OnExit)        

    #______________________________________________________________________________________________________    
    # Radio Boxes        
    def EvtRadioBox(self, event):
      
      # RadioBox - event 91 (prepare maps for BioDIM)
      if event.GetId() == 91:
        self.text_biodim = event.GetString()
        if self.text_biodim == 'No':
          self.prepare_biodim = False
        elif self.text_biodim == 'Yes':
          self.prepare_biodim = True
        else:
          raise "Error: Preparation of BioDIM maps must be either Yes or No!\n"
          
        # Refresh the list of possible input maps
        if self.prepare_biodim:        
          self.map_list = grass.list_grouped ('rast') ['userbase']
        else:
          self.map_list = grass.list_grouped ('rast') [self.current_mapset]      
      
      # RadioBox - event 92 (single/multiple maps)
      if event.GetId() == 92: 
        self.text_multiple = event.GetString()
        
        if self.text_multiple == 'Single':
          self.calc_multiple = False
          self.editmap_list.Enable()
          self.editname1.Disable()
        elif self.text_multiple == 'Multiple':
          self.calc_multiple = True
          self.editmap_list.Disable()
          self.editname1.Enable()
        else:
          raise "Error: Calculations must be done for either single or multiple maps!\n"
     
    #______________________________________________________________________________________________________
    # Combo Boxes
    def EvtComboBox(self, event):
      
        # Combo Box - event 93 (take the name of single or multiple maps and transform it into a list)
        if event.GetId() == 93:
            self.input_maps = [event.GetString()]
            self.logger.AppendText('Map: %s\n' % event.GetString())
        else:
            self.logger.AppendText('EvtComboBox: NEEDS TO BE SPECIFIED')
        
    #______________________________________________________________________________________________________
    # Function for clicking on buttons
    def OnClick(self,event):
        
        #--------------------------------------
        # Start button - event 10
        if event.GetId() == 10:

          # Before running and calculating the metrics, the user must define the output folder
          # where output maps and files will be saved
          self.outputdir = selectdirectory()
          
          # If self.calc_multiple == False, run calculations for a single map, already defined in the GUI
          # If self.calc_multiple == True, define the input maps given the input pattern 
          if self.calc_multiple == True:
            
            if self.prepare_biodim:
              self.input_maps = grass.list_grouped ('rast', pattern=self.pattern_name) ['userbase']
              #self.output_prefix2 = 'lndscp_'              
            else:
              self.input_maps = grass.list_grouped ('rast', pattern=self.pattern_name) [self.current_mapset]
          
          if len(self.input_maps) == 0:
            raise Exception('The input maps must be selected.')
          else:
                
            # Run all metrics selected
            lsmetrics_run(input_maps = self.input_maps,
                          outputdir = self.outputdir, output_prefix = self.output_prefix, add_counter_name = self.add_counter_name,
                          zero_bin = self.zero_bin, zero_metrics = self.zero_metrics, use_calculated_bin = self.use_calculated_bin,
                          calcstats = self.calc_statistics, prepare_biodim = self.prepare_biodim, remove_trash = self.remove_trash,
                          binary = self.binary, list_habitat_classes = self.list_habitat_classes, export_binary = self.export_binary,
                          calc_patch_size = self.calc_patch_size, diagonal = self.diagonal, export_patch_size = self.export_patch_size, export_patch_id = self.export_patch_id,
                          calc_frag_size = self.calc_frag_size, list_edge_depth_frag = self.list_edge_depth_frag, diagonal_neighbors = self.diagonal_neighbors, export_frag_size = self.export_frag_size, export_frag_id = self.export_frag_id,
                          struct_connec = self.struct_connec, export_struct_connec = self.export_struct_connec,
                          percentage_habitat = self.percentage_habitat, list_window_size_habitat = self.list_window_size_habitat, result_float_percentage = self.result_float_percentage, method_percentage = self.method_percentage, export_percentage_habitat = self.export_percentage_habitat,
                          functional_connected_area = self.functional_connected_area, list_gap_crossing = self.list_gap_crossing, export_func_con_area = self.export_func_con_area, export_func_con_pid = self.export_func_con_pid,
                          functional_area_complete = self.functional_area_complete, functional_connectivity_map = self.functional_connectivity_map,
                          calc_edge_core = self.calc_edge_core, list_edge_depth_edgecore = self.list_edge_depth_edgecore, export_edge_core = self.export_edge_core,
                          calc_edge_core_area = self.calc_edge_core_area, export_edge_core_pid = self.export_edge_core_pid,
                          percentage_edge_core = self.percentage_edge_core, window_size_edge_core = self.window_size_edge_core,
                          edge_dist = self.calc_edge_dist, classify_edge_as_dist_zero = self.classify_edge_as_dist_zero, export_edge_dist = self.export_edge_dist,
                          calc_diversity = self.calc_diversity, list_window_size_div = self.list_window_size_div, method_div = self.method_div, alpha = self.alpha, export_diversity = self.export_diversity)
          
            # After the calculations are finished, say goodbye
            d = wx.MessageDialog(self, "Calculations finished!\n"
                                 "", "Thanks!", wx.OK)
            # Create a message dialog box
            d.ShowModal() # Shows it
            d.Destroy()
        
    
    #______________________________________________________________________________________________________________                
    # Text Events
    def EvtText(self, event):
         
        # Text Event - event 190 (define the pattern for searching for input maps)
        if event.GetId() == 190:
          self.pattern_name = event.GetString()
          
        # Text Control - event 191
        # List of codes that represent habitat, for generating binary class maps
        if event.GetId() == 191:
          list_habitat = event.GetString()
          try: # Transform values in a list of integers
            self.list_habitat_classes = [int(i) for i in list_habitat.split(',')]
          except:
            self.list_habitat_classes = [-1]
            print('Codes for binary class reclassification of maps must be numerical.')
            
        # Text Control - event 192
        # List of edge depths for calculation fragment size maps
        if event.GetId() == 192:
          list_edge_frag = event.GetString()
          try: # Transform values in a list of float numbers
            self.list_edge_depth_frag = [float(i) for i in list_edge_frag.split(',')]
          except:
            self.list_edge_depth_frag = [-1]
            print('Edge depth must be a positive numerical values, given in meters.')
            
        # Text Control - event 193
        # List of moving window sizes for calculating proportion of habitat
        if event.GetId() == 193:
          list_window_size = event.GetString()
          try: # Transform values in a list of float numbers
            self.list_window_size_habitat = [float(i) for i in list_window_size.split(',')]
          except:
            self.list_window_size_habitat = [-1]
            print('Window size must be a positive numerical values, given in meters.')
            
        # Text Control - event 194
        # List of gap crossing distances for calculating functional connectivity        
        if event.GetId() == 194:
          list_gap_cross = event.GetString()
          try: # Transform values in a list of float numbers
            self.list_gap_crossing = [float(i) for i in list_gap_cross.split(',')]
          except:
            self.list_gap_crossing = [-1]
            print('Gap crossing distances must be a positive numerical values, given in meters.')           
        
        # Text Control - event 195
        # List of edge depths for calculating edge/core maps
        if event.GetId() == 195:
          list_edge_meco = event.GetString()
          try: # Transform values in a list of float numbers
            self.list_edge_depth_edgecore = [float(i) for i in list_edge_meco.split(',')]
          except:
            self.list_edge_depth_edgecore = [-1]
            print('Edge depths must be a positive numerical values, given in meters.')
            
        # Text Control - event 196
        # List of moving window sizes for calculating proportion of edge/core
        if event.GetId() == 196:
          list_window_size_edge = event.GetString()
          try: # Transform values in a list of float numbers
            self.window_size_edge_core = [float(i) for i in list_window_size_edge.split(',')]
          except:
            self.window_size_edge_core = [-1]
            print('Window sizes must be a positive numerical values, given in meters.')
            
        # Text Control - event 197
        # List of window sizes for calculating diversity maps        
        if event.GetId() == 197:
          list_window_size_diver = event.GetString()
          try: # Transform values in a list of float numbers
            self.list_window_size_div = [float(i) for i in list_window_size_diver.split(',')]
          except:
            self.list_window_size_div = [-1]
            print('Window sizes must be a positive numerical values, given in meters.')
            
        # Text Control - event 198
        # List of alpha values for landscape diversity index Renyi
        if event.GetId() == 198:
          list_alphas = event.GetString()
          try: # Transform values in a list of float numbers
            self.alpha = [float(i) for i in list_alphas.split(',')]
          except:
            self.alpha = [-1]
            print('Alpha must be a positive numerical values; please also avoid alpha = 1.')

    #______________________________________________________________________________________________________
    # Check Boxes
    def EvtCheckBox(self, event):
                         
        
        if event.GetId()==98: #criando txtx de statitiscas
          if int(event.Checked())==1: 
            self.calc_statistics=True           
            self.logger.AppendText('EvtCheckBox:\nCalculate connectivity statistics: '+str(self.calc_statistics)+' \n')
            
            
         
        # Check Box - event 100 (calculate binary class map)   
        if event.GetId() == 100:
          if int(event.Checked()) == 1:
            self.binary = True
            self.logger.AppendText('Create binary map: On\n')
            self.editname2.Enable() # Enable list of habitat values
            self.insure2.Enable() # Enable possibility to export binary maps
            self.insure3.Enable() # Enable possibility to use generated binary maps for other metrics
          else:
            self.binary = False
            self.logger.AppendText('Create binary map: Off\n')
            self.editname2.Disable() # Disable list of habitat values
            self.insure2.Disable() # Disable possibility to export binary maps
            self.insure3.Disable() # Disable possibility to use generated binary maps for other metrics
            
        # Check Box - event 71 (use calculated binary class maps to calculate other metrics)
        if event.GetId() == 71:
          if int(event.Checked()) == 1:
            self.use_calculated_bin = True
            self.logger.AppendText('Use binary maps for calculating other landscape metrics: On\n')
          else:
            self.use_calculated_bin = False
            self.logger.AppendText('Use binary maps for calculating other landscape metrics: Off\n')
            
        # Check Box - event 101 (check calculate patch size)
        if event.GetId() == 101:
          if int(event.Checked()) == 1:
            self.calc_patch_size = True
            self.logger.AppendText('Calculate patch size: On\n')
            self.insure5.Enable() # Enable possibility to export patch size maps
            #self.insure3.Enable() # Enable possibility to use generated binary maps for other metrics
          else:
            self.calc_patch_size = False
            self.logger.AppendText('Calculate patch size: Off\n')
            self.insure5.Disable() # Disable possibility to export patch size maps
            
          # If both patch size and frag size are checked, we may calculate structural connectivity
          if self.calc_frag_size and self.calc_patch_size:
            self.insure8.Enable() # Enable possibility to calculate structural connectivity maps
            self.insure9.Enable() # Enable possibility to export structural connectivity maps
          else:
            self.insure8.Disable() # Disable possibility to calculate structural connectivity maps
            self.insure9.Disable() # Disable possibility to export structural connectivity maps          
        
        
        # Check Box - event 102 (check calculate fragment size)
        if event.GetId() == 102:
          if int(event.Checked()) == 1:
            self.calc_frag_size = True
            self.logger.AppendText('Calculate fragment size: On\n')
            self.insure7.Enable() # Enable possibility to export fragment size maps
            self.editname3.Enable() # Enable list of edge depths
          else:
            self.calc_frag_size = False
            self.logger.AppendText('Calculate fragment size: Off\n')
            self.insure7.Disable() # Disable possibility to export fragment size maps
            self.editname3.Disable() # Disable list of habitat values
            
          # If both patch size and frag size are checked, we may calculate structural connectivity
          if self.calc_frag_size and self.calc_patch_size:
            self.insure8.Enable() # Enable possibility to calculate structural connectivity maps
            self.insure9.Enable() # Enable possibility to export structural connectivity maps
          else:
            self.insure8.Disable() # Disable possibility to calculate structural connectivity maps
            self.insure9.Disable() # Disable possibility to export structural connectivity maps
            
        
        # Check Box - event 103 (check calculate structural connectivity)
        if event.GetId() == 103:
          if int(event.Checked()) == 1:
            self.struct_connec = True
            self.logger.AppendText('Calculate structural connectivity: On\n')
            self.insure9.Enable() # Enable possibility to export structural connectivity maps
          else:
            self.struct_connec = False
            self.logger.AppendText('Calculate structural connectivity: Off\n')
            self.insure9.Disable() # Disable possibility to export structural connectivity maps
            
            
        # Check Box - event 104 (check calculate proportion of habitat)
        if event.GetId() == 104:
          if int(event.Checked()) == 1:
            self.percentage_habitat = True
            self.logger.AppendText('Calculate proportion of habitat: On\n')
            self.editname4.Enable() # Enable list of window sizes
            self.insure11.Enable() # Enable possibility to export maps of proportion of habitat
          else:
            self.percentage_habitat = False
            self.logger.AppendText('Calculate proportion of habitat: Off\n')
            self.editname4.Disable() # Disable list of window sizes
            self.insure11.Disable() # Disable possibility to export maps of proportion of habitat
            
            
        # Check box - event 105 (check calculate functionally connected area)
        if event.GetId() == 105:
          if int(event.Checked()) == 1:
            self.functional_connected_area = True
            self.logger.AppendText('Calculate functionally connected area: On\n')
            self.editname5.Enable() # Enable list of gap crossing distances
            self.insure13.Enable() # Enable possibility to export maps of functionally connected area
            self.insure14.Enable() # Enable possibility to calculate maps of functional connectivity
            self.insure15.Enable() # Enable possibility to calculate maps of complete functionally connected area
          else:
            self.functional_connected_area = False
            self.logger.AppendText('Calculate functionally connected area: Off\n')
            self.editname5.Disable() # Disable list of gap crossing distances
            self.insure13.Disable() # Disable possibility to export maps of functionally connected area
            self.insure14.Disable() # Disable possibility to calculate maps of functional connectivity
            self.insure15.Disable() # Disable possibility to calculate maps of complete functionally connected area
            
        # Check Box - event 106 (check calculate functional connectivity)        
        if event.GetId() == 106:
          if int(event.Checked()) == 1:
            self.functional_connectivity_map = True
            self.logger.AppendText('Calculate functional connectivity map: On\n')
          else:
            self.functional_connectivity_map = False
            self.logger.AppendText('Calculate functional connectivity map: Off\n')
            
        # Check Box - event 107 (check calculate complete functional connected area)
        if event.GetId() == 107:
          if int(event.Checked()) == 1:
            self.functional_area_complete = True
            self.logger.AppendText('Calculate complete functional connected area: On\n')
          else:
            self.functional_area_complete = False
            self.logger.AppendText('Calculate complete functional connected area: Off\n')                
        
        # Check box - event 108 (check calculate distance from edges)
        if event.GetId() == 108:
          if int(event.Checked()) == 1:
            self.calc_edge_dist = True
            self.logger.AppendText('Calculate distance from edges: On\n')
            self.insure16_5.Enable() # Enable possibility to export maps of distance from edges
          else:
            self.calc_edge_dist = False
            self.logger.AppendText('Calculate distance from edges: Off\n')
            self.insure16_5.Disable() # Disable possibility to export maps of distance from edges
        
        # Check Box - event 109 (check classify edge/core/matrix)
        if event.GetId() == 109:
          if int(event.Checked()) == 1:
            self.calc_edge_core = True
            self.logger.AppendText('Classify edge/core/matrix: On\n')
            self.editname6.Enable() # Enable list of edge depths for maps of edge/core/matrix
            self.insure18.Enable() # Enable possibility to export maps of edge/core/matrix
            self.insure19.Enable() # Enable possibility to calculate proportion of edge/core
            self.insure20.Enable() # Enable possibility to calculate area of edge/core clumps
          else:
            self.calc_edge_core = False
            self.logger.AppendText('Classify edge/core/matrix: Off\n')
            self.editname6.Disable() # Disable list of edge depths for maps of edge/core/matrix
            self.insure18.Disable() # Disable possibility to export maps of edge/core/matrix
            self.insure19.Disable() # Disable possibility to calculate proportion of edge/core
            self.insure20.Disable() # Disable possibility to calculate area of edge/core clumps
            
        # Check Box - event 110 (check calculate proportion of edge core)
        if event.GetId() == 110:
          if int(event.Checked()) == 1:
            self.percentage_edge_core = True
            self.logger.AppendText('Calculate proportion of edge/core: On\n')
            self.editname7.Enable() # Enable list of window sizes
          else:
            self.percentage_edge_core = False
            self.logger.AppendText('Calculate proportion of edge/core: Off\n')
            self.editname7.Disable() # Disable list of window sizes
            
        # Check Box - event 111 (check calculate area of edge/core clumps)
        if event.GetId() == 111:
          if int(event.Checked()) == 1:
            self.calc_edge_core_area = True
            self.logger.AppendText('Calculate area of edge/core clumps: On\n')
          else:
            self.calc_edge_core_area = False
            self.logger.AppendText('Calculate area of edge/core clumps: Off\n')
            
        # Check Box - event 112 (check calculate diversity metrics)
        if event.GetId() == 112:
          if int(event.Checked()) == 1:
            self.calc_diversity = True
            self.logger.AppendText('Calculate landscape diversity: On\n')
            self.editname8.Enable() # Enable list of window sizes
            self.insure22.Enable() # Enable possibility to export maps of diversity
            self.insure23.Enable() # Enable possibility to use method Shannon
            self.insure24.Enable() # Enable possibility to use method Simpson
            self.insure25.Enable() # Enable possibility to use method Pielou
            self.insure26.Enable() # Enable possibility to use method Renyi            
          else:
            self.calc_diversity = False
            self.logger.AppendText('Calculate landscape diversity: Off\n')        
            self.editname8.Disable() # Disable list of window sizes
            self.insure22.Disable() # Disable possibility to export maps of diversity
            self.insure23.Disable() # Disable possibility to use method Shannon
            self.insure24.Disable() # Disable possibility to use method Simpson
            self.insure25.Disable() # Disable possibility to use method Pielou
            self.insure26.Disable() # Disable possibility to use method Renyi
        
        # Check boxes for indexes of landscape diversity
        
        # Check Box - event 130 (check method for diversity metrics - Shannon)
        if event.GetId() == 130:
          if int(event.Checked()) == 1:
            self.method_div.append('shannon')
            self.logger.AppendText('Landscape diversity: Shannon selected\n')
          else:
            self.method_div.remove('shannon')
            self.logger.AppendText('Landscape diversity: Shannon unselected\n')
            
        # Check Box - event 131 (check method for diversity metrics - Simpson)
        if event.GetId() == 131:
          if int(event.Checked()) == 1:
            self.method_div.append('simpson')
            self.logger.AppendText('Landscape diversity: Simpson selected\n')
          else:
            self.method_div.remove('simpson')
            self.logger.AppendText('Landscape diversity: Simpson unselected\n')
            
        # Check Box - event 132 (check method for diversity metrics - Pielou)
        if event.GetId() == 132:
          if int(event.Checked()) == 1:
            self.method_div.append('pielou')
            self.logger.AppendText('Landscape diversity: Pielou selected\n')
          else:
            self.method_div.remove('pielou')
            self.logger.AppendText('Landscape diversity: Pielou unselected\n')        
          
        # Check Box - event 133 (check method for diversity metrics - Renyi)
        if event.GetId() == 133:
          if int(event.Checked()) == 1:
            self.method_div.append('renyi')
            self.logger.AppendText('Landscape diversity: Renyi selected\n')
            self.editname9.Enable() # Enable list of alpha values for Renyi index             
          else:
            self.method_div.remove('renyi')
            self.logger.AppendText('Landscape diversity: Renyi unselected\n')
            self.editname9.Disable() # Disable list of alpha values for Renyi index
            
            
        # Check boxes for exporting maps
        
        # Check Box - event 51 (export binary maps)
        if event.GetId() == 51:
          if int(event.Checked()) == 1:
            self.export_binary = True
            self.logger.AppendText('Export binary map: On\n')
          else:
            self.export_binary = False
            self.logger.AppendText('Export binary map: Off\n')
            
        # Check Box - event 52 (export patch size maps)
        if event.GetId() == 52:
          if int(event.Checked()) == 1:
            self.export_patch_size = True
            self.logger.AppendText('Export patch size map: On\n')
          else:
            self.export_patch_size = False
            self.logger.AppendText('Export patch size map: Off\n')
            
        # Check Box - event 53 (export fragment size maps)
        if event.GetId() == 53:
          if int(event.Checked()) == 1:
            self.export_frag_size = True
            self.logger.AppendText('Export fragment size map: On\n')
          else:
            self.export_frag_size = False
            self.logger.AppendText('Export fragment size map: Off\n')
            
        # Check Box - event 54 (export structural connectivity maps)
        if event.GetId() == 54:
          if int(event.Checked()) == 1:
            self.export_struct_connec = True
            self.logger.AppendText('Export structural connectivity map: On\n')
          else:
            self.export_struct_connec = False
            self.logger.AppendText('Export tructural connectivity map: Off\n')
            
        # Check Box - event 55 (export proportion of habitat)
        if event.GetId() == 55:
          if int(event.Checked()) == 1:
            self.export_percentage_habitat = True
            self.logger.AppendText('Export map of proportion of habitat: On\n')
          else:
            self.export_percentage_habitat = False
            self.logger.AppendText('Export map of proportion of habitat: Off\n')
            
        # Check Box - event 56 (export maps of functionally connected area)
        if event.GetId() == 56:
          if int(event.Checked()) == 1:
            self.export_func_con_area = True
            self.logger.AppendText('Export map of functionally connected area: On\n')
          else:
            self.export_func_con_area = False
            self.logger.AppendText('Export map of functionally connected area: Off\n')
        
        # Check Box - event 57 (export maps of distance from edges)
        if event.GetId() == 57:
          if int(event.Checked()) == 1:
            self.export_edge_dist = True
            self.logger.AppendText('Export map of distance from edges: On\n')
          else:
            self.export_edge_dist = False
            self.logger.AppendText('Export map of distance from edges: Off\n')        
            
        # Check Box - event 58 (export maps of edge/core/matrix)
        if event.GetId() == 58:
          if int(event.Checked()) == 1:
            self.export_edge_core = True
            self.logger.AppendText('Export map of edge/core/matrix: On\n')
          else:
            self.export_edge_core = False
            self.logger.AppendText('Export map of edge/core/matrix: Off\n')
            
        # Check Box - event 59 (export maps of diversity)
        if event.GetId() == 59:
          if int(event.Checked()) == 1:
            self.export_diversity = True
            self.logger.AppendText('Export map of landscape diversity: On\n')
          else:
            self.export_diversity = False
            self.logger.AppendText('Export map of landscape diversity: Off\n')        
            
    #______________________________________________________________________________________________________
    # Button to exit LSMetrics
    def OnExit(self, event):
      
        # Message
        d = wx.MessageDialog( self, "Thanks for using LSMetrics "+VERSION+"!\n"
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
    
    # Adjusting width of GUI depending on the Operational System
    if CURRENT_OS == "Windows":
      size = (530, 850)
    elif CURRENT_OS == "Linux":
      size = (530 + 50, 770)
    elif CURRENT_OS == "Darwin": # For Mac
      size = (530 + 50, 770)
    
    # Run GUI
    app = wx.PySimpleApp()
    frame = wx.Frame(None, -1, "LSMetrics "+VERSION, pos=(0,0), size = size)
    LSMetrics(frame,-1)
    frame.Show(1)
    
    app.MainLoop()
