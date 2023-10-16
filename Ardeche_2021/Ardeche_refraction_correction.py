import glob
import os
import shutil

from lidar_platform import global_shifts
from lidar_platform.topo_bathymetry import refraction_correction, sbet
import lidar_platform.topo_bathymetry.bathymetry as bathy

idir = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\Ardeche_01102021\C3_after_corr\correction_refraction'
sbet_params = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\Data\Ardeche_01102021\params_sbet_Ardeche_01102021.txt'
water_surface = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\Ardeche_01102021\C2_after_corr\processing\water_surface\Ardeche_01102021_C2_corrected_thin_1m_surface_final.laz'
lines = glob.glob(os.path.join(idir, '*.laz'))
global_shift = global_shifts.Ardeche_2
cc_2023_01_06 = r'G:\RENNES1\PaulLeroy\CloudCompare_2023_01_06\CloudCompare.exe'

n_jobs = 10

#%% BE CAREFUL TO SPLIT LAZ FILES AS LASPY SEEMS LIMITED IN SIZE FOR LAZ WITH WAVEFORMS IN SOME CONFIGURATIONS
# lassplit -split 10000000 .\Ardeche_01102021_L005_C3_r_w.laz -digits 2 -olaz

#%% Add depth
for line in lines:
    out = bathy.add_depth_laz(line, water_surface, global_shift=global_shift, silent=True, cc_exe=cc_2023_01_06)
    corrected = refraction_correction.do_work([out], sbet_params, n_jobs)

#%% read_bfe sbet data
# sbet_obj = sbet.sbet_config(sbet_params)

#%% REFRACTION CORRECTION FOR ALL LINES
lines_with_depth = glob.glob(os.path.join(idir,'with_depth','to_split','*.laz'))
for line in lines_with_depth:
    corrected = refraction_correction.do_work([line], sbet_params, n_jobs)



