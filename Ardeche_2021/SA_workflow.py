# Thomas Bernard
# 17/10/2022

"""
This workflow consists in applying StripAlign (SA) on multiple channels (C2/C3) and multiple epochs.
It take cares to first classify points in rivers (step 2) of all specified flight-lines from a water_surface
point cloud to exclude these points during the registration steps.
It is also possible to classify noisy points for FWF data using lastools (step 1).
In step 2bis you can classify points below a specified scan_angle absolute value.
Two quality check are performed: one before and one after the correction.
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
                                                                           > QC_inter_survey
                    /temp
                    run_SA.bat
                    stripalign.opt.asc
"""

#%% Import modules
import subprocess
import glob
import os
import shutil

from lidar_platform.config import global_shifts
from lidar_platform import misc
from scripts import classify_bathy as cb

# parameters
bin_lastools = r'C:\opt\LAStools\bin'

####### Preprocessing ##############
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
Channels = ['test']
max_dist = 20 # Maximum distance to compute a C2C distance (allows to reduce the computation time)
reference = "Ardeche_01102021_C2_thin_1m_surface_final.laz" # the file name of the water_surface point cloud. This file has to be in the same folder than workspace.
out_dir = workspace + r"\water\classified"
global_shift = global_shifts.Ardeche

cb.classify_bathy(workspace, epoch, Channels, max_dist, reference, out_dir, global_shift)

#%% 3. Preprocessing: classify points with scan angle rank of -12 and 12 as 7 (considered as noise)
workspace = r"G:\RENNES1\ThomasBernard\StripAlign\Ardeche\Data"
epochs = ["Ardeche_18102021"] # epoch a and b
Channels = ['test']
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


#%%####### Run Strip Align - BayesMap ##############
# 4. Run StripAlign for C2 C3
# First apply correction to both Ardeche_01102021 and Ardeche_18102021 (C2/C3) all together
Strip_path = 'G:/RENNES1/ThomasBernard/StripAlign/Ardeche/'
batch_file = 'run_SA.bat'
subprocess.call(["start",Strip_path+batch_file],shell=True)

#%% 4b. Clean and move results files
path_res = r"G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results"
corr_path = os.path.join(path_res,'corr')
epochs = ["Ardeche_01102021","Ardeche_18102021"] # epoch a and b
Channels = ['C2','C3']
for name in epochs:
    for Channel in Channels:
        laz_dir = os.path.join(path_res, os.path.join(name, f'{Channel}_after_corr'))
        p2p_dir = os.path.join(laz_dir,'p2p')
        os.makedirs(laz_dir, exist_ok=True)
        os.makedirs(p2p_dir, exist_ok=True)

        p2p_files = glob.glob(os.path.join(corr_path, f'{name}*{Channel}*_p2p_corr.laz'))
        res_files = glob.glob(os.path.join(corr_path, f'{name}*{Channel}_r_1.laz'))

        for file in p2p_files:
            shutil.move(file, p2p_dir)
        for file in res_files:
            shutil.move(file, laz_dir)


#%% 4c. Run StripAlign for C3_fwf
# Second apply correction to Ardeche_01102021 C3_FWF with C3 as reference
Strip_path = 'G:/RENNES1/ThomasBernard/StripAlign/Ardeche/'
batch_file = 'run_SA_C3_C3fwf.bat'
subprocess.call(["start",Strip_path+batch_file],shell=True)

#%% 4d. Clean and move results files for FWF
path_res = r"G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results"
corr_fwf_path = os.path.join(path_res,'corr_fwf')
epochs = ["Ardeche_01102021"] # epoch a and b
Channels = ['C3_fwf']
for name in epochs:
    for Channel in Channels:
        laz_dir = os.path.join(path_res, os.path.join(name, f'{Channel}_after_corr'))
        p2p_dir = os.path.join(laz_dir,'p2p')
        os.makedirs(laz_dir, exist_ok=True)
        os.makedirs(p2p_dir, exist_ok=True)

        p2p_files = glob.glob(os.path.join(corr_fwf_path, f'*_p2p_corr.laz'))
        for file in p2p_files:
            shutil.move(file, p2p_dir)

        res_files = glob.glob(os.path.join(corr_fwf_path, f'*.laz'))
        for file in res_files:
            shutil.move(file, laz_dir)


#%%####### Quality checks ##############
# 5. Quality check intra et inter-survey (QC)
# Use the QC_recouvrement.py script and QC_inter_survey_C2C3.py

#%%####### Bathymetry ##############
# 6a. Correction refraction C3

#%%####### Bathymetry ##############
# 6b1. Correction refraction C3_fwf
# ATTENTION dans le script "Ardeche_FWF_refraction_correction_check.py", la fonction "refraction_correction.do_work" ne fonctionne
# pour certaines lignes pour une raison inconnue. Ci-après est une solution de contournement pour que cela fonctionne à
# à appliquer avant d'utiliser le script  "Ardeche_FWF_refraction_correction_check.py".
# Cette solution a été appliquée aux lignes: Ardeche_01102021_L004_C3_r_w_1 ;
workspace = r"G:\RENNES1\ThomasBernard\StripAlign\Archives\Ardeche\Data"
epochs = ["Ardeche_01102021"] # epoch a and b
Channels = [r'C3_fwf\correction_refraction\tmp']
epsg=2154
for epoch in epochs:
    for channel in Channels:
        path = os.path.join(workspace,os.path.join(epoch,channel))
        filenames = glob.glob(os.path.join(path, '*.laz'))
        for filename in filenames:
            cmd = os.path.join(bin_lastools, 'lassplit')
            args = f' -i {filename} -split 10000000 -digits 2 -olaz'
            args += f' -epsg {epsg} -meter -elevation_meter'
            misc.run(cmd + args)

            #clean
            infile = os.path.splitext(filename)[0]
            if os.path.exists(infile+ '.laz'):
                os.remove(filename)


# use the "Ardeche_FWF_refraction_correction_check.py" script
# Attention! les SF "EdgeofFlightline" et "SyntheticFlag" disparaissent après utilisation fonction refraction_correction.do_work

#%%####### Bathymetry ##############
# 6b2. Optional
workspace = r"G:\RENNES1\ThomasBernard\StripAlign\Archives\Ardeche\Data"
epochs = ["Ardeche_01102021"] # epoch a and b
Channels = [r'C3_fwf\correction_refraction\tmp']
rename = 'Ardeche_01102021_L004_C3_r_w_1.laz' #file nmae after merged.
epsg=2154
for epoch in epochs:
    for channel in Channels:
        path = os.path.join(workspace,os.path.join(epoch,channel))
        files = glob.glob(os.path.join(os.path.join(path,'with_depth'), '*_ref_corr.laz'))
        # move _ref_corr.laz files to be merged
        merge_dir = 'merge'
        path_merge = os.path.join(os.path.join(path,'with_depth'),merge_dir)
        os.makedirs(path_merge, exist_ok=True)
        for file in files:
            shutil.move(file, path_merge)

