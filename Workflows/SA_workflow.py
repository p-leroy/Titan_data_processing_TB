# Thomas Bernard
# 17/10/2022
"""
This workflow consists in applying StripAlign (SA) on multiple channels (C2/C3) and multiple epochs.
It take cares to first classify points in rivers of all specified flight-lines from a water_surface
point cloud to exclude these points during the registration steps.
"""

#%% Import modules
import subprocess

from scripts import classify_bathy as cb

#%% Classify point in rivers from a water_surface point cloud for all specified flight_lines
workspace = r"G:\RENNES1\ThomasBernard\StripAlign\Multi_channel_test\Data"
epoch = ["Ardeche_01102021","Ardeche_18102021"] # epoch a and b
Num_lines_a = ['16','17','18']
Num_lines_b = ['07','08','09']
Channels = ['C2','C3']
nb_lines = 3 # Number of line per channel
max_dist = 20 # Maximum distance to compute a C2C distance (allows to reduce the computation time)
reference = "Ardeche_01102021_C2_thin_1m_surface_final.laz" # the file name of the water_surface point cloud. This file has to be in the same folder than workspace.
out_dir = workspace + r"\water\classified"
# rewrite C2C scalar fields (if use '-SPLIT_XYZ' option. Used by default)
scalar_fields_old = ['C2C absolute distances[<20] (X)','C2C absolute distances[<20] (Y)','C2C absolute distances[<20] (Z)']
scalar_fields_new = ['C2C (X)','C2C (Y)','C2C (Z)']
global_shift = global_shifts.Ardeche
# for os
path_output = 'G:/RENNES1/ThomasBernard/StripAlign/Multi_channel_test/Data/'

cb.classify_bathy(workspace,epoch,Num_lines_a,Num_lines_b,Channels,nb_lines,max_dist,reference,out_dir,scalar_fields_old,scalar_fields_new,global_shift_path_output)

#%% Run StripAlign
Strip_path = 'G:/RENNES1/ThomasBernard/StripAlign/Multi_channel_test/'
batch_file = 'Multi_channel_process.bat'
subprocess.call([Strip_path+batch_file])