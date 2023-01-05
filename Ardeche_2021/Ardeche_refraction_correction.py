import glob
import os
import shutil

from lidar_platform.topo_bathymetry import refraction_correction

idir = r'G:\RENNES1\PaulLeroy\Brioude_30092021\05-Traitements\C3_r_denoised_g\with_depth\c2c_class_16\with_16\c2c_class_15\with_15'
sbet = r'G:\RENNES1\PaulLeroy\Brioude_30092021\SBET\params_sbet_Brioude_09_2022.txt'
lines = glob.glob(os.path.join(idir, '*.laz'))

n_jobs = 10

#%% REFRACTION CORRECTION FOR ALL LINES
corrected = refraction_correction.do_work(lines, sbet, n_jobs)

#%% MOVE OUTPUT FILES TO DELIVERABLES
to_move = glob.glob(os.path.join(idir, '*refraction_corrected.laz'))
[shutil.move(file, os.path.join(idir, 'ref_corr')) for file in to_move]

#%% FWF EXTRACTION REFRACTION CORRECTION
idir_fwf = r'G:\RENNES1\PaulLeroy\Brioude_30092021\05-Traitements\C3_r_fwf'
fwf_with_class_16 = os.path.join(idir_fwf, 'C3_r_w_selection_class_16.laz')
fwf_corrected = refraction_correction.do_work([fwf_with_class_16], sbet, n_jobs)