r.li.edgedensity input=SP_3543907_USO_raster_forest@PERMANENT config=C:\Users\Compaq 6910p\AppData\Roaming\GRASS7\r.li\land output=SP_3543907_USO_raster_forest_test
r.li.shape input=SP_3543907_USO_raster_forest@PERMANENT config=C:\Users\Compaq 6910p\AppData\Roaming\GRASS7\r.li\land output=SP_3543907_USO_raster_forest_shape
g.extension -s extension=r.pi url=
v.colors map=SP_3543907_USO@PERMANENT use=z
v.colors map=SP_3543907_USO@PERMANENT use=z column=CLASSE_USO color=random
r.in.gdal input=/home/leecb/Github/LS_METRICS/DB_demo/APA_Sao_Joao_RJ_cut_SIRGAS_UTM23S.tif output=APA_Sao_Joao_RJ_cut_SIRGAS_UTM23S
r.colors map=APA_Sao_Joao_RJ_cut_SIRGAS_UTM23S@PERMANENT color=random
r.colors map=APA_Sao_Joao_RJ_cut_SIRGAS_UTM23S@PERMANENT color=aspectcolr
r.colors map=APA_Sao_Joao_RJ_cut_SIRGAS_UTM23S@PERMANENT color=byg
r.colors map=APA_Sao_Joao_RJ_cut_SIRGAS_UTM23S@PERMANENT color=ryg
r.colors map=APA_Sao_Joao_RJ_cut_SIRGAS_UTM23S@PERMANENT color=wave
g.mapset -l
g.list rast
g.list vect
python
clear
clear
g.region -p
g.list rast
g.remove rast patt=*
g.remove rast patt=* -f
exit
r.info map=SP_RioClaro_use_raster@PERMANENT
raster_what()
g.list rast
g.remove rast patt=*HABMAT
g.remove rast patt=*HABMAT -f
g.list rast
r.info map=zero_zero_SP_RioClaro_use_raster_HABMAT_patch_AreaHA@PERMANENT
r.info map=null_zero_SP_RioClaro_use_raster_HABMAT_patch_AreaHA@PERMANENT
r.info map=zero_APA_Sao_Joao_RJ_cut_SIRGAS_UTM23S_HABMAT_pid@PERMANENT
r.info map=zero_SP_RioClaro_use_raster_HABMAThabitat_pct_100m@PERMANENT
r.info map=zero_SP_RioClaro_use_raster_HABMAThabitat_pct_200m@PERMANENT
r.info map=zero_SP_RioClaro_use_raster_HABMAT@PERMANENT
g.list rast
# Removing generated rasters        
grass.run_command('g.remove', type = 'raster', pattern = '*HABMAT', flags = 'f')
grass.run_command('g.remove', type = 'raster', pattern = '*AreaHA', flags = 'f')
grass.run_command('g.remove', type = 'raster', pattern = '*pid', flags = 'f')
grass.run_command('g.remove', type = 'raster', pattern = '*fid', flags = 'f')
python
# Removing generated rasters        
grass.run_command('g.remove', type = 'raster', pattern = '*HABMAT', flags = 'f')
grass.run_command('g.remove', type = 'raster', pattern = '*AreaHA', flags = 'f')
grass.run_command('g.remove', type = 'raster', pattern = '*pid', flags = 'f')
grass.run_command('g.remove', type = 'raster', pattern = '*fid', flags = 'f')
# Removing generated rasters        
grass.run_command('g.remove', type = 'raster', pattern = '*HABMAT', flags = 'f')
grass.run_command('g.remove', type = 'raster', pattern = '*AreaHA', flags = 'f')
grass.run_command('g.remove', type = 'raster', pattern = '*pid', flags = 'f')
grass.run_command('g.remove', type = 'raster', pattern = '*fid', flags = 'f')
python
python
python
python
python
python
g.list rast
python
python
python
python
python
python
python
python
python
python
python
python
gap_crossing_pixels
python
python
g.remove rast pattern=*
g.remove rast pattern=zero*
g.remove rast pattern=zero* -f
g.remove rast pattern=zero* -f
g.remove rast pattern=*
python
python
python
g.list rast
clear
exit
cd Github/
ls
cd LS_METRICS/
cd _LSMetrics_v1_0_0_stable/
ls
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
git status
cd ..
git status
git add *
git status
git commit -m "test GUI v1"
git push origin master
git push origin master
git pull
python LSMetrics_v1_0_0.py
python _LSMetrics_v1_0_0_stable/LSMetrics_v1_0_0.py
cd _LSMetrics_v1_0_0_stable/
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
git statys
git status
git add *
git commit -m "test GUI v2"
git push origin master
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
git add *
git commit -m "test GUI v3"
git push 
git config credential.helper store
git push https://github.com/LEEClab/LS_METRICS.git
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
git add *
git commit -m "test GUI v4"
git push origin master
git push origin master
python LSMetrics_v1_0_0.py
git add *
git commit -m "test GUI v5"

