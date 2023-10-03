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
from lidar_platform import misc,cc
from lidar_platform.config.config import cc_custom, cc_std, cc_std_alt
from scripts import classify_bathy as cb

# parameters
bin_lastools = r'C:\opt\LAStools\bin'
cc_2023_01_06 = r'G:\RENNES1\PaulLeroy\CloudCompare_2023_01_06\CloudCompare.exe'

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
#%% Build water surface from corrected data
# 1. Preprocessing : Thin C2 and C2 with the lowest points
#  Use the C2_thin_water_surface_preprocessing.py and C3_thin_water_surface_preprocessing.py script
# 2. Construct water surface seed and propate the water surface
# Use the Ardeche_01102021_water_surface.py script
# 3. Automatic filtering of water surface with gradient z > 0.1 removed (with cloudcompare)
# do 1., 2., 3. for Ardeche_18102021 (in 2. use the Ardeche_18102021_water_surface.py script)

#%% 6a. Correction refraction C3

#%%6b1. Correction refraction C3_fwf
# ATTENTION dans le script "Ardeche_FWF_refraction_correction_check.py", la fonction "refraction_correction.do_work" ne fonctionne
# pour certaines lignes pour une raison inconnue. Ci-après est une solution de contournement pour que cela fonctionne à
# à appliquer avant d'utiliser le script  "Ardeche_FWF_refraction_correction_check.py".
# Cette solution a été appliquée à toutes les lignes sauf: Ardeche_01102021_L001_C3_r_w ; Ardeche_01102021_L002_C3_r_w ;
# Ardeche_01102021_L003_C3_r_w ; Ardeche_01102021_L004_C3_r_w_2 ; Ardeche_01102021_L008_C3_r_w_2
# Ardeche_01102021_L009_C3_r_w_2 ; Ardeche_01102021_L011_C3_r_w_5 ; Ardeche_01102021_L012_C3_r_w ; Ardeche_01102021_L013_C3_r_w_5 ;
# Ardeche_01102021_L014_C3_r_w_5 ; Ardeche_01102021_L015_C3_r_w ; Ardeche_01102021_L016_C3_r_w_6 ; Ardeche_01102021_L017_C3_r_w_6 ;
# Ardeche_01102021_L018_C3_r_w_6 ; Ardeche_01102021_L019_C3_r_w_6;  Ardeche_01102021_L021_C3_r_w_5; Ardeche_01102021_L022_C3_r_w_5;
# Ardeche_01102021_L023_C3_r_w_5
workspace = r"G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results"
epochs = ["Ardeche_01102021"] # epoch a and b
Channels = [r'C3_fwf_after_corr\correction_refraction\with_depth\to_split']
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

#%% Merge splitted files "*_ref_corr.laz" (for FWF)
workspace = r"G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results"
epoch = "Ardeche_01102021" # epoch a and b
Channel = r'C3_fwf_after_corr\correction_refraction\with_depth\to_split'
path= os.path.join(workspace,epoch,Channel)
path_ref_corr = os.path.join(path,'done') # path of "_ref_corr.laz" files
Splitted_files_list = glob.glob(os.path.join(path,'*.laz'))

for file in Splitted_files_list:
    filename = os.path.basename(file).split(".")[0]
    ref_corr_basename = f'{filename}_*_ref_corr'
    ref_corr_files = glob.glob(os.path.join(path_ref_corr,f'{ref_corr_basename}.laz'))
    print(ref_corr_files)
    cc.merge(ref_corr_files,fmt='LAZ',silent=True,debug=True,global_shift=global_shifts.Ardeche_2,cc=cc_2023_01_06 )
    #Clean
    for file_ref in ref_corr_files:
        os.remove(file_ref)
    os.rename(os.path.join(path_ref_corr,f'{filename}_00_ref_corr_MERGED.laz'),os.path.join(path_ref_corr,f'{filename}_ref_corr.laz'))

# move "_ref_corr.laz" files to the "with_depth" directory
source_dir = path_ref_corr
dest_dir= os.path.join(workspace,epoch,'C3_fwf_after_corr\correction_refraction\with_depth\done')
source_files = glob.glob(os.path.join(source_dir,'*ref_corr.laz'))
for file in source_files:
    shutil.move(file, dest_dir)
# Attention après le merge le champ scalaire "Edge of flight line" disparait (sur cloudcompare).


#%% 4.4.1. Keep only points with depth refraction corrected from FWF data
# a. drop noisy and water surface points
workspace = r"G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results"
epoch = "Ardeche_01102021" # epoch a and b
Channel = r'C3_fwf_after_corr\correction_refraction'
epsg=2154
files = glob.glob(os.path.join(workspace,epoch,Channel, '*.laz'))
# create bathy directory
dir_bathy = os.path.join(workspace,epoch,Channel,'bathy')
os.makedirs(dir_bathy,exist_ok=True)

