import os
import shutil

import laspy

from lidar_platform import cc, global_shifts, misc

# idir = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\Data\Ardeche_01102021\C3_fwf\TMP'
# water_surface = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\Data\Ardeche_01102021_C2_thin_1m_surface_final.laz'
# compared = os.path.join(idir, 'Ardeche_01102021_L001_C3_r_w.laz')
# global_shift = global_shifts.Ardeche

# this is the alpha version of CloudCompare with a modified version of the FWF plugin
cc_exe = r'C:\Program Files\CloudCompare_2.13.alpha_11_13_2022_FWF\CloudCompare.exe'
cc_qlasio = r'G:\RENNES1\PaulLeroy\CloudCompare_20221202\CloudCompare.exe'


def open_file(cmd, fullname, global_shift='AUTO', fwf=False):
    if not os.path.exists(fullname):
        raise FileNotFoundError(fullname)
    if fwf:
        cmd.append('-fwf_o')
    else:
        cmd.append('-o')
    if global_shift is not None:
        cmd.append('-GLOBAL_SHIFT')
        if global_shift == 'AUTO' or global_shift == 'FIRST':
            cmd.append(global_shift)
        elif type(global_shift) is tuple or type(global_shift) is list:
            x, y, z = global_shift
            cmd.append(str(x))
            cmd.append(str(y))
            cmd.append(str(z))
        else:
            raise ValueError('invalid value for global_shit')
    cmd.append(fullname)


def custom_c2c(compared, reference, max_dist=None, split_XYZ=False, octree_level=None, remove_C2C_SF=False, odir="",
               silent=True, debug=False, global_shift='AUTO', cc_exe=cc_qlasio):
    cmd = []
    cmd.append(cc_exe)
    if silent:
        cmd.append('-SILENT')
    cmd.append('-NO_TIMESTAMP')
    cmd.append('-C_EXPORT_FMT')
    cmd.append('LAS')
    cmd.append('-EXT')
    cmd.append('laz')

    open_file(cmd, compared, global_shift=global_shift)
    open_file(cmd, reference, global_shift=global_shift)

    cmd.append('-c2c_dist')
    if octree_level:
        cmd.append('-OCTREE_LEVEL')
        cmd.append(str(octree_level))
    if max_dist:
        cmd.append('-MAX_DIST')
        cmd.append(str(max_dist))
    if split_XYZ is True:
        cmd.append('-SPLIT_XYZ')
    if remove_C2C_SF is True:
        cmd.append('-REMOVE_SF')
        cmd.append('11')
        cmd.append('-REMOVE_SF')
        cmd.append('10')
        cmd.append('-REMOVE_SF')
        cmd.append('9')
        #cmd.append('-RENAME_SF')
        #cmd.append('LAST')
        #cmd.append('c2c_z')



    root, ext = os.path.splitext(compared)
    if max_dist:
        output = root + f'_C2C_DIST_MAX_DIST_{max_dist}.laz'
    else:
        output = root + '_C2C_DIST.laz'
    head, tail = os.path.split(output)

    misc.run(cmd, verbose=debug)

    # move the result if odir has been set
    if os.path.exists(odir) and odir is not None:
        overlap = os.path.join(odir, tail)
        shutil.move(output, overlap)
        output = overlap

    return output


# %%
#custom_c2c(compared, water_surface, global_shift=global_shift, debug=True, split_XYZ=True, cc_exe=cc_qlasio)

# %%
# #laz = laspy.read_bfe(
#     r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\Data\Ardeche_01102021\C3_fwf\TMP\Ardeche_01102021_L001_C3_r_w_C2C_DIST.laz')
# laz['C2C absolute distances (Z)']