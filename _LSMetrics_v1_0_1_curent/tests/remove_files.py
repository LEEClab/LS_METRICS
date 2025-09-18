import grass.script as grass

port = grass.list_grouped ('rast', pattern = '*HABMAT*') ['PERMANENT']
#print(port)

for i in port:
    print(i)
    grass.run_command('g.remove', type="raster", name=i+'@PERMANENT', flags='f')

