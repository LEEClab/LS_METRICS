import grass.script as grass
import math

def radius_to_window(mapname, radius_m):
    """
    Converte raio em metros para tamanho da janela em células (ímpar).
    """
    info = grass.raster_info(mapname)
    nsres = info.get('nsres')
    ewres = info.get('ewres')
    if nsres is None or ewres is None:
        raise RuntimeError("Não consegui identificar a resolução do raster. Confirme se está em projeção métrica.")

    cellsize = (abs(float(nsres)) + abs(float(ewres))) / 2.0
    radius_cells = int(round(float(radius_m) / cellsize))
    if radius_cells < 1:
        radius_cells = 1
    window_cells = 2 * radius_cells + 1
    diameter_m = window_cells * cellsize
    return window_cells, diameter_m


def renyi_index(mapin, radius_m, alpha=1.0):
    """
    Calcula o índice de Rényi em uma janela definida por raio (em metros) e parâmetro alpha.
    Gera o mapa final: {mapin}_Renyi_{alpha}_{raio:04d}m
    """
    if alpha == 1.0:
        grass.message("⚠️ alpha=1.0 equivale ao índice de Shannon. Considerar alpha diferente para Rényi.")

    window_cells, diameter_m = radius_to_window(mapin, radius_m)
    grass.message(f"🪟 Raio: {radius_m} m -> Janela: {window_cells} células (~{diameter_m:.1f} m de diâmetro)")

    # classes presentes
    stats_out = grass.read_command('r.stats', input=mapin, flags='n', separator=',')
    CodProcess = [int(x) for x in stats_out.strip().splitlines() if x.strip().isdigit()]

    if len(CodProcess) == 0:
        raise RuntimeError("Nenhuma classe encontrada no raster.")

    # listas temporárias
    bin_maps, neigh_maps, pi_maps, pi_alpha_maps = [], [], [], []

    # mapas binários e vizinhança
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

    # soma total de vizinhança
    grass.run_command('r.series',
                      input=neigh_maps,
                      output='tmp_sumRasts',
                      method='sum',
                      overwrite=True)

    # proporções (pi) e pi^alpha
    for i in neigh_maps:
        pname = f"{i}_pi"
        alpha_name = f"{i}_pi_alpha"
        grass.mapcalc(f"{pname} = {i} / tmp_sumRasts", overwrite=True, quiet=True)
        if alpha == 1.0:
            grass.mapcalc(f"{alpha_name} = {pname} * log({pname})", overwrite=True, quiet=True)
        else:
            grass.mapcalc(f"{alpha_name} = {pname} ^ {alpha}", overwrite=True, quiet=True)
        pi_maps.append(pname)
        pi_alpha_maps.append(alpha_name)

    # soma dos pi^alpha
    grass.run_command('r.series',
                      input=pi_alpha_maps,
                      output=f"tmp_renyi_sum_R{radius_m}m",
                      method='sum',
                      overwrite=True)

    # preparar nome final sem ponto no alpha
    alpha_str = str(alpha).replace('.', '_')
    outname = f"{mapin}_Renyi_{alpha_str}_{radius_m:04d}m"

    if alpha == 1.0:
        # Shannon
        grass.mapcalc(f"{outname} = -1 * tmp_renyi_sum_R{radius_m}m", overwrite=True, quiet=True)
    else:
        # Rényi
        grass.mapcalc(f"{outname} = log(tmp_renyi_sum_R{radius_m}m) / (1 - {alpha})", overwrite=True, quiet=True)

    # limpeza
    to_remove = bin_maps + neigh_maps + pi_maps + pi_alpha_maps + ["tmp_sumRasts", f"tmp_renyi_sum_R{radius_m}m"]
    grass.run_command('g.remove', type='rast', name=to_remove, flags='f', quiet=True)

    grass.message(f"✅ Mapa final gerado: {outname}")


# -------------------
# Exemplo de uso
# -------------------
inputmap = 'cenario_4_cut_teste_tif'
renyi_index(inputmap, 45, alpha=0.5)
renyi_index(inputmap, 90, alpha=2.0)
