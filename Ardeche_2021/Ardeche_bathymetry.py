import os

from lidar_platform import bathymetry

idir = r'G:\RENNES1\PaulLeroy\Brioude_30092021\05-Traitements'
# C3 input
c3_config = 'i_corr_not_classified'  # values are defined in bathymetry
c3_c2c3 = os.path.join(idir, 'C3_r_denoised', 'lines_i_correction',
                       'processing', 'C3_r_denoised_thin_lowest_lastOnly_1m_C2C3.bin')
# water surface
class_9 = os.path.join(idir, 'C2_r_denoised', 'processing', 'water_surface',
                             'water_surface_cleaned_NN5m_20_smoothed20.bin')


#%%
bathymetry_seed = bathymetry.extract_seed_from_water_surface(c3_c2c3, class_9, c3_config)

#%%
bathymetry_seed = r'G:\\RENNES1\\PaulLeroy\\Brioude_30092021\\05-Traitements\\C3_r_denoised\\lines_i_correction\\processing\\bathymetry\\C3_r_denoised_thin_lowest_lastOnly_1m_C2C3_bathymetry_seed.bin'

#%%
step = 0
bathymetry_n = bathymetry.propagate(c3_c2c3, bathymetry_seed, c3_config, step=step)
for step in range(step + 1, step + 21):
    bathymetry_n = bathymetry.propagate(c3_c2c3, bathymetry_n, c3_config, step=step)