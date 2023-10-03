import glob
import os

from joblib import Parallel, delayed
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np

from lidar_platform import cc, global_shifts
from lidar_platform.qc import overlap_map, overlap as over, overlap_control

#%% Same parameters for C2, C3 and C2C3
results_dir = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\Data'
mission = 'Ardeche_18102021'
C2_dir = 'C2'
C3_dir = 'C3'
C2C3_dir = 'C2C3_after_corr'
cc_option_mission = 'Ardeche'
water_surface = "Ardeche_01102021_C2_corrected_thin_1m_surface_final.laz"

#%% THIN LINES

idir = f'{results_dir}\{mission}\{C2_dir}'
pattern = '*.laz'
odir = f'{results_dir}\\04-QC\Overlap\{mission}\{C2_dir}'
over.thin_lines(idir, pattern, odir)

#%% OVERLAP CONTROL C2

workspace= f'{results_dir}\\04-QC\Overlap\{mission}'
lines_dir_a = f'{results_dir}\{mission}\{C2_dir}'
m3c2_params = "m3c2_params.txt"
global_shift = global_shifts.Ardeche

cc_options = ['standard', 'LAS_auto_save', cc_option_mission]
line_nb_digits = 2
line_template = [f'{mission}_L',line_nb_digits, "_C2_r_1.laz"]
max_uncertainty = 0.1
settings = [cc_options, line_template, max_uncertainty]

folder = C2_dir

a = overlap_control.Overlap(workspace, lines_dir_a, settings, m3c2_params, water_surface=water_surface)
a.preprocessing(folder, pattern='*_thin.laz', use_water_surface=False)
a.processing(global_shift)

#%% THIN LINES C3
idir = f'{results_dir}\{mission}\{C3_dir}'
pattern = '*.laz'
odir = f'{results_dir}\\04-QC\Overlap\{mission}\{C3_dir}'
over.thin_lines(idir, pattern, odir)

#%% OVERLAP CONTROL C3

workspace = f'{results_dir}\\04-QC\Overlap\{mission}'
lines_dir_a = f'{results_dir}\{mission}\{C3_dir}'
m3c2_params = "m3c2_params.txt"
global_shift = global_shifts.Ardeche

cc_options = ['standard', 'LAS_auto_save', cc_option_mission]
line_nb_digits = 2
line_template = [f'{mission}_L',line_nb_digits, "_C3_r_1.laz"]
max_uncertainty = 0.1
settings = [cc_options, line_template, max_uncertainty]

folder = C3_dir

a = overlap_control.Overlap(workspace, lines_dir_a, settings, m3c2_params, water_surface=water_surface)
a.preprocessing(folder, pattern='*_thin.laz', use_water_surface=False)
a.processing(global_shift)

#%% THIN LINES C2_C3

idir = f'{results_dir}\{mission}\{C2C3_dir}'
pattern = '*.laz'
odir = f'{results_dir}\\04-QC\Overlap\{mission}\{C2C3_dir}'
over.thin_lines(idir, pattern, odir)

#%% OVERLAP CONTROL C2_C3

workspace = f'{results_dir}\\04-QC\Overlap\{mission}'
lines_dir_a = f'{results_dir}\{mission}\{C2C3_dir}'
lines_dir_b = lines_dir_a
m3c2_params = "m3c2_params.txt"
global_shift = global_shifts.Ardeche

cc_options = ['standard', 'LAS_auto_save', cc_option_mission]
line_nb_digits = 2
line_template = [f'{mission}_L', line_nb_digits, "_C2_r_1.laz"]
line_template_b = [f'{mission}_L', line_nb_digits, "_C3_r_1.laz"]
max_uncertainty = 0.1
settings = [cc_options, line_template, max_uncertainty]

folder = C2C3_dir

a = overlap_control.Overlap(workspace, lines_dir_a, settings, m3c2_params, water_surface=water_surface)
a.preprocessing_c2_c3(folder, lines_dir_b, line_template_b)
a.processing(global_shift)

