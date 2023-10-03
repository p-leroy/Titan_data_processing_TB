import glob
import os

from joblib import Parallel, delayed

from lidar_platform import bathymetry, global_shifts
from lidar_platform.tools import cc

idir = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\Ardeche_01102021\C3_after_corr\correction_refraction\tiles_g\without_buffer\lines'
lines = glob.glob(os.path.join(idir, '*.laz'))
# water surface hd
class_9 = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\Ardeche_01102021\05-Traitements\Raster\LAS\C2\class_9\C2_r_1_water_surface_hd.laz'
# bathymetry
class_16 = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\Ardeche_01102021\C3_after_corr\correction_refraction\processing\bathymetry\C3_r_thin_lowest_lastOnly_1m_C2C3_propagation_step_1_ref_corr.laz'
# water_volume
class_15 = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\Ardeche_01102021\C3_after_corr\correction_refraction\processing\bathymetry\C3_r_thin_lowest_lastOnly_1m_C2C3_bathymetry_seed_ref_corr_water_column.laz'
# bathymetry HD
lines_15_16_dir = r'G:\RENNES1\Vieux_Rhin_2022\processing\C3_denoised\lines_1_2_5_6\lines_15_16'
# class 16 extracted from full waveform
class_16_fwf_21 = r'G:\RENNES1\Vieux_Rhin_2022\06-Livrables\tmp\fwf\c3-20220321_fwf_16.laz'
class_16_fwf_22 = r'G:\RENNES1\Vieux_Rhin_2022\06-Livrables\tmp\fwf\c3-20220322_fwf_16.laz'

global_shift = global_shifts.Ardeche_2

#%% ADD DEPTH AS A SCALAR FIELD
with_depth = Parallel(n_jobs=10, verbose=0)(
    delayed(bathymetry.add_depth)(line, class_9, global_shift)
    for line in lines)

#%% COMPUTE DISTANCES TO CLASS 16
c2c_class_16 = Parallel(n_jobs=10, verbose=0)(
    delayed(bathymetry.c2c_class_16)(line, class_16, global_shift)
    for line in with_depth)

#%% CLASSIFY CLASS 16 POINTS
#c2c_class_16 = glob.glob(r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\Ardeche_01102021\C3_after_corr\correction_refraction\tiles_g\without_buffer\lines\with_depth\c2c_class_16\*.sbf')
with_16 = Parallel(n_jobs=10, verbose=0)(
    delayed(bathymetry.get_class_16_hd)(line, lastools_gc=True)
    for line in c2c_class_16)

#%% COMPUTE DISTANCES TO CLASS 15
with_16 = glob.glob(r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\Ardeche_01102021\C3_after_corr\correction_refraction\tiles_g\without_buffer\lines\with_depth\c2c_class_16\with_16\*.sbf')
c2c_class_15 = Parallel(n_jobs=15, verbose=0)(
    delayed(bathymetry.c2c_class_15)(line, class_15, global_shift)
    for line in with_16)

#%% GET CLASS 15 HD FROM WATER SURFACE (depth) AND CLASS 15 (distances computed previously)
with_15 = Parallel(n_jobs=10, verbose=0)(
    delayed(bathymetry.get_class_15_hd)(line)
    for line in c2c_class_15)

#%% CONVERT TO LAZ
results = Parallel(n_jobs=10, verbose=0)(
    delayed(cc.to_laz)(line, remove=True)
    for line in with_15)

#%% MOVE LAZ TO 05-Traitements/Raster/LAS/C3
with_15= r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\Ardeche_01102021\C3_after_corr\correction_refraction\tiles_g\without_buffer\lines\with_depth\c2c_class_16\with_16\c2c_class_15\with_15'
raster_las_c3 = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\Ardeche_01102021\05-Traitements\Raster\LAS\C3'
laz = glob.glob(os.path.join(with_15, '*.laz'))
for file in laz:
    shutil.move(file, raster_las_c3)

#%% EXTRACT LINES FROM CLASS 16 FWF
id_name = work.load_id_name_dictionary(r'G:\RENNES1\Vieux_Rhin_2022\processing\C3_denoised\id_name.json')
bathymetry.extract_lines_from_class_16_fwf(class_16_fwf_21, id_name)
bathymetry.extract_lines_from_class_16_fwf(class_16_fwf_22, id_name)