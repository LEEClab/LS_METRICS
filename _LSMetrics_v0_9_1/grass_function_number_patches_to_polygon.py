#' ---
#' title: function number patches to polygon
#' author: mauricio vancine
#' date: 2020-05-27
#' ---

# import module
import grass.script as gs

# function
def number_patches_to_polygon(vector, raster_id_list, col_names_list):
	# column names
	cols = [str(i) + " double precision" for i in col_names_list]
	# add columns
	gs.run_command("v.db.addcolumn", map = vector, column = cols, quiet = True)
	# cats
	cats = gs.read_command("db.select", flags = "c", sql = "SELECT cat FROM " + vector, quiet = True).split('\n')
	# remove absent values ''
	cats = [i for i in cats if i != '']
	# selection, region, mask and area
	for i in cats:
		# information
		print("Complete: " + str(round((int(i)/len(cats)*100), 2)) + "%")
		# select feature
		gs.run_command("v.extract", flags = "t", input = vector, output = "vector_cat", where = "cat = " + i, overwrite = True, quiet = True)
		# define region to feature
		gs.run_command("g.region", flags = "a", vector = "vector_cat", quiet = True)
		# define mask to feature
		gs.run_command("r.mask", vector = "vector_cat", overwrite = True, quiet = True)
		# for to raster
		for j in list(range(len(raster_id_list))):
			# mask raster
			gs.mapcalc("raster_id_cat = " + raster_id_list[j], overwrite = True, quiet = True)
			# assess patch ids
			ids = gs.read_command("r.category", map = "raster_id_cat").split('\n')
			# remove absent values ''
			ids = [i for i in ids if i != '']
			# number of patches 
			np = len(ids)
			# add value to column
			gs.run_command("v.db.update", map = vector, column = col_names_list[j], value = str(np), where = "cat = " + i, quiet = True)
	# return mask for vector
	gs.run_command("g.region", flags = "a", vector = vector, quiet = True)
	gs.run_command("r.mask", vector = vector, overwrite = True, quiet = True)
	# remove temp files
	gs.run_command("g.remove", flags = "f", type = "vector", name = "vector_cat", quiet = True)
	gs.run_command("g.remove", flags = "f", type = "raster", name = "raster_id_cat", quiet = True)