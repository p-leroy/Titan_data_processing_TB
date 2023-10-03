# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 2023
@author: Thomas Bernard
"""

# %% init

import glob
import multiprocessing
import os

from lidar_platform import misc
from lidar_platform.qc import assembly_plan

idir = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\Ardeche_01102021\C2_after_corr'

buffer = 25  # default step size of lasground_new is 25 meters
cores = 50
o = 'C2.laz'
tile_size = 500

lines = os.path.join(idir, '*.laz')
lax = os.path.join(idir, '*.lax')
dir_tiles = os.path.join(idir, f'tiles_{tile_size}')
dir_tiles_gc = os.path.join(idir, f'tiles_{tile_size}_gc')
dir_tiles_ground = os.path.join(idir, 'tiles_ground')
dir_tiles_other = os.path.join(idir, 'tiles_other')
tiles = os.path.join(dir_tiles, '*.laz')
tiles_g = os.path.join(dir_tiles_gc, '*_g.laz')
tiles_gc = os.path.join(dir_tiles_gc, '*_gc.laz')
tiles_ground = os.path.join(dir_tiles_ground, '*_ground.laz')
tiles_ground_1 = os.path.join(dir_tiles_ground, '*_ground_1.laz')
tiles_ground_1_thin = os.path.join(dir_tiles_ground, '*_ground_1_thin.laz')
tiles_other = os.path.join(dir_tiles_other, '*_other.laz')
odir = os.path.join(idir, 'processing')
out = os.path.join(odir, 'C2_r_1_ground_thin_1m.laz')

os.makedirs(dir_tiles, exist_ok=True)  # tiles
os.makedirs(dir_tiles_gc, exist_ok=True)  # tiles after lasground and lasclassify (classes 1, 2, 5, 6)
os.makedirs(dir_tiles_ground, exist_ok=True)
os.makedirs(dir_tiles_other, exist_ok=True)
os.makedirs(odir, exist_ok=True)


cpuCount = multiprocessing.cpu_count()
print(f"cpu_count {cpuCount}")


def remove(file):
    for f in glob.glob(file):
        os.remove(f)


#%% index las files
misc.run(f'lasindex -i {lines} -cores {cores}')
# build tiles
misc.run(f'lastile -i {lines} -tile_size {tile_size} -buffer {buffer} -cores {cores} -odir {dir_tiles} -o {o}')

#%% CLASSIFY
# bare-earth extraction: ground points (class = 2) and non-ground points (class = 1)
misc.run(f'lasground_new -i {tiles} -cores {cores} -compute_height -town -odir {dir_tiles_gc} -odix _g -olaz')
# classify high vegetation (class = 5) and buildings (class = 6)
misc.run(f'lasclassify -i {tiles_g} -cores {cores} -odix c -olaz')

#%% SEPARATE CLASSES
# keep only ground points (class = 2)
misc.run(f'las2las -i {tiles_gc} -keep_class 2 -cores {cores} -odir {dir_tiles_ground} -odix _ground -olaz')
# drop ground points (class = 2)
misc.run(f'las2las -i {tiles_gc} -drop_class 2 -cores {cores} -odir {dir_tiles_other} -odix _other -olaz')
# remove buffer (will add _1 to each tile name)
misc.run(f'lastile -i {tiles_ground} -remove_buffer -cores {cores} -olaz')
# remove buffer (will add _1 to each tile name)
misc.run(f'lastile -i {tiles_other} -remove_buffer -cores {cores} -olaz')

#%% THIN DATA AND MERGE
misc.run(f'lasthin -i {tiles_ground_1} -step 1 -lowest -cores {cores} -odix _thin -olaz')
misc.run(f'lasmerge -i -v {tiles_ground_1_thin} -o {out}')


#%% ASSEMBLY PLAN FOR TILES
assembly_plan.from_tiles(dir_tiles, '202109', tile_size=tile_size, coords_loc=1)

#%% ASSEMBLY PLAN FOR LINES
assembly_plan.from_lines(glob.glob(lines), idir)

#%% CLEAN TEMPORARY FILES
remove(lax)
remove(tiles_g) # ground and non-ground points with buffer
remove(tiles_ground) # only ground points with buffer
remove(tiles_ground_1_thin) # thin ground only points without buffer
remove(tiles_other) # other classes with buffer

#%% REMOVE BUFFER OF GC TILES
dir_gc_without_buffer = os.path.join(dir_tiles_gc, 'without_buffer')
os.makedirs(dir_gc_without_buffer , exist_ok=True)  # tiles
misc.run(f'lastile -i {tiles_gc} -remove_buffer -cores {cores} -odir {dir_gc_without_buffer} -olaz')