import glob
import os

from joblib import Parallel, delayed
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np

from lidar_platform import cc
from lidar_platform.qc import overlap_map, overlap as over, overlap_control

#%% Same parameters for C2, C3 and C2C3
results_dir = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results'
mission = 'Ardeche_18102021'
C2_dir = 'C2_after_corr'
C3_dir = 'C3_after_corr'
C2C3_dir = 'C2C3_after_corr'
cc_option_mission = 'Ardeche'
water_surface = "Ardeche_01102021_C2_thin_1m_surface_final.laz"

#%% THIN LINES

idir = f'{results_dir}\{mission}\{C2_dir}'
pattern = '*.laz'
odir = f'{results_dir}\\04-QC\Overlap\{mission}\{C2_dir}'
over.thin_lines(idir, pattern, odir)

#%% OVERLAP CONTROL C2

workspace= f'{results_dir}\\04-QC\Overlap\{mission}'
lines_dir_a = f'{results_dir}\{mission}\{C2_dir}'
m3c2_params = "m3c2_params.txt"

cc_options = ['standard', 'LAS_auto_save', cc_option_mission]
line_nb_digits = 2
line_template = [f'{mission}_L',line_nb_digits, "_C2_r_1.laz"]
max_uncertainty = 0.1
settings = [cc_options, line_template, max_uncertainty]

folder = C2_dir

a = overlap_control.Overlap(workspace, lines_dir_a, settings, m3c2_params, water_surface=water_surface)
a.preprocessing(folder, pattern='*_thin.laz', use_water_surface=False)
a.processing()

#%% THIN LINES C3
idir = f'{results_dir}\{mission}\{C3_dir}'
pattern = '*.laz'
odir = f'{results_dir}\\04-QC\Overlap\{mission}\{C3_dir}'
over.thin_lines(idir, pattern, odir)

#%% OVERLAP CONTROL C3

workspace = f'{results_dir}\\04-QC\Overlap\{mission}'
lines_dir_a = f'{results_dir}\{mission}\{C3_dir}'
m3c2_params = "m3c2_params.txt"

cc_options = ['standard', 'LAS_auto_save', cc_option_mission]
line_nb_digits = 2
line_template = [f'{mission}_L',line_nb_digits, "_C3_r_1.laz"]
max_uncertainty = 0.1
settings = [cc_options, line_template, max_uncertainty]

folder = C3_dir

a = overlap_control.Overlap(workspace, lines_dir_a, settings, m3c2_params, water_surface=water_surface)
a.preprocessing(folder, pattern='*_thin.laz', use_water_surface=False)
a.processing()

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

cc_options = ['standard', 'LAS_auto_save', cc_option_mission]
line_nb_digits = 2
line_template = [f'{mission}_L', line_nb_digits, "_C2_r_1.laz"]
line_template_b = [f'{mission}_L', line_nb_digits, "_C3_r_1.laz"]
max_uncertainty = 0.1
settings = [cc_options, line_template, max_uncertainty]

folder = C2C3_dir

a = overlap_control.Overlap(workspace, lines_dir_a, settings, m3c2_params, water_surface=water_surface)
a.preprocessing_c2_c3(folder, lines_dir_b, line_template_b)
a.processing()

#%% PLOTS


def func(filepath, distance_filter):
    pc, sf, config = cc.read_sbf(filepath)

    # SF1 = Npoints_cloud1
    # SF2 = Npoints_cloud2
    # SF3 = STD_cloud1
    # SF4 = STD_cloud2
    # SF5 = significant change
    # SF6 = distance uncertainty
    # SF7 = M3C2 distance

    uncertainty = sf[:, 5]
    distance = sf[:, 6]

    select = ~np.isnan(uncertainty)
    select &= (uncertainty < distance_filter)
    select &= ~np.isnan(distance)
    select &= (distance < 1)

    m3c2_dist = distance[select]

    if len(m3c2_dist) > 100:
        line_select = np.unique(np.random.randint(0, len(m3c2_dist), int(0.5 * len(m3c2_dist))))
        results = m3c2_dist[line_select]
    else:
        results = []
    return results

workspace = r'G:\RENNES1\ThomasBernard\StripAlign\Multi_channel_test\results\QC\before_corr\Ardeche_01102021'
folder = 'C2'
list_filepath = glob.glob(os.path.join(workspace, folder, "*_m3c2_*.sbf"))

if True:
    max_uncertainty = 0.1
    result = Parallel(n_jobs=20, verbose=2)(delayed(func)(i, max_uncertainty) for i in list_filepath)
    np.savez_compressed(os.path.join(workspace, folder, "save_results_data_v1.npz"), np.concatenate(result))

npz = os.path.join(workspace, folder, "save_results_data_v1.npz")
f = np.load(npz)
tab = f[f.files[0]]
f.close()

print(np.mean(tab))
print(np.std(tab))

plt.figure(1)
plt.xlabel("Distance M3C2 (en cm)")
plt.ylabel("Fréquence")
plt.title('Histogramme des écarts en altitude\npour les données du canal vert')
plt.hist(tab * 100, bins=50, range=(-15, 15), edgecolor='white')
plt.ticklabel_format(axis="y", style='sci', scilimits=(0,0))
plt.text(x=-30,y=3000,s="Moyenne : -9cm\nEcart-type : 5.5cm")
out = os.path.join(workspace, folder,  "figure_C3_v1.png")
plt.savefig(out, dpi=150)
plt.show()