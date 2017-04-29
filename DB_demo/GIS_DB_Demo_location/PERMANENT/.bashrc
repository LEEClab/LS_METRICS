test -r ~/.alias && . ~/.alias
PS1='GRASS 7.0.4 (GIS_DB_Demo_location):\w > '
grass_prompt() {
	LOCATION="`g.gisenv get=GISDBASE,LOCATION_NAME,MAPSET separator='/'`"
	if test -d "$LOCATION/grid3/G3D_MASK" && test -f "$LOCATION/cell/MASK" ; then
		echo [2D and 3D raster MASKs present]
	elif test -f "$LOCATION/cell/MASK" ; then
		echo [Raster MASK present]
	elif test -d "$LOCATION/grid3/G3D_MASK" ; then
		echo [3D raster MASK present]
	fi
}
PROMPT_COMMAND=grass_prompt
export GRASS_VERSION=7.0.4
export GRASS_GNUPLOT="gnuplot -persist"
export GRASS_PYTHON=python
export GRASS_ADDON_BASE=/home/leecb/.grass7/addons
export GRASS_PAGER=pager
export GRASS_HTML_BROWSER=xdg-open
export GRASS_PROJSHARE=/usr/share/proj
export PATH="/usr/lib/grass70/bin:/usr/lib/grass70/scripts:/home/leecb/.grass7/addons/bin:/home/leecb/.grass7/addons/scripts:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games"
export HOME="/home/leecb"
