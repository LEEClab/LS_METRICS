import grass.script as grass

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


def pielou_index(mapin, radius_m):
    """
    Calcula o índice de Pielou em uma janela definida por raio (em metros).
    Fórmula: J = H' / ln(S)
    Onde:
      - H' = índice de Shannon não normalizado
      - S  = número de classes
    Gera o mapa final:
    {mapin}_Pielou_{raio:04d}m
    """

    # --- converte raio para janela
    window_cells, diameter_m = radius_to_window(mapin, radius_m)
    grass.message(f"🪟 Raio: {radius_m} m -> Janela: {window_cells} células (~{diameter_m:.1f} m de diâmetro)")

    # classes presentes
    stats_out = grass.read_command('r.stats', input=mapin, flags='n', separator=',')
    CodProcess = [int(x) for x in stats_out.strip().splitlines() if x.strip().isdigit()]
    n_classes = len(CodProcess)

    if n_classes < 2:
        grass.message("⚠️ Apenas uma classe encontrada, índice de Pielou = 0")
        outname = f"{mapin}_Pielou_{radius_m:04d}m"
        grass.mapcalc(f"{outname} = 0", overwrite=True, quiet=True)
        return

    # listas temporárias
    bin_maps, neigh_maps, pi_maps, term_maps = [], [], [], []

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

    # soma total
    grass.run_command('r.series',
                      input=neigh_maps,
                      output='tmp_sumRasts',
                      method='sum',
                      overwrite=True)

    # proporções e termos de Shannon
    for i in neigh_maps:
        pname = f"{i}_pi"
        tname = f"{i}_term"
        grass.mapcalc(f"{pname} = {i} / tmp_sumRasts", overwrite=True, quiet=True)
        grass.mapcalc(f"{tname} = if({pname} > 0, {pname} * log({pname}), 0)", overwrite=True, quiet=True)
        pi_maps.append(pname)
        term_maps.append(tname)

    # Shannon bruto (H’)
    grass.run_command('r.series',
                      input=term_maps,
                      output=f"tmp_shannon_raw_R{radius_m}m",
                      method='sum',
                      overwrite=True)
    grass.mapcalc(f"tmp_H_R{radius_m}m = -1 * tmp_shannon_raw_R{radius_m}m", overwrite=True, quiet=True)

    # Pielou
    outname = f"{mapin}_Pielou_{radius_m:04d}m"
    grass.mapcalc(f"{outname} = tmp_H_R{radius_m}m / log({n_classes})", overwrite=True, quiet=True)

    # limpeza
    to_remove = bin_maps + neigh_maps + pi_maps + term_maps + [
        "tmp_sumRasts",
        f"tmp_shannon_raw_R{radius_m}m",
        f"tmp_H_R{radius_m}m"
    ]
    grass.run_command('g.remove', type='rast', name=to_remove, flags='f', quiet=True)

    grass.message(f"✅ Mapa final gerado: {outname}")


# -------------------
# Exemplo de uso
# -------------------
inputmap = 'cenario_4_cut_teste_tif'
pielou_index(inputmap, 45)
pielou_index(inputmap, 90)
