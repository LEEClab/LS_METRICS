# Script for testing LSMetrics

python

# import modules
import os
import grass.script as grass

# folder for saving outputs
output_dir = r'/home/leecb/Github/LS_METRICS/test_output'

# We have two input maps loaded, one in shape format, and other in raster format

#-------------------------------
# First we have to prepare the inputs - transform the vector map into a raster map

## define region and resolution
#grass.run_command("g.region", flags = "p", vector = "SP_3543907_USO", res = 30)

## vector to raster
#grass.run_command("v.to.rast", input = "SP_3543907_USO", output = "SP_RioClaro_use_raster", \
                  #type = "area", use = "cat", label_column = "CLASSE_USO", overwrite = True)

#-------------------------------
# Now let's test the function to create binary maps
# This also tests function createtxt for text files with statistics, and create_TXTinputBIODIM
# and lsmetrics_run, also

# Change dir
ls_metrics_dir = r'/home/leecb/Github/LS_METRICS/_LSMetrics_v1_0_0_stable'
os.chdir(ls_metrics_dir)
from LSMetrics_v1_0_0 import create_binary, createtxt, create_TXTinputBIODIM, lsmetrics_run

# 1) For only one map
list_of_maps = ['SP_RioClaro_use_raster']
habitat_is = ['4','5'] 
# or numerical, both run: 
#habitat_is = [4,5]

# With zero
create_binary(list_maps = list_of_maps, list_habitat_classes = habitat_is, zero = True, prefix = 'zero_')

# With null
create_binary(list_maps = list_of_maps, list_habitat_classes = habitat_is, zero = False, prefix = 'null_')

# 2) For more than one map
list_of_maps = ['SP_RioClaro_use_raster', 'APA_Sao_Joao_RJ_cut_SIRGAS_UTM23S']
habitat_is = ['4','5','6'] 
# or numerical, both run: 
#habitat_is = [4,5,6]

# With zero
create_binary(list_maps = list_of_maps, list_habitat_classes = habitat_is, zero = True, prefix = 'zero_')

# 3) Test export and calculate statistics
create_binary(list_maps = list_of_maps, list_habitat_classes = habitat_is, zero = True, prefix = 'zero_',
              calc_statistics = True, export = True, dirout = output_dir)

# 4) Test create output for biodim
create_binary(list_maps = list_of_maps, list_habitat_classes = habitat_is, zero = True, prefix = 'zero_',
              prepare_biodim = True, dirout = output_dir)

# 5) Test using lsmetrics_run function
lsmetrics_run(input_maps = list_of_maps,
              outputdir = output_dir, output_prefix = 'zero_',
              calcstats = True, prepare_biodim = True, remove_trash = True,
              binary = True, list_habitat_classes = habitat_is, zero = True, 
              add_counter_name = True, export_binary = True)

# Removing generated rasters        
grass.run_command('g.remove', type = 'raster', pattern = '*HABMAT', flags = 'f')

# OK!
#-------------------------------


#-------------------------------
# Now let's test the function to calculate patch size

python

# import modules
import os
import grass.script as grass

# folder for saving outputs
output_dir = r'/home/leecb/Github/LS_METRICS/test_output'

# Change dir
ls_metrics_dir = r'/home/leecb/Github/LS_METRICS/_LSMetrics_v1_0_0_stable'
os.chdir(ls_metrics_dir)
from LSMetrics_v1_0_0 import create_binary, createtxt, create_TXTinputBIODIM, lsmetrics_run, patch_size

# 0) Calculate binary maps
list_of_maps = ['SP_RioClaro_use_raster', 'APA_Sao_Joao_RJ_cut_SIRGAS_UTM23S']
habitat_is = ['4','5','6']

# Create binary 0/1 maps
bin_map_list = create_binary(list_maps = list_of_maps, list_habitat_classes = habitat_is, zero = True, prefix = 'zero_')

# 1) For only one map

# With zero
patch_size(input_maps = [bin_map_list[0]], zero = True, prefix = 'zero_')

# With null
patch_size(input_maps = [bin_map_list[0]], prefix = 'null_')

# 2) For more than one map

