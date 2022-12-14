# This script aims to interpole scalar fields with cloudcompare
import glob
import os

from lidar_platform.tools import cc, misc
from lidar_platform.config import global_shifts
from lidar_platform.config.config import cc_custom, cc_std, cc_std_alt, cc_2022_12_08, cc_2_13_FWF



def interp_SF(source, destination, sf_index, export_fmt= 'LAZ', global_shift=None, silent=True, debug=False):
    args = ''
    if silent is True:
        args += ' -SILENT -NO_TIMESTAMP'
    else:
        args += ' -NO_TIMESTAMP'

    args += f' -C_EXPORT_FMT {export_fmt}'

    if global_shift is not None:
        x, y, z = global_shift
        args += f' -o -GLOBAL_SHIFT {x} {y} {z} {source}'
        args += f' -o -GLOBAL_SHIFT {x} {y} {z} {destination}'
    else:
        args += f' -o {source}'
        args += f' -o {destination}'

    args += f' -SF_INTERP {sf_index}'

    args += ' -SAVE_CLOUDS'

    misc.run(cc_2022_12_08 + args, verbose=debug)

#%% Script

source_dir =  r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\Data\Ardeche_01102021\C3_fwf' # dossier des fichiers sources (contenant le SF à interpoler)
dest_dir =  r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\Data\Ardeche_01102021\C3_fwf\origin' # dossier des fichiers de destination
sf_index = 5
global_shift = global_shifts.Ardeche
source_files= glob.glob(os.path.join(source_dir,'*.laz'))
dest_files= glob.glob(os.path.join(dest_dir,'*.laz'))

for file in source_files:
    filename = os.path.basename(file)
    source = os.path.join(source_dir,filename)
    print(source)
    destination = os.path.join(dest_dir,filename) # source and dest files have the same name
    print(destination)
    interp_SF(source, destination, sf_index, export_fmt= 'LAZ', global_shift=global_shift, silent=True, debug=True)

