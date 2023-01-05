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
                                                   /C3_fwf
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
import glob
import os
import shutil

from lidar_platform.config import global_shifts
from lidar_platform import misc
from scripts import classify_bathy as cb

# parameters
bin_lastools = 'C:/opt/LAStools/bin'

#%% 1. Optional preprocessing (if full-waveform) : classify the noise in a sf with value=7
FWF = True
path_fwf = 'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\Data\Ardeche_01102021\C3_fwf'
if FWF is True:
    filenames = glob.glob(os.path.join(path_fwf, '*.laz'))
    epsg=2154
    for filename in filenames:
        cmd = os.path.join(bin_lastools, 'lasnoise')
        args = f' -i {filename} -odix _class -olaz'
        args += (' -step 2') # drop noise and water
        args += (' -isolated 250')
        args += f' -epsg {epsg} -meter -elevation_meter'
        misc.run(cmd + args)

        #clean
        infile = os.path.splitext(filename)[0]
        if os.path.exists(infile + '_class.laz'):
            os.remove(filename)
            os.rename(infile+'_class.laz', infile + '.laz')

#%% 2. Preprocessing: classify point in rivers from a water_surface point cloud for all specified flight_lines
workspace = r"G:\RENNES1\ThomasBernard\StripAlign\Ardeche\Data"
epoch = ["Ardeche_18102021"] # epoch a and b
Channels = ['C2','C3']
max_dist = 20 # Maximum distance to compute a C2C distance (allows to reduce the computation time)
reference = "Ardeche_01102021_C2_thin_1m_surface_final.laz" # the file name of the water_surface point cloud. This file has to be in the same folder than workspace.
out_dir = workspace + r"\water\classified"
global_shift = global_shifts.Ardeche

cb.classify_bathy(workspace, epoch, Channels, max_dist, reference, out_dir, global_shift)

#%% 2bis. Preprocessing: classify points with scan angle rank of -12 and 12 as 7 (considered as noise)
workspace = r"G:\RENNES1\ThomasBernard\StripAlign\Ardeche\Data"
epochs = ["Ardeche_01102021","Ardeche_18102021"] # epoch a and b
Channels = ['C2','C3','C3_fwf']
epsg=2154
for epoch in epochs:
    for channel in Channels:
        path = os.path.join(workspace,os.path.join(epoch,channel))
        filenames = glob.glob(os.path.join(path, '*.laz'))
        for filename in filenames:
            cmd = os.path.join(bin_lastools, 'las2las')
            args = f' -i {filename} -odix _class -olaz'
            args += (f' -drop_abs_scan_angle_below 12')
            args += (f' -filtered_transform')
            args += (f' -set_classification 7')
            args += f' -epsg {epsg} -meter -elevation_meter'
            misc.run(cmd + args)

            #clean
            infile = os.path.splitext(filename)[0]
            if os.path.exists(infile + '_class.laz'):
                os.remove(filename)
                os.rename(infile+'_class.laz', infile + '.laz')

#%% 3. Run StripAlign for C2 C3
# First apply correction to both Ardeche_01102021 and Ardeche_18102021 (C2/C3) all together
Strip_path = 'G:/RENNES1/ThomasBernard/StripAlign/Ardeche/'
batch_file = 'run_SA.bat'
subprocess.call(["start",Strip_path+batch_file],shell=True)

#%% Clean and move results files
path_res = r"G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results"
corr_path = os.path.join(path_res,'corr')
corr_fwf_path = os.path.join(path_res,'corr_fwf')
for name in epoch:
    for Channel in Channels:
        laz_dir = os.path.join(path_res, os.path.join(name, f'{Channel}_after_corr'))
        p2p_dir = os.path.join(laz_dir,'p2p')
        os.makedirs(laz_dir, exist_ok=True)
        os.makedirs(p2p_dir, exist_ok=True)

        if Channel=='C3_fwf':
            p2p_files = glob.glob(corr_fwf_path + f'{name}_*_C3_*_p2p_corr.laz')
            res_files = glob.glob(corr_fwf_path + f'{name}_*_C3_r_1.laz')
        else:
            p2p_files = glob.glob(corr_path + f'{name}_*_{Channel}_*_p2p_corr.laz')
            res_files = glob.glob(corr_path + f'{name}_*_{Channel}_r_1.laz')

        for file in res_files:
            shutil.move(file, laz_dir)
        for file in p2p_files:
            shutil.move(file, p2p_dir)

    if Channel != 'C3_fwf':
        C2C3_dir = os.path.join(path_res, os.path.join(name, f'C2C3_after_corr'))
        os.makedirs(C2C3_dir, exist_ok=True)
        file_list = glob.glob(os.path.join(laz_dir, '*.laz'))
        for file in file_list:
            filename = os.path.basename(file)
            shutil.copyfile(file, os.path.join(C2C3_dir,filename))

#%% 4. Run StripAlign for C3_fwf
# Second apply correction to Ardeche_01102021 C3_FWF with C3 as reference
batch_file = 'run_SA_C3_C3fwf.bat'
subprocess.call(["start",Strip_path+batch_file],shell=True)






#%% 4. Quality check (QC) after correction
# Use the QC_recouvrement.py script and QC_inter_survey_C2C3.py