for file in files:
    cmd = os.path.join(bin_lastools, 'las2las')
    args = f' -i {file} -odir {dir_bathy} -olaz'
    args += (f' -drop_class 7 ') # drop noise and water
    args += f' -epsg {epsg} -meter -elevation_meter'
    misc.run(cmd + args)


#%% select bathy points
workspace = r"G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results"
epochs = ["Ardeche_01102021"] # epoch a and b
Channels = [r'C3_fwf_after_corr\correction_refraction\bathy']
epsg=2154
minvalue, maxvalue = -20, 'MAX' # -20 to exclude possible remaining noisy points with large negative z value. For C3 maxvalue=0
global_shift = global_shifts.Ardeche_2
sf_name = 'depth'

# Split .laz files
for epoch in epochs:
    for channel in Channels:
        path = os.path.join(workspace,os.path.join(epoch,channel))
        filenames = glob.glob(os.path.join(path, '*.laz'))
        for filename in filenames:
            cc.filter_ptcloud(filename,sf_name,minvalue,maxvalue,fmt='LAZ',global_shift=global_shift,silent=True, debug=True, cc=cc_2023_01_06)


#%% Merge files
for epoch in epochs:
    for channel in Channels:
        path = os.path.join(workspace,os.path.join(epoch,channel))
        filenames = '*].laz'
        files = glob.glob(os.path.join(path, filenames))
        cc.merge(files, fmt='LAZ', silent=True, debug=True, global_shift=global_shifts.Ardeche_2,
                 cc=cc_2023_01_06)
        # Clean
        for file in files:
            os.remove(file)
        os.rename(os.path.join(path, 'Ardeche_01102021_L001_C3_r_w_ref_corr_FILTERED_[-20_-0.07]_MERGED.laz'),
                  os.path.join(path, 'Ardeche_01102021_C3_r_w_ref_corr_bathy.laz'))


#%% filter bathy
cloud =os.path.join(path,'Ardeche_01102021_C3_r_w_ref_corr_bathy.laz')
filter_density = 200
head, tail = os.path.split(cloud)
head, tail, root, ext = misc.head_tail_root_ext(cloud)
odir = os.path.join(head, 'filtered')
os.makedirs(odir, exist_ok=True)
out = os.path.join(odir, root + f'_filtered_{filter_density}.laz')

cmd = cc_2023_01_06
cmd += ' -SILENT -NO_TIMESTAMP -C_EXPORT_FMT LAS -EXT LAZ -AUTO_SAVE OFF'
cmd += f' -O -GLOBAL_SHIFT AUTO {cloud}'
cmd += ' -DENSITY 5. -TYPE KNN'
cmd += f' -SET_ACTIVE_SF LAST -FILTER_SF {filter_density} MAX'
cmd += f' -SAVE_CLOUDS FILE {out}'
misc.run(cmd)

#%%Apply Poisson reconstruction
# split merged file
workspace = r"G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results"
epoch = "Ardeche_01102021" # epoch a and b
Channel = r'C3_fwf_after_corr\correction_refraction\bathy\filtered\first_C2M'
epsg=2154
file = os.path.join(workspace,epoch,Channel,'first_C2M.laz' )#'Ardeche_01102021_C3_r_w_ref_corr_bathy_filtered_200.laz'

cmd = os.path.join(bin_lastools, 'lassplit')
args = f' -i {file} -split 10000 -digits 2 -olaz'
args += f' -epsg {epsg} -meter -elevation_meter'
misc.run(cmd + args)

#%% Apply thin
workspace = r"G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results"
epoch = "Ardeche_01102021" # epoch a and b
Channel = r'C3_fwf_after_corr\correction_refraction\bathy\filtered\first_C2M'
files = glob.glob(os.path.join(workspace,epoch,Channel, '*M_*.laz'))#f'*_{filter_density}_*.laz'
for file in files:
    cmd = os.path.join(bin_lastools, 'lasthin')
    args = f' -i {file} -odix _thin -olaz'
    args += (f' -step 1 ')
    args += (f' -percentile 10 ')
    args += f' -epsg {epsg} -meter -elevation_meter'
    misc.run(cmd + args)

#%% merge and clean
files = glob.glob(os.path.join(workspace,epoch,Channel, f'*_thin.laz'))
cc.merge(files, fmt='LAZ', silent=True, debug=True, global_shift=global_shifts.Ardeche_2,cc=cc_2023_01_06)
# Clean
for file in files:
    os.remove(file)
merge_file = f'{os.path.basename(files[0]).split(".")[0]}_MERGED.laz'
path=os.path.join(workspace,epoch,Channel)
os.rename(os.path.join(path, merge_file),os.path.join(path, 'Ardeche_01102021_C3_r_w_ref_corr_bathy_filtered_200_thin.laz'))
