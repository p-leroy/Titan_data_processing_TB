import glob
import os

from lidar_platform.topo_bathymetry import poisson_reconstruction as poisson
from lidar_platform import misc

workspace = r'G:\RENNES1\PaulLeroy\Brioude_30092021\05-Traitements\Raster\MNT_C2_C3_FWF_1m'
tiles = glob.glob(os.path.join(workspace, "Brioude_2021_MNT_*00.laz"))
list_of_names = [os.path.split(file)[1] for file in tiles]
water_surface = r'G:\RENNES1\PaulLeroy\Brioude_30092021\06-Livrables\Other\class_9_water_surface_1m.laz'

bbox_place = 3  # start at 0, separator="_"
tile_size = 1000
dist_buffer = 250

params_cc = ['standard', 'LAS', 'Brioude']

params_normal = {"shiftname": "Brioude",
                 "normal_radius": "2",
                 "model": "QUADRIC"}

params_recon = {"bType": "Neumann",
                "degree": "1",  # B-spline degree. The default value is 1 instead of 2 as written in the documentation
                "width": "4",
                "samplesPerNode": "15",  # Noise-free samples [1.0 - 5.0], more noisy samples [15.0 - 20.0]
                "pointWeight": "4",  # The default value for this parameter is twice the B-spline degree.
                "density": "",
                "performance": "",
                "verbose": ""}

#%% the parallel processing with joblib is not stable (worse being retested later)
for tile in tiles:
    poisson.poisson_recon(tile, water_surface, bbox_place, tile_size,
                          params_recon, params_cc, params_normal,
                          z_ws_min=-10, z_ws_max=0, d_ws_max=200,
                          d_orig_min=0.5, d_orig_max=100,
                          )

#%% Merge interpolation files
poissonRecon_d = os.path.join(workspace, 'PoissonRecon')
misc.run(
    "lasmerge -i " + os.path.join(poissonRecon_d, "*_sample_mesh_select*.laz") +
    f" -odir {poissonRecon_d} -o poisson_reconstruction.laz")