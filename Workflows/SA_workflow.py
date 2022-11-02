# Thomas Bernard
# 17/10/2022
"""
This workflow consists in applying StripAlign (SA) on multiple channels (C2/C3) and multiple epochs.
It take cares to first classify points in rivers of all specified flight-lines from a water_surface
point cloud to exclude these points during the registration steps. Two quality check are performed:
one before and one after the correction.
What you need:
- lidar flight lines to register (.laz)
- SBET trajectory file (.out)
- A surface water point cloud (.laz)
- A .bat file with the command line code for StripAlign (and an additional .asc file optionnaly for constant parameters)
- A "/temp" folder to stock temporary files of StripAlign
- A proj.txt file that describe the projection used for flight lines (WKT file)

Suggested file organization:

Project_directory > /Data    > /Epoch_1          > /C2
                                                   /C3
                               /Epoch_2          > /C2
                                                   /C3
                               water_surface.laz
                               proj.txt
                    /results  > /reg : results of the registration step (StripAlign)
                                /corr : results of the correction step (StripAlign)
                                /04-QC           > /Overlap                > /C2              # Quality check (QC) results (before and after correction)
                                                                           > /C3
                                                                           > /C2C3
                                                                           > /C2_after_corr
                                                                           > /C3_after_corr
                                                                           > /C2C3_after_corr
                    /temp
                    run_SA.bat
                    stripalign.opt.asc
"""
#%% 1. Quality check (QC) before correction
# Use the QC_recouvrement.py script

#%% Import modules
import subprocess

from lidar_platform.config import global_shifts
from scripts import classify_bathy as cb


#%% 2. Classify point in rivers from a water_surface point cloud for all specified flight_lines
workspace = r"G:\RENNES1\ThomasBernard\StripAlign\Herault\Data"
epoch = ["Herault_30092021"] # epoch a and b
Num_lines_a = ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','34']
Num_lines_b = ['07','08','09']
Channels = ['C3']
max_dist = 20 # Maximum distance to compute a C2C distance (allows to reduce the computation time)
reference = "C2_ground_thin_1m_surface_final.laz" # the file name of the water_surface point cloud. This file has to be in the same folder than workspace.
out_dir = workspace + r"\water\classified"
global_shift = global_shifts.Herault
# for os (same as workspace)
path_output = 'G:/RENNES1/ThomasBernard/StripAlign/Herault/Data/'

cb.classify_bathy(workspace,epoch,Num_lines_a,Num_lines_b,Channels,max_dist,reference,out_dir,global_shift,path_output)


#%% 3. Run StripAlign
Strip_path = 'G:/RENNES1/ThomasBernard/StripAlign/Herault/'
batch_file = 'Multi_channel_process.bat'
subprocess.call(["start",Strip_path+batch_file],shell=True)

#%% 4. Quality check (QC) after correction
# Use the QC_recouvrement.py script