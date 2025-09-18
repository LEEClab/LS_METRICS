import grass.script as grass
import math
import os

class RenyiIndex:
    def __init__(self, mapin, radius, alpha=1.0, export=False, export_path=None):
        self.mapin = mapin
        self.radius = radius
        self.alpha = alpha
        self.export = export
        self.export_path = export_path

    def radius_to_window(self):
        """Converte raio em metros para tamanho da janela em células (ímpar)."""
        info = grass.raster_info(self.mapin)
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
        """Calcula o índice de Rényi."""
        if self.alpha == 1.0:
            grass.message("⚠️ alpha=1.0 equivale ao índice de Shannon. Considere alpha diferente para Rényi.")

        window_cells, diameter_m = self.radius_to_window()
        grass.message(f"🪟 Raio: {self.radius} m -> Janela: {window_cells} células (~{diameter_m:.1f} m de diâmetro)")

        # classes presentes
        stats_out = grass.read_command('r.stats', input=self.mapin, flags='n', separator=',')
        CodProcess = [int(x) for x in stats_out.strip().splitlines() if x.strip().isdigit()]
        if len(CodProcess) == 0:
            raise RuntimeError("Nenhuma classe encontrada no raster.")

        bin_maps, neigh_maps, pi_maps, pi_alpha_maps = [], [], [], []

        for i in CodProcess:
            cname = f"{i:05d}"
            binary_map = f"tmp_{self.mapin}_C{cname}"
            neigh_map  = f"tmp_{self.mapin}_C{cname}_R{self.radius}m"

            grass.mapcalc(f"{binary_map} = if({self.mapin} == {i}, 1, 0)", overwrite=True, quiet=True)
            grass.run_command('r.neighbors',
                              input=binary_map,
                              output=neigh_map,
                              method='sum',
                              size=window_cells,
                              overwrite=True)
            bin_maps.append(binary_map)
            neigh_maps.append(neigh_map)

        # soma total de vizinhança
        grass.run_command('r.series',
                          input=neigh_maps,
                          output='tmp_sumRasts',
                          method='sum',
                          overwrite=True)

        # proporções e pi^alpha
        for i in neigh_maps:
            pname = f"{i}_pi"
            alpha_name = f"{i}_pi_alpha"
            grass.mapcalc(f"{pname} = {i} / tmp_sumRasts", overwrite=True, quiet=True)
            if self.alpha == 1.0:
                grass.mapcalc(f"{alpha_name} = {pname} * log({pname})", overwrite=True, quiet=True)
            else:
                grass.mapcalc(f"{alpha_name} = {pname} ^ {self.alpha}", overwrite=True, quiet=True)
            pi_maps.append(pname)
            pi_alpha_maps.append(alpha_name)

        # soma dos pi^alpha
        grass.run_command('r.series',
                          input=pi_alpha_maps,
                          output=f"tmp_renyi_sum_R{self.radius}m",
                          method='sum',
                          overwrite=True)

        # nome final sem ponto no alpha
        alpha_str = str(self.alpha).replace('.', '_')
        outname = f"{self.mapin}_Renyi_{alpha_str}_{int(self.radius)}m"
        
        if self.alpha == 1.0:
            grass.mapcalc(f"{outname} = -1 * tmp_renyi_sum_R{self.radius}m", overwrite=True, quiet=True)
        else:
            grass.mapcalc(f"{outname} = log(tmp_renyi_sum_R{self.radius}m) / (1 - {self.alpha})", overwrite=True, quiet=True)

        # nome interno no GRASS sem .tif


        # exporta se necessário
        if self.export and self.export_path:
            if not os.path.exists(self.export_path):
                os.makedirs(self.export_path)
            # aqui adiciona a extensão .tif apenas no arquivo de saída
            export_file = os.path.join(self.export_path, f"{outname}.tif")
            grass.run_command('r.out.gdal', input=outname, output=export_file, format='GTiff', overwrite=True)
            grass.message(f"📂 Mapa exportado: {export_file}")

        # limpeza
        to_remove = bin_maps + neigh_maps + pi_maps + pi_alpha_maps + ["tmp_sumRasts", f"tmp_renyi_sum_R{self.radius}m"]
        grass.run_command('g.remove', type='rast', name=to_remove, flags='f', quiet=True)

        grass.message(f"✅ Mapa final gerado: {outname}")
        return outname


# -------------------
# Exemplo de uso
# -------------------
# renyi = RenyiIndex('cenario_4_cut_teste_tif', 45, alpha=0.5, export=True, export_path="D:/Resultados")
# renyi.compute()
