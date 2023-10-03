import os
import glob

from lidar_platform import bathymetry as bathy
from lidar_platform.topo_bathymetry import refraction_correction
from lidar_platform import cc, global_shifts
from lidar_platform.config.config import cc_2022_12_08

idir = r'G:\RENNES1\ThomasBernard\StripAlign\Archives\Ardeche\Data\Ardeche_01102021\C3_fwf\correction_refraction\tmp\fail'

water_surface = r'G:\RENNES1\ThomasBernard\StripAlign\Archives\Ardeche\Data\Ardeche_01102021_C2_thin_1m_surface_final.laz'
sbet = r'G:\RENNES1\ThomasBernard\StripAlign\Archives\Ardeche\Data\Ardeche_01102021\params_sbet_Ardeche_01102021.txt'
global_shift = global_shifts.Ardeche
filenames = glob.glob(os.path.join(idir, '*.laz'))
FWF = True


#%% Script
for line in filenames:
    if FWF == True:
        print('Process full-waveform...')
        # add depth for FWF (Work only with .laz file and with the Cloudcompare version 2022_12_08)
        out = bathy.add_depth_FWF(line, water_surface, global_shift, silent=True)
        # correction of the refraction
        #refraction_correction.do_work([out], sbet, 10, point_format=4, fwf=False)
        # clean

    else:
        # add depth
        out = bathy.add_depth(line, water_surface, global_shift, silent=True, cc_exe = cc_2022_12_08)
        # convert to laz
        laz = cc.to_laz(out,silent=False,cc_exe=cc_2022_12_08)
        # correction of the refraction
        refraction_correction.do_work([laz], sbet, 10, fwf=False)
        # clean