python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
git add *
git commit -m "test GUI v6"
git push origin master
git add *
git commit -m "test GUI v7"
git push origin master
git push origin master
python LSMetrics_v1_0_0.py
git add *
git commit -m "test GUI v8"
git push origin master
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
git add *
git commit -m "test GUI v9"
git push origin master
git push origin master
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
git add *
git commit -m "test GUI v10"
git push origin master
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
git add *
git commit -m "test GUI v11"
git push origin master
git push origin master
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
git add *
git commit -m "test GUI v12"
git push origin master
python LSMetrics_v1_0_0.py
g.list rast
g.gui
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
g.remove rast patt=*
g.remove rast patt=*HABMAT*
g.remove rast patt=*HABMAT* -f
g.remove rast patt=*HABMAT* -f
g.remove rast patt=*HABMAT* -f
python LSMetrics_v1_0_0.py
glist rast
g.list rast
clear
python
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
g.remove rast patt=*HABMAT* -f
g.remove rast patt=*HABMAT* -f
g.remove rast patt=*HABMAT* -f
clear
g.list rast
clear
python LSMetrics_v1_0_0.py
g.remove rast patt=*HABMAT* -f
g.remove rast patt=*HABMAT* -f
g.list rast
exit
r.import input=/home/leecb/Github/LS_METRICS/test_output/test_ero_d_dila_d_clump_c_0001_SP_RioClaro_use_raster_HABMAT_pid.tif output=test_ero_d_dila_d_clump_c_0001_SP_RioClaro_use_raster_HABMAT_pid
r.colors map=test_ero_d_dila_d_clump_c_0001_SP_RioClaro_use_raster_HABMAT_pid@PERMANENT color=random
r.import input=/home/leecb/Github/LS_METRICS/test_output/test_ero_d_dila_d_clump_c_0001_SP_RioClaro_use_raster_HABMAT_patch_AreaHA.tif output=test_ero_d_dila_d_clump_c_0001_SP_RioClaro_use_raster_HABMAT_patch_AreaHA
r.import input=/home/leecb/Github/LS_METRICS/test_output/test_ero_c_dila_c_clump_c_0001_SP_RioClaro_use_raster_HABMAT_0050m_fid.tif output=test_ero_c_dila_c_clump_c_0001_SP_RioClaro_use_raster_HABMAT_0050m_fid
r.import input=/home/leecb/Github/LS_METRICS/test_output/test_ero_d_dila_d_clump_c_0001_SP_RioClaro_use_raster_HABMAT_0050m_fid.tif output=test_ero_d_dila_d_clump_c_0001_SP_RioClaro_use_raster_HABMAT_0050m_fid
cd Github/LS_METRICS/_LSMetrics_v1_0_0_stable/
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
cd ..
git status
git status
git status
clear
git status
cd _LSMetrics_v1_0_0_stable/
python LSMetrics_v1_0_0.py
g.list rast
g.remove rast patt=*HABMAT* -F
g.remove rast patt=*HABMAT* -f
g.remove rast patt=*HABMAT* -f
g.remove rast patt=*patch* -f
g.remove rast patt=*pid* -f
g.list rast
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
python LSMetrics_v1_0_0.py
g.list rast
g.remove rast patt=*HABMAT* -f
g.remove rast patt=*HABMAT* -f
g.list rast
clear
exit
cd Github/LS_METRICS/
cd _LSMetrics_v1_0_0_stable/
python LSMetrics_v1_0_0.py
exit
cd Github/LS_METRICS/
git status
cd _LSMetrics_v1_0_0/
ls
python LSMetrics_v1_0_0.py 
g.list rast
g.list rast
python
exit
g.list rast
g.list rast
g.remove rast patt="*HABMAT* -f

g.remove rast patt=*HABMAT* -f
g.remove rast patt=*HABMAT* -f
g.list rast
g.remove rast patt=*test* -f
g.list rast
clear
exit
cd Github/LS_METRICS/_LSMetrics_v1_0_0/
python LSMetrics_v1_0_0.py 
g.list rast
g.list rast
g.remove rast patt=*conne* -f
g.remove rast patt=*conne* -f
g.list rast
clear
ls
python LSMetrics_v1_0_0.py 
python LSMetrics_v1_0_0.py 
python LSMetrics_v1_0_0.py 
python LSMetrics_v1_0_0.py 
python LSMetrics_v1_0_0.py 
python LSMetrics_v1_0_0.py 
python LSMetrics_v1_0_0.py 
python LSMetrics_v1_0_0.py 
exit
g.list rast
g.remove rast patt=*HABMAT* -f
g.remove rast patt=*HABMAT* -f
g.list rast
CLEAR
clear
exit
cd Github/LS_METRICS/_LSMetrics_v1_0_0/
ls
python LSMetrics_v1_0_0.py 
python LSMetrics_v1_0_0.py 
python LSMetrics_v1_0_0.py 
python LSMetrics_v1_0_0.py 
python
python
exit