# With null
patch_size(input_maps = bin_map_list)

# 3) Test export, calculate statistics, and create output for biodim
patch_size(input_maps = bin_map_list, 
           calc_statistics = True, prepare_biodim = True, 
           export = True, dirout = output_dir)

# 4) Test using lsmetrics_run function using binary maps already calculated
lsmetrics_run(input_maps = bin_map_list,
              outputdir = output_dir,
              zero_metrics = True, add_counter_name = True, 
              calcstats = True, prepare_biodim = True, remove_trash = True, use_calculated_bin = True,
              binary = False, export_binary = True,
              calc_patch_size = True, diagonal = False, export_patch_size = True)

# 5) Test using lsmetrics_run function calculating binary maps AND patch size maps
lsmetrics_run(input_maps = list_of_maps,
              outputdir = output_dir, output_prefix = 'together_', add_counter_name = True, 
              zero_bin = True, zero_metrics = False, 
              calcstats = True, prepare_biodim = True, remove_trash = True, use_calculated_bin = True,
              binary = True, list_habitat_classes = habitat_is, export_binary = False,
              calc_patch_size = True, diagonal = True, export_patch_size = True)


# Removing generated rasters        
grass.run_command('g.remove', type = 'raster', pattern = '*HABMAT', flags = 'f')
grass.run_command('g.remove', type = 'raster', pattern = '*AreaHA', flags = 'f')
grass.run_command('g.remove', type = 'raster', pattern = '*pid', flags = 'f')

# OK!
#-------------------------------


#-------------------------------
# Now let's test the functions to calculate fragment size and structural connectivity

python

# import modules
import os
import grass.script as grass

# folder for saving outputs
output_dir = r'/home/leecb/Github/LS_METRICS/test_output'

# Change dir
ls_metrics_dir = r'/home/leecb/Github/LS_METRICS/_LSMetrics_v1_0_0_stable'
os.chdir(ls_metrics_dir)
from LSMetrics_v1_0_0 import create_binary, createtxt, create_TXTinputBIODIM, lsmetrics_run, patch_size, fragment_area

# 0) Calculate binary maps and patch size
list_of_maps = ['SP_RioClaro_use_raster', 'APA_Sao_Joao_RJ_cut_SIRGAS_UTM23S']
habitat_is = ['4','5','6']

# Create binary 0/1 maps
bin_map_list = create_binary(list_maps = list_of_maps, list_habitat_classes = habitat_is, zero = True, prefix = 'zero_')

list_pid, list_patch_area = patch_size(input_maps = bin_map_list)

# 1) For only one map and one scale
list_scales = [50]

# With null
fragment_area(input_maps = [bin_map_list[0]], list_edge_depths = list_scales, prefix = 'null_',
              diagonal = False, export = True, export_fid=True)

help(fragment_area)

# 2) For only one map and and three scales
list_scales = [50, 100, 200]

fragment_area(input_maps = [bin_map_list[0]], list_edge_depths = list_scales, prefix = 'null_',
              diagonal = True)

# 3) For more than one map and three scale
# Test export, calculate statistics, and create output for biodim

# With null
fragment_area(input_maps = bin_map_list, list_edge_depths = list_scales, prefix = 'null_',
              prepare_biodim = True, calc_statistics = True, 
              export = True, export_fid = True, dirout = output_dir)

# 4) Test using lsmetrics_run function using binary maps already calculated
lsmetrics_run(input_maps = [bin_map_list[0]],
              outputdir = output_dir,
              zero_metrics = True, add_counter_name = True, use_calculated_bin = True,
              calcstats = True, prepare_biodim = True, remove_trash = True, 
              binary = False, export_binary = True,
              calc_patch_size = True, diagonal = True, export_patch_size = True, export_patch_id = True,
              calc_frag_size = True, list_edge_depth_frag = list_scales, export_frag_size = True, export_frag_id = True)

