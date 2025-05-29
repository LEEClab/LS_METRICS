import grass.script as grass

port = grass.list_grouped ('rast', pattern = '*') ['PERMANENT']
for i in port:
    if 'C' in i:
        grass.run_command('g.remove', type="raster", name=i, flags='f')
        print( i)
 


