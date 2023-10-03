import os

from lidar_platform import global_shifts, water_surface

idir = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\Ardeche_18102021'
# C2 input
c2_config = 'not_classified'  # values are defined in config_workflow
c2_root = os.path.join(idir, 'C2_after_corr', 'processing', 'C2_r_thin_lowest_lastOnly_1m')
c2_thin = c2_root + '.laz'
# C3 input
c3_config = 'not_classified'  # values are defined in config_workflow
c3_root = os.path.join(idir, 'C3_after_corr', 'processing', 'C3_r_thin_lowest_lastOnly_1m')
c3_thin = c3_root + '.laz'

#%% COMPUTE CLOUD TO CLOUD DISTANCES BETWEEN C2 AND C3
c2_c2c3 = water_surface.c2c_c2c3(c2_thin, c3_thin, c2_config, global_shift=global_shifts.Ardeche_2)
c3_c2c3 = water_surface.c2c_c2c3(c3_thin, c2_thin, c3_config, global_shift=global_shifts.Ardeche_2)

#%% EXTRACT WATER SURFACE SEED from C2
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
water_surface_n = water_surface.propagate_1deg(c2_c2c3, water_surface_seed, c2_config, deepness=0.1, step=step)
for step in range(step + 1, step + 2):
    water_surface_n = water_surface.propagate_1deg(c2_c2c3, water_surface_n, c2_config, deepness=0.1, step=step)

#%% #%% If you want to search water surface points in C3 try this
# C3 input
c3_config = 'not_classified'  # values are defined in config_workflow
c3_root = os.path.join(idir, 'C3_after_corr', 'processing', 'C3_r_thin_highest_firstOnly_1m')
c3_thin_h = c3_root + '.laz'

#%% COMPUTE CLOUD TO CLOUD DISTANCES BETWEEN C3 lowest lastonly AND C3 highest firstonly
c3_c3hc3l = water_surface.c2c_c2c3(c3_thin_h, c3_thin, c3_config, global_shift=global_shifts.Ardeche_2)

#%% EXTRACT WATER SURFACE SEED from C3 (if you want to try to extend the water surface)
# parameters are in bathymetry.py
# values of filtering are :
#cmd += f' -SET_ACTIVE_SF {bathy.i_c2c3_z + shift} -FILTER_SF 0.1 5.'
#cmd += ' -OCTREE_NORMALS 5. -MODEL LS -ORIENT PLUS_Z -NORMALS_TO_DIP'
#cmd += f' -SET_ACTIVE_SF {bathy.i_dip + shift} -FILTER_SF MIN 1.'
#cmd += ' -DENSITY 5. -TYPE KNN'
#cmd += f' -SET_ACTIVE_SF LAST -FILTER_SF 5 MAX'
water_surface_seed = water_surface.extract_seed(c3_c3hc3l, c3_config)
# + at the end --> manual filtering to remove the last isolated points out of water surface
#%%
c3_c3hc3l = c3_root + '_C3hC3l.bin'
water_surface_seed = os.path.join(idir, 'C2_after_corr', 'processing', 'water_surface',
                                  'C3_r_thin_highest_firstOnly_1m_C3hC3l_water_surface_seed.bin')

#%%
step = 0
water_surface_n = water_surface.propagate_1deg(c3_c3hc3l , water_surface_seed, c3_config, deepness=0.1, step=step)
for step in range(step + 1, step + 2):
    water_surface_n = water_surface.propagate_1deg(c3_c3hc3l, water_surface_n, c3_config, deepness=0.1, step=step)