#%% Import modules
import subprocess
import glob
import os

from lidar_platform import cc, las
from lidar_platform import misc
from lidar_platform.config.config import cc_custom, cc_2_13_FWF , cc_2022_12_08
from lidar_platform.config import global_shifts

# parameters
bin_lastools = r'C:\opt\LAStools\bin'

#%% Script

workspace = r"G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results"
epochs = ["Ardeche_18102021"] # epoch a and b
Channels = [r'C3_after_corr\correction_refraction\with_depth']
epsg=2154
minvalue, maxvalue = 'MIN', 0
global_shift = global_shifts.Ardeche_2
sf_name = 'depth'
# Split .laz files
for epoch in epochs:
    for channel in Channels:
        path = os.path.join(workspace,os.path.join(epoch,channel))
        filenames = glob.glob(os.path.join(path, '*.laz'))
        for filename in filenames:
            cc.filter_ptcloud(filename,sf_name,minvalue,maxvalue,fmt='LAZ',global_shift=global_shift,silent=True, debug=True, cc=cc_2_13_FWF)

#%% Merge files
for epoch in epochs:
    for channel in Channels:
        path = os.path.join(workspace,os.path.join(epoch,channel))
        filenames = '*].laz'
        cmd = os.path.join(bin_lastools, 'lasmerge')
        files= os.path.join(path,filenames)
        args = f' -i {files} -o {path}\depth_merge.laz'
        #args += f' -epsg {epsg} -meter -elevation_meter'
        misc.run(cmd + args)