# 5) Test using lsmetrics_run function calculating binary maps AND patch size maps AND fragment size maps
lsmetrics_run(input_maps = [list_of_maps[0]],
              outputdir = output_dir, output_prefix = 'together_', add_counter_name = True, 
              zero_bin = True, zero_metrics = False, use_calculated_bin = True,
              calcstats = True, prepare_biodim = True, remove_trash = True,
              binary = True, list_habitat_classes = habitat_is, export_binary = False,
              calc_patch_size = True, diagonal = False, export_patch_size = True, export_patch_id = True,
              calc_frag_size = True, list_edge_depth_frag = list_scales, export_frag_size = True, export_frag_id = True)

# 6) test with structural connectivity

# Removing generated rasters        
grass.run_command('g.remove', type = 'raster', pattern = '*HABMAT', flags = 'f')
grass.run_command('g.remove', type = 'raster', pattern = '*AreaHA', flags = 'f')
grass.run_command('g.remove', type = 'raster', pattern = '*pid', flags = 'f')
grass.run_command('g.remove', type = 'raster', pattern = '*fid', flags = 'f')

# OK!
#-------------------------------


#-------------------------------
# Now let's test the function to calculate the proportion of habitat

python

# import modules
import os
import grass.script as grass

# folder for saving outputs
output_dir = r'/home/leecb/Github/LS_METRICS/test_output'

# Change dir
ls_metrics_dir = r'/home/leecb/Github/LS_METRICS/_LSMetrics_v1_0_0_stable'
os.chdir(ls_metrics_dir)
from LSMetrics_v1_0_0 import create_binary, createtxt, create_TXTinputBIODIM, lsmetrics_run, percentage, get_size_pixels

# 1) For only one map
list_of_maps = ['SP_RioClaro_use_raster']
habitat_is = ['4','5'] 
list_scales = [100, 200]

# With zero
bin_map_list = create_binary(list_maps = list_of_maps, list_habitat_classes = habitat_is, zero = True, prefix = 'zero_')

percentage(input_maps = bin_map_list, scale_list = list_scales, append_name = 'habitat',
           remove_trash = True, export = False, dirout = '')

# DO NOT DO THAT! WARNING!
# With null
bin_map_list = create_binary(list_maps = list_of_maps, list_habitat_classes = habitat_is, zero = False, prefix = 'null_')

percentage(input_maps = bin_map_list, scale_list = list_scales, append_name = 'habitat',
           remove_trash = True, export = False, dirout = '')

# 2) For more than one map
list_of_maps = ['SP_RioClaro_use_raster', 'APA_Sao_Joao_RJ_cut_SIRGAS_UTM23S']
habitat_is = ['4','5','6'] 
# or numerical, both run: 
#habitat_is = [4,5,6]

# With zero
bin_map_list = create_binary(list_maps = list_of_maps, list_habitat_classes = habitat_is, zero = True, prefix = 'zero_')

percentage(input_maps = bin_map_list, scale_list = list_scales, append_name = 'habitat',
           remove_trash = True, export = False, dirout = '')

# 3) Test using lsmetrics_run function using binary maps already calculated
lsmetrics_run(input_maps = bin_map_list,
              outputdir = output_dir, remove_trash = True,
              binary = False, export_binary = True,
              percentage_habitat = True, list_window_size = list_scales, export_percentage_habitat = True)

# 5) Test using lsmetrics_run function calculating binary maps AND patch size maps
lsmetrics_run(input_maps = list_of_maps,
              outputdir = output_dir, output_prefix = 'together_', add_counter_name = True, 
              zero_bin = True, zero_metrics = False, 
              calcstats = True, prepare_biodim = True, remove_trash = True, use_calculated_bin = True,
              binary = True, list_habitat_classes = habitat_is, export_binary = False,
              percentage_habitat = True, list_window_size_habitat = list_scales, export_percentage_habitat = True)

# Removing generated rasters
grass.run_command('g.remove', type = 'raster', pattern = '*HABMAT', flags = 'f')
grass.run_command('g.remove', type = 'raster', pattern = '*pct*', flags = 'f')

# OK!
#-------------------------------


#-------------------------------
# Now let's test the function to calculate functional connectivity

python

# import modules
import os
import grass.script as grass

# folder for saving outputs
output_dir = r'/home/leecb/Github/LS_METRICS/test_output'

