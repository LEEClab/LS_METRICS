import grass.script as grass
import os

class ShannonFunction:
    def __init__(self, inputmap, radius, export=False, export_path=None):
        self.inputmap = inputmap
        self.radius = radius
        self.export = export
        self.export_path = export_path

    def radius_to_window(self):
        info = grass.raster_info(self.inputmap)
        nsres = info.get('nsres')
        ewres = info.get('ewres')
        if nsres is None or ewres is None:
            raise RuntimeError("Não consegui identificar a resolução do raster. Confirme se está em projeção métrica.")
        cellsize = (abs(float(nsres)) + abs(float(ewres))) / 2.0
        radius_cells = int(round(float(self.radius) / cellsize))
        if radius_cells < 1:
            radius_cells = 1
        window_cells = 2 * radius_cells + 1
        diameter_m = window_cells * cellsize
        return window_cells, diameter_m

    def compute(self):
        mapin = self.inputmap
        radius_m = self.radius
        window_cells, diameter_m = self.radius_to_window()
        grass.message(f"🪟 Raio: {radius_m} m -> Janela: {window_cells} células (~{diameter_m:.1f} m de diâmetro)")

        stats_out = grass.read_command('r.stats', input=mapin, flags='n', separator=',')
        CodProcess = [int(x) for x in stats_out.strip().splitlines() if x.strip().isdigit()]

        bin_maps, neigh_maps, pi_maps, term_maps = [], [], [], []

        for i in CodProcess:
            cname = f"{i:05d}"
            binary_map = f"tmp_{mapin}_C{cname}"
            neigh_map  = f"tmp_{mapin}_C{cname}_R{radius_m}m"
            grass.mapcalc(f"{binary_map} = if({mapin} == {i}, 1, 0)", overwrite=True, quiet=True)
            grass.run_command('r.neighbors',
                              input=binary_map,
                              output=neigh_map,
                              method='sum',
                              size=window_cells,
                              overwrite=True)
            bin_maps.append(binary_map)
            neigh_maps.append(neigh_map)

        grass.run_command('r.series',
                          input=neigh_maps,
                          output='tmp_sumRasts',
                          method='sum',
                          overwrite=True)

        for i in neigh_maps:
            pname = f"{i}_pi"
            tname = f"{i}_term"
            grass.mapcalc(f"{pname} = {i} / tmp_sumRasts", overwrite=True, quiet=True)
            grass.mapcalc(f"{tname} = if({pname} > 0, {pname} * log({pname}), 0)", overwrite=True, quiet=True)
            pi_maps.append(pname)
            term_maps.append(tname)

        grass.run_command('r.series',
                          input=term_maps,
                          output=f"tmp_shannon_raw_R{radius_m}m",
                          method='sum',
                          overwrite=True)

        grass.mapcalc(f"tmp_shannon_R{radius_m}m = -1 * tmp_shannon_raw_R{radius_m}m", overwrite=True, quiet=True)

        outname = f"{mapin}_Shannon_{int(radius_m):04d}m"
        n_classes = len(CodProcess)
        if n_classes > 1:
            grass.mapcalc(f"{outname} = tmp_shannon_R{radius_m}m / log({n_classes})", overwrite=True, quiet=True)
        else:
            grass.mapcalc(f"{outname} = 0", overwrite=True, quiet=True)

        # Export condicional
        if self.export:
            if not self.export_path:
                raise ValueError("Você marcou export=True, mas não informou export_path.")
            if not os.path.exists(self.export_path):
                os.makedirs(self.export_path)
            output_file = os.path.join(self.export_path, f"{outname}.tif")
            grass.run_command('r.out.gdal',
                              input=outname,
                              output=output_file,
                              format='GTiff',
                              createopt='COMPRESS=LZW',
                              overwrite=True)
            grass.message(f"📤 Mapa exportado para: {output_file}")

        # Limpeza geral
        to_remove = bin_maps + neigh_maps + pi_maps + term_maps + [
            "tmp_sumRasts",
            f"tmp_shannon_raw_R{radius_m}m",
            f"tmp_shannon_R{radius_m}m"
        ]
        grass.run_command('g.remove', type='rast', name=to_remove, flags='f', quiet=True)

        grass.message(f"✅ Mapa final gerado: {outname}")
