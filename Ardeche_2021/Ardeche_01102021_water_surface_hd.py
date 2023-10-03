import glob
import os
import shutil

from joblib import Parallel, delayed

from tools import cc
from topo_bathymetry import water_surface as water
from lidar_platform import global_shifts

idir = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\Ardeche_01102021\C2_after_corr\tiles_500_gc\without_buffer\lines'
lines = glob.glob(os.path.join(idir, '*.laz'))

class_9 = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\Ardeche_01102021\C2_after_corr\processing\water_surface\Ardeche_01102021_C2_corrected_thin_1m_surface_final.laz'
class_15_16 = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\Ardeche_01102021\C3_after_corr\correction_refraction\processing\bathymetry\C3_r_thin_lowest_lastOnly_1m_C2C3_bathymetry_seed_ref_corr.laz'

global_shift = global_shifts.Ardeche_2

#%% COMPUTE DISTANCES BETWEEN FLIGHT LINE AND WATER SURFACE
c2c = Parallel(n_jobs=10, verbose=0)(
    delayed(water.c2c_class_9)(line, class_9, global_shift)
    for line in lines)

#%% CLASSIFY WATER SURFACE IN FLIGHT LINE
c2c = glob.glob(os.path.join(idir,'c2c_class_9', f'*.sbf'))
sbf_with_9 = Parallel(n_jobs=10, verbose=0)(
    delayed(water.classify_class_9_in_line)(line, xy_max=5, lastools_gc=True)
    for line in c2c)

#%% compute distances to class 15 and class 16 merged
i_dir = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\Ardeche_01102021\C2_after_corr\tiles_500_gc\without_buffer\lines\c2c_class_9\lines_with_9'
i_corr = glob.glob(os.path.join(i_idir,'*.sbf'))
c2c_15_16 = Parallel(n_jobs=10, verbose=0)(
    delayed(water.c2c_class_15_16)(line, class_15_16, global_shift)
    for line in i_corr)

#%% reclassify the ground in C2 if needed
c2c_15_16 = glob.glob(os.path.join(i_dir,'c2c_class_15_16', f'*.sbf'))
with_2_corrected = Parallel(n_jobs=10, verbose=0)(
    delayed(water.reclassify_class_2_using_class_15_16)(line, xy_max=2)
    for line in c2c_15_16)

#%% CONVERT TO LAZ
with_2_corrected = glob.glob(r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\Ardeche_01102021\C2_after_corr\tiles_500_gc\without_buffer\lines\c2c_class_9\lines_with_9\c2c_class_15_16\lines_with_2_corr\*.sbf')
laz_results = Parallel(n_jobs=10, verbose=0)(
    delayed(cc.to_laz)(line, remove=True)
    for line in with_2_corrected)

#%% CONVERT TO LAZ
lines_with_9 = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\Ardeche_01102021\C2_after_corr\tiles_500_gc\without_buffer\lines\c2c_class_9\lines_with_9'
sbf = glob.glob(os.path.join(lines_with_9, '*.sbf'))
for count, file in enumerate(sbf):
    expected_out = os.path.splitext(file)[0] + '.laz'
    if os.path.exists(expected_out):
        print(f'laz already exists, nothing to do {expected_out}')
    else:
        print(f'{count} / {len(sbf)}')
        cc.to_laz(file)

#%% MOVE LAZ TO 05-Traitements/Raster/LAS/C2
lines_with_2_corrected= r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\Ardeche_01102021\C2_after_corr\tiles_500_gc\without_buffer\lines\c2c_class_9\lines_with_9\c2c_class_15_16\lines_with_2_corr'
raster_las_c2 = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\Ardeche_01102021\05-Traitements\Raster\LAS\C2'
laz = glob.glob(os.path.join(lines_with_2_corrected, '*.laz'))
for file in laz:
    shutil.move(file, raster_las_c2)