# Change dir
ls_metrics_dir = r'/home/leecb/Github/LS_METRICS/_LSMetrics_v1_0_0_stable'
os.chdir(ls_metrics_dir)
from LSMetrics_v1_0_0 import create_binary, createtxt, create_TXTinputBIODIM, lsmetrics_run, functional_connectivity

# 1) For only one map
list_of_maps = ['SP_RioClaro_use_raster']
habitat_is = ['4','5'] 
list_scales = [100, 200]

# With zero
bin_map_list = create_binary(list_maps = list_of_maps, list_habitat_classes = habitat_is, zero = True, prefix = 'zero_')

functional_connectivity(input_maps = bin_map_list, list_gap_crossing = list_scales, zero = False,
                        functional_area_complete = True)

# 2) For more than one map, testing export
list_of_maps = ['SP_RioClaro_use_raster', 'APA_Sao_Joao_RJ_cut_SIRGAS_UTM23S']
habitat_is = [4,5,6]
list_scales = [0, '100', '200']

bin_map_list = create_binary(list_maps = list_of_maps, list_habitat_classes = habitat_is, zero = True, prefix = 'zero_')

functional_connectivity(input_maps = bin_map_list, list_gap_crossing = list_scales, zero = False,
                        functional_area_complete = True, export = True, export_pid = True, dirout = output_dir)

# 3) For more than one map, testing export and generating a map of funcional connectivity
list_of_maps = ['SP_RioClaro_use_raster', 'APA_Sao_Joao_RJ_cut_SIRGAS_UTM23S']
habitat_is = [4,5,6]
list_scales = ['100', '200', 0]

bin_map_list = create_binary(list_maps = list_of_maps, list_habitat_classes = habitat_is, zero = True, prefix = 'zero_')

functional_connectivity(input_maps = bin_map_list, list_gap_crossing = list_scales, zero = False,
                        functional_connec = True,
                        functional_area_complete = False, export = True, export_pid = True, dirout = output_dir)

# 4) For more than one map, testing export and generating a map of funcional connectivity,
# using function lsmetrics_run
list_of_maps = ['SP_RioClaro_use_raster', 'APA_Sao_Joao_RJ_cut_SIRGAS_UTM23S']
habitat_is = [4,5,6]
list_scales = ['100', '200', 0]

bin_map_list = create_binary(list_maps = list_of_maps, list_habitat_classes = habitat_is, zero = True, prefix = 'zero_')

lsmetrics_run(input_maps = bin_map_list,
              outputdir = output_dir, output_prefix = '',
              zero_bin = True, zero_metrics = False, use_calculated_bin = False,
              calcstats = True, prepare_biodim = True, remove_trash = True, 
              binary = False, list_habitat_classes = [], export_binary = False,
              functional_connected_area = True, list_gap_crossing = list_scales, export_func_con_area = True, export_func_con_pid = False,
              functional_area_complete = False, functional_connectivity_map = True)

# 5) Using function lsmetrics_run, generating binary maps inside it
list_of_maps = ['SP_RioClaro_use_raster', 'APA_Sao_Joao_RJ_cut_SIRGAS_UTM23S']
habitat_is = [4,5,6]
list_scales = ['100', '200', 0]

lsmetrics_run(input_maps = [list_of_maps[0]],
              outputdir = output_dir, output_prefix = '',
              zero_bin = True, zero_metrics = False, use_calculated_bin = False,
              calcstats = True, prepare_biodim = True, remove_trash = True, 
              binary = True, list_habitat_classes = habitat_is, export_binary = True,
              functional_connected_area = False, list_gap_crossing = list_scales, export_func_con_area = True, export_func_con_pid = True,
              functional_area_complete = True, functional_connectivity_map = True)

# Removing generated rasters        
grass.run_command('g.remove', type = 'raster', pattern = '*HABMAT', flags = 'f')
grass.run_command('g.remove', type = 'raster', pattern = '*AreaHA', flags = 'f')
grass.run_command('g.remove', type = 'raster', pattern = '*pid', flags = 'f')
grass.run_command('g.remove', type = 'raster', pattern = '*connectivity', flags = 'f')

# OK!
#-------------------------------


