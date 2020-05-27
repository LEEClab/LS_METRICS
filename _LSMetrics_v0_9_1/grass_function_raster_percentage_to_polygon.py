#' ---
#' title: function raster percentage to polygon
#' author: mauricio vancine
#' date: 2020-05-27
#' ---

# import module
import grass.script as gs

# function
def raster_percentage_to_polygon(vector, raster_bin_list, col_names_list):
	# add columns
	cols = [str(i) + " double precision" for i in col_names_list]
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
		# rasterize the feature
		gs.run_command("v.to.rast", input = "vector_cat", output = "raster_cat", use = "val", val = 1, overwrite = True, quiet = True)
		# calculate the area to feature
		val_vector = gs.read_command("r.stats", flags = "an", input = "raster_cat", quiet = True)
		# for to raster
		for j in list(range(len(raster_bin_list))):
			# reclassify
			gs.mapcalc("raster_null = if(" + raster_bin_list[j] + " == 1, 1, null())", overwrite = True, quiet = True)
			# calculate area to raster
			val_raster = gs.read_command("r.stats", flags = "an", input = "raster_null", quiet = True)
			# calculate proportion
			if val_raster == "":
				val = 0
			else:
				val = round((float(str(val_raster).replace("\n","").replace("1 ", "")) / 
                float(str(val_vector ).replace("\n","").replace("1 ", ""))) * 100, 2)
			# add value to column
			gs.run_command("v.db.update", map = vector, column = col_names_list[j], value = str(val), where = "cat = " + i, quiet = True)
	# return mask for vector
	gs.run_command("g.region", flags = "a", vector = vector, quiet = True)
	gs.run_command("r.mask", vector = vector, overwrite = True, quiet = True)
	# remove temp files
	gs.run_command("g.remove", flags = "f", type = "vector", name = "vector_cat", quiet = True)
	gs.run_command("g.remove", flags = "f", type = "raster", name = "raster_null", quiet = True)
	gs.run_command("g.remove", flags = "f", type = "raster", name = "raster_cat", quiet = True)
