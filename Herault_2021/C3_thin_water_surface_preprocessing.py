import glob
import os

from lidar_platform.tools import misc

idir = r'G:\RENNES1\ThomasBernard\StripAlign\Herault\results\Herault_30092021\C3_after_corr'
outname = 'C3_r_thin_lowest_lastOnly_1m.laz'

lines = os.path.join(idir, '*.laz')
lines_out_d = os.path.join(idir, 'lines_lowest')
lines_out = os.path.join(lines_out_d, '*.laz')
lines_out_1 = os.path.join(lines_out_d, '*_1.laz')

odir = o = os.path.join(idir, 'processing')
o = os.path.join(odir, outname)

cpuCount = os.cpu_count()
cores = int(cpuCount / 2)
print(f"cpu_count {cpuCount}")

os.makedirs(lines_out_d, exist_ok=True)  # tiles
os.makedirs(odir, exist_ok=True)  # processing

#%% THIN TILES, REMOVE BUFFERS AND MERGE
misc.run(f'lasthin -i {lines} -step 1 -lowest -last_only -cores {cores} -odir {lines_out_d} -odix _thin_lastOnly -olaz')
#misc.run(f'lastile -i {tiles_out} -remove_buffer -cores {cores} -olaz')
misc.run(f'lasmerge -i {lines_out} -o {o}')

#%% REMOVE TEMPORARY FILES
[os.remove(file) for file in glob.glob(lines_out)]