#-------------------------------
# Now let's test the function to calculate edge dist

python

# import modules
import os
import grass.script as grass

# folder for saving outputs
output_dir = r'/home/leecb/Github/LS_METRICS/test_output'

# Change dir
ls_metrics_dir = r'/home/leecb/Github/LS_METRICS/_LSMetrics_v1_0_0_stable'
os.chdir(ls_metrics_dir)
from LSMetrics_v1_0_0 import create_binary, createtxt, create_TXTinputBIODIM, lsmetrics_run, dist_edge

# 1) For only one map
list_of_maps = ['SP_RioClaro_use_raster']
habitat_is = ['4','5'] 

# With zero
bin_map_list = create_binary(list_maps = list_of_maps, list_habitat_classes = habitat_is, zero = True, prefix = 'zero_',
                             export = True, dirout = output_dir)

# With edges = 0
dist_edge(input_maps = bin_map_list,
          classify_edge_as_zero = True,
          prepare_biodim = False, remove_trash = True,
          prefix = '', add_counter_name = False, export = True, dirout = output_dir)

# Without edges = 0
dist_edge(input_maps = bin_map_list,
          classify_edge_as_zero = False,
          prepare_biodim = False, remove_trash = True,
          prefix = 'sem_zero', add_counter_name = False, export = True, dirout = output_dir)

# 2) For more than one map
list_of_maps = ['SP_RioClaro_use_raster', 'APA_Sao_Joao_RJ_cut_SIRGAS_UTM23S']
habitat_is = [4,5,6]

bin_map_list = create_binary(list_maps = list_of_maps, list_habitat_classes = habitat_is, zero = True, prefix = 'zero_')

dist_edge(input_maps = bin_map_list,
          classify_edge_as_zero = False,
          prepare_biodim = False, remove_trash = True,
          prefix = 'sem_zero', add_counter_name = False, export = True, dirout = output_dir)

# 3) For more than one map, using function lsmetrics_run
list_of_maps = ['SP_RioClaro_use_raster', 'APA_Sao_Joao_RJ_cut_SIRGAS_UTM23S']
habitat_is = [4,6]

bin_map_list = create_binary(list_maps = list_of_maps, list_habitat_classes = habitat_is, zero = True, prefix = 'zero_')

lsmetrics_run(input_maps = bin_map_list,
              outputdir = output_dir, output_prefix = '',
              zero_bin = True, zero_metrics = False, use_calculated_bin = False,
              calcstats = True, prepare_biodim = True, remove_trash = True, 
              binary = False, list_habitat_classes = [], export_binary = False,
              edge_dist = True, classify_edge_as_dist_zero = True, export_edge_dist = True)

# 4) Using function lsmetrics_run, generating binary maps inside it
list_of_maps = ['SP_RioClaro_use_raster', 'APA_Sao_Joao_RJ_cut_SIRGAS_UTM23S']
habitat_is = [4,6]

lsmetrics_run(input_maps = list_of_maps,
              outputdir = output_dir, output_prefix = '',
              zero_bin = True, zero_metrics = False, use_calculated_bin = True,
              calcstats = True, prepare_biodim = True, remove_trash = True, 
              binary = True, list_habitat_classes = habitat_is, export_binary = True,
              edge_dist = True, classify_edge_as_dist_zero = True, export_edge_dist = True)

# Removing generated rasters
grass.run_command('g.remove', type = 'raster', pattern = '*HABMAT', flags = 'f')
grass.run_command('g.remove', type = 'raster', pattern = '*dist', flags = 'f')

# OK!
#-------------------------------


#-------------------------------
# Now let's test the function to calculate edge/core

python

# import modules
import os
import grass.script as grass

# folder for saving outputs
output_dir = r'/home/leecb/Github/LS_METRICS/test_output'

# Change dir
ls_metrics_dir = r'/home/leecb/Github/LS_METRICS/_LSMetrics_v1_0_0_stable'
os.chdir(ls_metrics_dir)
from LSMetrics_v1_0_0 import create_binary, createtxt, create_TXTinputBIODIM, lsmetrics_run, edge_core, percentage

