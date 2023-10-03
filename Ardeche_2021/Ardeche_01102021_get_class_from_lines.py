#Import modules
import os
from lidar_platform import misc

# Get class
workspace = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\Ardeche_01102021\05-Traitements\Raster\LAS\C2'
lines = os.path.join(workspace,'*.laz')
keep_class = 9
odir = os.path.join(workspace,f'class_{keep_class}')

os.makedirs(odir,exist_ok=True)

cpuCount = os.cpu_count()
print(f"cpu_count {cpuCount}")
cores = int((cpuCount / 2))

#%% Keep class
misc.run(f'las2las -i {lines} -keep_class {keep_class} -cores {cores} -odir {odir} -odix _class_{keep_class} -olaz')

#%% Merge LAZ
lines_class= os.path.join(odir, '*.laz')
out = os.path.join(odir, 'C2_r_1_water_surface_hd.laz')
misc.run(f'lasmerge -i {lines_class} -o {out}')