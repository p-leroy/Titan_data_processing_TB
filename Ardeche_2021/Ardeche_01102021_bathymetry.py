import os

from lidar_platform import bathymetry
from lidar_platform.config.config import cc_custom, cc_std, cc_2023_01_06

idir = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\Ardeche_01102021'
# C3 input
c3_config = 'not_classified'  # values are defined in bathymetry
c3_c2c3 = os.path.join(idir, 'C3_after_corr', 'processing', 'C3_r_thin_lowest_lastOnly_1m_C2C3.bin')
# water surface
class_9 = os.path.join(idir, 'C2_after_corr', 'processing', 'water_surface',
                             'Ardeche_01102021_C2_corrected_thin_1m_surface_final.bin')


#%%
bathymetry_seed = bathymetry.extract_seed_from_water_surface(c3_c2c3, class_9, c3_config, cc_exe=cc_2023_01_06)

#%%
# Le fichier obtenu "C3_r_thin_lowest_lastOnly_1m_C2C3_bathymetry_seed.bin" a été filtré manuellement sous Cloudcompare en suivant ces étapes:
# 1. SF "C2C3_Z" --> keep only points > -20m
# 2. Compute roughness with scale 10 m
# 3. Keep only points with "roughness(10)" < 0.2
# 4. Manual filtering with the segmentation tools from two different point clouds:
#       a. SF "C2C3_Z" --> <= -2m
#       b. SF "C2C3-Z" --> > -2m
#           segmentation via connected component (octree=13=1.6m; min_points=10)
#           Manual filtering
# 5. Merge 4a. and 4b.
# 6. density (d) filter --> KNN + radius=5 -6> Keep points with d>5
# 7. Save to "C3_r_thin_lowest_lastOnly_1m_C2C3_bathymetry_seed.bin"
# the process is save to the bin file --> "G:\\RENNES1\\ThomasBernard\\StripAlign\Ardeche\\results\\Ardeche_01102021\\C3_after_corr\\processing\\bathymetry\\traitement_bathy_Ardeche01102021.bin"

#%%
bathymetry_seed = r'G:\\RENNES1\\ThomasBernard\\StripAlign\Ardeche\\results\\Ardeche_01102021\\C3_after_corr\\processing\\bathymetry\\C3_r_thin_lowest_lastOnly_1m_C2C3_bathymetry_seed_without_water_column.bin'

#%%
step = 0
bathymetry_n = bathymetry.propagate(c3_c2c3, bathymetry_seed, c3_config, step=step, cc_exe=cc_2023_01_06)
for step in range(step + 1, step + 2):
    bathymetry_n = bathymetry.propagate(c3_c2c3, bathymetry_n, c3_config, step=step, cc_exe= cc_2023_01_06)