# 1) For only one map
list_of_maps = ['SP_RioClaro_use_raster']
habitat_is = ['4','5'] 

# With zero
bin_map_list = create_binary(list_maps = list_of_maps, list_habitat_classes = habitat_is, zero = True, prefix = 'zero_',
                             export = True, dirout = output_dir)

edge_core(input_maps = bin_map_list, list_edge_depths = [50, 100, 200],
          diagonal = True,
          calc_edge_core_area = True,
          calc_percentage = True, window_size = [200, 500],
          calc_statistics = True, remove_trash = True,
          prefix = '', add_counter_name = False, export = True, export_pid = True, dirout = output_dir)

# 2) For two maps
list_of_maps = ['SP_RioClaro_use_raster', 'APA_Sao_Joao_RJ_cut_SIRGAS_UTM23S']
habitat_is = [4,6]
list_edges = [50, 100, 200]

bin_map_list = create_binary(list_maps = list_of_maps, list_habitat_classes = habitat_is, zero = True, prefix = 'zero_')

edge_core(input_maps = bin_map_list, list_edge_depths = list_edges,
          diagonal = True,
          calc_edge_core_area = True,
          calc_percentage = True, window_size = [200, 500],
          calc_statistics = True, remove_trash = True,
          prefix = '', add_counter_name = False, export = True, export_pid = True, dirout = output_dir)

# 3) For more than one map, using function lsmetrics_run
list_of_maps = ['SP_RioClaro_use_raster', 'APA_Sao_Joao_RJ_cut_SIRGAS_UTM23S']
habitat_is = [4,6]
list_edges = [50, 100, 200]
list_scales = [300, 700]

bin_map_list = create_binary(list_maps = list_of_maps, list_habitat_classes = habitat_is, zero = True, prefix = 'zero_')

lsmetrics_run(input_maps = bin_map_list,
              outputdir = output_dir, output_prefix = '', add_counter_name = False,
              zero_bin = True, zero_metrics = False, use_calculated_bin = False,
              calcstats = True, prepare_biodim = False, remove_trash = True, 
              binary = False, list_habitat_classes = list_edges, export_binary = False,
              calc_edge_core = True, list_edge_depth_edgecore = list_edges, export_edge_core = True,
              calc_edge_core_area = False, export_edge_core_pid = False,
              percentage_edge_core = True, window_size_edge_core = list_scales)

# 4) Using function lsmetrics_run, generating binary maps inside it
list_of_maps = ['SP_RioClaro_use_raster', 'APA_Sao_Joao_RJ_cut_SIRGAS_UTM23S']
habitat_is = [4,6]
list_edges = [50, '100', 200]

lsmetrics_run(input_maps = list_of_maps,
              outputdir = output_dir, output_prefix = '', add_counter_name = False,
              zero_bin = True, zero_metrics = False, use_calculated_bin = True,
              calcstats = True, prepare_biodim = False, remove_trash = True, 
              binary = True, list_habitat_classes = habitat_is, export_binary = False,
              calc_edge_core = True, list_edge_depth_edgecore = list_edges, export_edge_core = True,
              calc_edge_core_area = True, export_edge_core_pid = False,
              percentage_edge_core = False, window_size_edge_core = [])

# Removing generated rasters
grass.run_command('g.remove', type = 'raster', pattern = '*HABMAT', flags = 'f')
grass.run_command('g.remove', type = 'raster', pattern = '*m', flags = 'f')
grass.run_command('g.remove', type = 'raster', pattern = '*AreaHA', flags = 'f')
grass.run_command('g.remove', type = 'raster', pattern = '*pid', flags = 'f')

# OK!
#-------------------------------


#-------------------------------
# Now let's test the function to diversity

python

# import modules
import os
import grass.script as grass

# folder for saving outputs
output_dir = r'/home/leecb/Github/LS_METRICS/test_output'

# Change dir
ls_metrics_dir = r'/home/leecb/Github/LS_METRICS/_LSMetrics_v1_0_0_stable'
os.chdir(ls_metrics_dir)
from LSMetrics_v1_0_0 import create_binary, createtxt, create_TXTinputBIODIM, lsmetrics_run, landscape_diversity

