import glob
import os

from lidar_platform.qc import assembly_plan
from lidar_platform import misc

idir = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\Ardeche_01102021\C3_after_corr\correction_refraction'

buffer = 25
cores = 50
o = 'C3.laz'
tile_size = 500

lines = os.path.join(idir, '*.laz')
lax = os.path.join(idir, '*.lax')
dir_tiles = os.path.join(idir, f'tiles_{tile_size}')
dir_tiles_g = os.path.join(idir, 'tiles_g')
dir_tiles_g_without_buffer = os.path.join(dir_tiles_g, 'without_buffer')
dir_tiles_ground = os.path.join(dir_tiles_g_without_buffer, 'ground')
tiles = os.path.join(dir_tiles, '*.laz')
tiles_g = os.path.join(dir_tiles_g, '*_g.laz')
tiles_g_without_buffer = os.path.join(dir_tiles_g_without_buffer, '*_g.laz')
tiles_g_thin = os.path.join(dir_tiles_g_without_buffer, '*_g_thin.laz')
tiles_ground = os.path.join(dir_tiles_ground, '*.laz')
odir = os.path.join(idir, 'processing')
out = os.path.join(odir, 'C3_r_1_ground_thin_1m.laz')

os.makedirs(dir_tiles, exist_ok=True)  # tiles
os.makedirs(dir_tiles_g, exist_ok=True)  # tiles classified with lasground (1 2)
os.makedirs(dir_tiles_g_without_buffer, exist_ok=True)
os.makedirs(dir_tiles_ground, exist_ok=True)
os.makedirs(odir, exist_ok=True)

cpuCount = os.cpu_count()
print(f"cpu_count {cpuCount}")
cores = int((cpuCount / 2))


#%% index las files
misc.run(f'lasindex -i {lines} -cores {cores}')
# build tiles
misc.run(f'lastile -i {lines} -tile_size {tile_size} -buffer {buffer} -cores {cores} -odir {dir_tiles} -o {o}')
#misc.run(f'lastile -i {lines} -tile_size 1000 -buffer 250 -cores {cores} -odir {dir_tiles} -o {o}')

#%% CLASSIFY
# bare-earth extraction: ground points (class = 2) and non-ground points (class = 1)
misc.run(f'lasground_new -i {tiles} -cores {cores} -town -compute_height -odir {dir_tiles_g} -odix _g -olaz')
# classify high vegetation (class = 5) and buildings (class = 6)
# NOT DONE BECAUSE BETTER RESULTS ARE OBTAINED BY INTERPOLATING THE CLASS FROM C2!
# misc.run(f'lasclassify -i {tiles_g} -cores {cores} -odix c -olaz')

#%% remove buffer (will add _1 to each tile name)
misc.run(f'lastile -i {tiles_g} -remove_buffer -cores {cores} -odir {dir_tiles_g_without_buffer} -olaz')

#%% keep only ground points for Poisson reconstruction
misc.run(f'las2las -i {tiles_g_without_buffer} -keep_class 2 -cores {cores} -odir {dir_tiles_ground} -odix _ground -olaz')

#%% THIN DATA AND MERGE
misc.run(f'lasthin -i {tiles_g_without_buffer} -keep_class 2 -step 1 -lowest -cores {cores} -odix _thin -olaz')
misc.run(f'lasmerge -i {tiles_g_thin} -o {out}')


#%% ASSEMBLY PLAN FOR TILES
assembly_plan.from_tiles(dir_tiles, '202109', tile_size=tile_size, coords_loc=1)

#%% ASSEMBLY PLAN FOR LINES
assembly_plan.from_lines(glob.glob(lines), idir)

#%% CLEAN TEMPORARY FILES
[os.remove(file) for file in glob.glob(lax)]
[os.remove(file) for file in glob.glob(tiles_g)]
[os.remove(file) for file in glob.glob(tiles_g_thin)]