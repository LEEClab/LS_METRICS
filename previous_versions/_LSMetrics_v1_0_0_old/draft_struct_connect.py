import os
import grass.script as grass

grass.run_command('r.stats.zonal', base = 'SP_RioClaro_use_raster_HABMAT_pid', cover = 'SP_RioClaro_use_raster_HABMAT_0100m_fid',
                  method = 'count',  output = 'teste_count')

expression1 = 'test_count_area = teste_count * '+str(29.9961760945711)+' * '+str(29.9911798664122)+' / 10000'
grass.mapcalc(expression1, overwrite = True)

expression2 = 'test_count_area_frag = if(!isnull(SP_RioClaro_use_raster_HABMAT_0100m_fid), test_count_area, null())'
grass.mapcalc(expression2, overwrite = True)

round test_count_area_frag

subtrair: strut_connect = frag - test_count_area_frag
ou: strut_connect = patch_area - test_count_area_frag (se frag != test_count_area_frag)
