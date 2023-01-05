import glob
import os

from joblib import Parallel, delayed

from lidar_platform import bathymetry, global_shifts
from lidar_platform.tools import cc

idir = r'G:\RENNES1\PaulLeroy\Brioude_30092021\05-Traitements\C3_r_denoised_g'
lines = glob.glob(os.path.join(idir, '*.laz'))
# water surface
class_9 = r'G:\RENNES1\PaulLeroy\Brioude_30092021\06-Livrables\class_9_water_surface_1m.laz'
# bathymetry
class_16 = r'G:\RENNES1\PaulLeroy\Brioude_30092021\06-Livrables\class_16_bathymetry_1m.laz'
# water_volume
class_15 = r'G:\RENNES1\PaulLeroy\Brioude_30092021\06-Livrables\class_15_water_volume_1m.laz'
# bathymetry HD
lines_15_16_dir = r'G:\RENNES1\Vieux_Rhin_2022\processing\C3_denoised\lines_1_2_5_6\lines_15_16'
# class 16 extracted from full waveform
class_16_fwf_21 = r'G:\RENNES1\Vieux_Rhin_2022\06-Livrables\tmp\fwf\c3-20220321_fwf_16.laz'
class_16_fwf_22 = r'G:\RENNES1\Vieux_Rhin_2022\06-Livrables\tmp\fwf\c3-20220322_fwf_16.laz'

global_shift = global_shifts.brioude

#%% ADD DEPTH AS A SCALAR FIELD
with_depth = Parallel(n_jobs=10, verbose=0)(
    delayed(bathymetry.add_depth)(line, class_9, global_shift, i_to_rename=12)
    for line in lines)

#%% COMPUTE DISTANCES TO CLASS 16
c2c_class_16 = Parallel(n_jobs=10, verbose=0)(
    delayed(bathymetry.c2c_class_16)(line, class_16, global_shift)
    for line in with_depth)

#%% CLASSIFY CLASS 16 POINTS
with_16 = Parallel(n_jobs=10, verbose=0)(
    delayed(bathymetry.get_class_16_hd)(line, lastools_gc=True)
    for line in c2c_class_16)

#%% COMPUTE DISTANCES TO CLASS 15
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

#%% EXTRACT LINES FROM CLASS 16 FWF
id_name = work.load_id_name_dictionary(r'G:\RENNES1\Vieux_Rhin_2022\processing\C3_denoised\id_name.json')
bathymetry.extract_lines_from_class_16_fwf(class_16_fwf_21, id_name)
bathymetry.extract_lines_from_class_16_fwf(class_16_fwf_22, id_name)