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
#%% 1. Manual filtering of noise --> explained in the README file and below
"""
1. Traitement manuel pour supprimer des points outliers (au niveau de l'avion) sur C2 et C3.
Effectué sur:
C2	C3
/	L01
/	L02	
L03	L03
/	L04
/	L05
/	L06
/	L07
/	/
/	L09
/	L10
/	L11
/	L12
/	L13
/	L14
/	L15
/	L16
L18	L18
/	L19
L20	L20
/	L21
L22	L22
/	L23
/	L24
/	L25
L26	L26
/	L27
/	L28
/	L29
/	L30
/	L31
/	L32
/	L33
/	L34	

2. Filtrage sur la ligne 18 C2 et C3 car problème de GPS time induisant des erreurs résiduelles lors de l'assemblage avec Stripalign.
 --> Les points avec un GPSTime compris entre 78.2 et 82.5 ont été supprimés pour le C3
 --> Les points avec un GPSTime compris entre 490.3 et 493.1 ont été supprimés pour le C3
"""

#%% Import modules
import subprocess
import glob
import os
import shutil

import numpy as np

from lidar_platform.config import global_shifts
from lidar_platform import misc, cc, las
from scripts import classify_bathy as cb

# parameters
bin_lastools = 'C:/opt/LAStools/bin'

#%% 2. Optional preprocessing (only if full-waveform data) : classify the noise in a sf with value=7
FWF = False
path_fwf = 'G:\RENNES1\ThomasBernard\StripAlign\Herault\Data\Herault_30092021\C3_fwf'
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

#%% 3. Preprocessing: classify point in rivers from a water_surface point cloud for all specified flight_lines
workspace = r"G:\RENNES1\ThomasBernard\StripAlign\Herault\Data"
epoch = ["Herault_30092021"] # epoch a and b
Channels = ['C2','C3']
max_dist = 20 # Maximum distance to compute a C2C distance (allows to reduce the computation time)
reference = "C2_ground_thin_1m_surface_final.laz" # the file name of the water_surface point cloud. This file has to be in the same folder than workspace.
out_dir = workspace + r"\water\classified"
global_shift = global_shifts.Herault

cb.classify_bathy(workspace, epoch, Channels, max_dist, reference, out_dir, global_shift)

#%% 4. Preprocessing: classify with the largest absolute scan angle as 7 (considered as noise)
# Here I chose to find the maximum value of the scan angle first since it is different between flight lines.
#cc.to_sbf

workspace = r"G:\RENNES1\ThomasBernard\StripAlign\Herault\Data"
epochs = ["Herault_30092021"] # epoch a and b
Channels = ['C2',"C3"]
global_shift = global_shifts.Herault
for epoch in epochs:
    for channel in Channels:
        path = os.path.join(workspace,os.path.join(epoch,channel))
        filenames = glob.glob(os.path.join(path, '*.laz'))
        for filename in filenames:
            laz = las.read(filename)
            scan_angle = laz['scan_angle_rank']
            max_value = np.max(np.abs(scan_angle))
            mask = np.abs(scan_angle)>max_value-1
            laz['classification'][mask==True] = 7
            las.WriteLAS(filename, laz)


#%% 5. Run StripAlign for C2 C3
Strip_path = 'G:/RENNES1/ThomasBernard/StripAlign/Herault/'
batch_file = 'run_SA.bat'
subprocess.call(["start",Strip_path+batch_file],shell=True)

#%% 6. Clean and move results files
path_res = r"G:\RENNES1\ThomasBernard\StripAlign\Herault\results"
corr_path = os.path.join(path_res,'corr')
epochs = ["Herault_30092021"] # epoch a and b
Channels = ['C2','C3']
for name in epochs:
    for Channel in Channels:
        laz_dir = os.path.join(path_res, os.path.join(name, f'{Channel}_after_corr'))
        p2p_dir = os.path.join(laz_dir,'p2p')
        os.makedirs(laz_dir, exist_ok=True)
        os.makedirs(p2p_dir, exist_ok=True)

        p2p_files = glob.glob(os.path.join(corr_path, f'*{Channel}*_p2p_corr.laz'))
        res_files = glob.glob(os.path.join(corr_path, f'*{Channel}_r_1.laz'))

        for file in p2p_files:
            shutil.move(file, p2p_dir)

        for file in res_files:
            shutil.move(file, laz_dir)


#%% 7. Run StripAlign for C3_fwf
#batch_file = 'run_SA_C3_C3fwf.bat'
#subprocess.call(["start",Strip_path+batch_file],shell=True)


#%% 4. Quality check (QC) after correction
# Use the QC_recouvrement.py script and QC_inter_survey_C2C3.py