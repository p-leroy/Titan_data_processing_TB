import os

from lidar_platform import global_shifts, water_surface
from lidar_platform.config.config import cc_custom, cc_2023_01_06
idir = r'G:\RENNES1\ThomasBernard\StripAlign\Herault\results\Herault_30092021'
# C2 input
c2_config = 'classified' # values are defined in bathymetry.py
c2_root = os.path.join(idir, 'C2_after_corr', 'processing', 'C2_r_thin_lowest_lastOnly_1m')
c2_thin = c2_root + '.laz'
# C3 input
c3_config = 'not_classified'  # values are defined in bathymetry.py
c3_root = os.path.join(idir, 'C3_after_corr', 'processing', 'C3_r_thin_lowest_lastOnly_1m')
c3_thin = c3_root + '.laz'

#%% COMPUTE CLOUD TO CLOUD DISTANCES BETWEEN C2 AND C3
c2_c2c3 = water_surface.c2c_c2c3(c2_thin, c3_thin, c2_config, global_shift=global_shifts.Herault)
c3_c2c3 = water_surface.c2c_c2c3(c3_thin, c2_thin, c3_config, global_shift=global_shifts.Herault)

#%% EXTRACT WATER SURFACE SEED
# parameters are in bathymetry.py
# values of filtering are :
#cmd += f' -SET_ACTIVE_SF {bathy.i_c2c3_z + shift} -FILTER_SF 0.1 5.'
#cmd += ' -OCTREE_NORMALS 5. -MODEL LS -ORIENT PLUS_Z -NORMALS_TO_DIP'
#cmd += f' -SET_ACTIVE_SF {bathy.i_dip + shift} -FILTER_SF MIN 1.'
#cmd += ' -DENSITY 5. -TYPE KNN'
#cmd += f' -SET_ACTIVE_SF LAST -FILTER_SF 5 MAX'
water_surface_seed = water_surface.extract_seed(c2_c2c3, c2_config)

# + at the end --> manual filtering to remove the last isolated points out of water surface

#%%
c2_c2c3 = c2_root + '_C2C3.bin'
c3_c2c3 = c3_root + '_C2C3.bin'
water_surface_seed = os.path.join(idir, 'C2_after_corr', 'processing', 'water_surface',
                                  'C2_r_thin_lowest_lastOnly_1m_C2C3_water_surface_seed.bin')

#%%
step = 0
water_surface_n = water_surface.propagate_1deg(c2_c2c3, water_surface_seed, c2_config, deepness=0.05, step=step,cc_exe=cc_2023_01_06)
for step in range(step + 1, step + 2):
    water_surface_n = water_surface.propagate_1deg(c2_c2c3, water_surface_n, c2_config, deepness=0.05, step=step,cc_exe=cc_2023_01_06)