# 1) For only one map
list_of_maps = ['SP_RioClaro_use_raster']
scales = [100, '500']

landscape_diversity(input_maps = list_of_maps, 
                    scale_list = scales, method = ['simpson', 'renyi'], alpha = [2],
                    append_name = '', current_mapset = 'PERMANENT',
                    export = True, dirout = output_dir)

# 2) For only one map using a binary as input - to see what happens
list_of_maps = ['SP_RioClaro_use_raster']
scales = [100, '500']
habitat_is = ['4','5'] 

# With zero
bin_map_list = create_binary(list_maps = list_of_maps, list_habitat_classes = habitat_is, zero = True, prefix = 'zero_',
                             export = True, dirout = output_dir)

landscape_diversity(input_maps = bin_map_list, 
                    scale_list = scales, method = ['simpson', 'renyi'], alpha = [2],
                    append_name = '', current_mapset = 'PERMANENT',
                    export = True, dirout = output_dir)

# 3) For two maps
list_of_maps = ['SP_RioClaro_use_raster', 'APA_Sao_Joao_RJ_cut_SIRGAS_UTM23S']
scales = [100]

landscape_diversity(input_maps = list_of_maps, 
                    scale_list = scales, method = ['shannon', 'pielou'], alpha = [2],
                    append_name = '', current_mapset = 'PERMANENT',
                    export = True, dirout = output_dir)

# 4) For more than one map, using function lsmetrics_run
list_of_maps = ['SP_RioClaro_use_raster', 'APA_Sao_Joao_RJ_cut_SIRGAS_UTM23S']
list_scales = [100, 300]
methods = ['pielou', 'renyi']
alpha_val = ['0.5']

lsmetrics_run(input_maps = list_of_maps,
              outputdir = output_dir, output_prefix = '',
              calc_diversity = True, list_window_size_div = list_scales, 
              method_div = methods, alpha = alpha_val, export_diversity = True)

# Removing generated rasters
grass.run_command('g.remove', type = 'raster', pattern = '*diversity*', flags = 'f')



# test fragment
python

# import modules
import os
import grass.script as grass

# folder for saving outputs
output_dir = r'/home/leecb/Github/LS_METRICS/test_output'

# Change dir
ls_metrics_dir = r'/home/leecb/Github/LS_METRICS/_LSMetrics_v1_0_0_stable'
os.chdir(ls_metrics_dir)
from LSMetrics_v1_0_0 import create_binary, createtxt, create_TXTinputBIODIM, lsmetrics_run, patch_size, fragment_area

# 0) Calculate binary maps and patch size
list_of_maps = ['SP_RioClaro_use_raster', 'APA_Sao_Joao_RJ_cut_SIRGAS_UTM23S']
habitat_is = ['4','5','6']

# Create binary 0/1 maps
bin_map_list = create_binary(list_maps = list_of_maps, list_habitat_classes = habitat_is, zero = True, prefix = 'zero_')

list_pid, list_patch_area = patch_size(input_maps = bin_map_list)

# 1) For only one map and one scale
list_scales = [50]


lsmetrics_run(input_maps = [list_of_maps[0]],
              outputdir = output_dir, output_prefix = 'test_ero_d_dila_d_clump_c_', add_counter_name = True, 
              zero_bin = True, zero_metrics = False, use_calculated_bin = True,
              calcstats = True, prepare_biodim = True, remove_trash = True,
              binary = True, list_habitat_classes = habitat_is, export_binary = False,
              calc_patch_size = True, diagonal = False, export_patch_size = True, export_patch_id = True,
              calc_frag_size = True, list_edge_depth_frag = list_scales, export_frag_size = True, export_frag_id = True)

# Removing generated rasters        
grass.run_command('g.remove', type = 'raster', pattern = '*HABMAT', flags = 'f')
grass.run_command('g.remove', type = 'raster', pattern = '*AreaHA', flags = 'f')
grass.run_command('g.remove', type = 'raster', pattern = '*pid', flags = 'f')
grass.run_command('g.remove', type = 'raster', pattern = '*fid', flags = 'f')
