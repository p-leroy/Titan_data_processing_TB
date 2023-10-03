import os

from lidar_platform.topo_bathymetry import build_deliverables as deliverables

workspace = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\Ardeche_01102021\05-Traitements\Raster'
#poisson_reconstruction = os.path.join(workspace, 'LAS', 'PoissonRecon', 'C2_C3_FWF_poisson_reconstruction_c.laz')
resolution = 1
root_name = "Ardeche_01102021"
tile_size = 1000
buffer = 250
keep_only_16_in_c3 = True

#%% BUILD DELIVERABLES
# available deliverables: .dtm .density .dsm .dcm
a = deliverables.Deliverable(workspace, resolution, root_name)

#%% DTM C2
a.dtm('C2', tile_size, buffer)
#a.density('C2')

#%% DTM C2_C3
a.dtm('C2_C3', tile_size, buffer,
      keep_only_16_in_c3=keep_only_16_in_c3)
#a.density('C2_C3')

#%% DTM C2_C3_FWF
a.dtm('C2_C3_FWF', tile_size, buffer,
      keep_only_16_in_c3=keep_only_16_in_c3)
a.density('C2_C3_FWF')

#%% DTM C2_C3_FWF_PoissonRecon
a.dtm('C2_C3_FWF_PoissonRecon', tile_size, buffer,
      poisson_reconstruction=poisson_reconstruction,
      keep_only_16_in_c3=keep_only_16_in_c3)
a.density('C2_C3_FWF_PoissonRecon')