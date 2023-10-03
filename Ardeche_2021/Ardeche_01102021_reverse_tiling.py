import glob
import os

from lidar_platform.tools.src_id_line_num import get_name_id_dict, load_id_name_dictionary
from lidar_platform.tools import ReverseTiling

rootname = '_XX_'  # not used
workspace_c2 = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\Ardeche_01102021\C2_after_corr\tiles_500_gc\without_buffer'
workspace_c3 = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\Ardeche_01102021\C3_after_corr\correction_refraction\tiles_g\without_buffer'
buffer = False
cores = 20
pt_src_id_as_line_number = False

#%% GET LINE NUMBER POINT SOURCE ID DICTIONARY
dir_c2 = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\Ardeche_01102021\C2_after_corr'
lines_c2 = glob.glob(os.path.join(dir_c2, '*.laz'))
id_name_file_c2 = os.path.join(dir_c2, 'id_name.json')

if os.path.exists(id_name_file_c2):
    print(f'load existing dictionary {id_name_file_c2}')
    id_name_c2 = load_id_name_dictionary(id_name_file_c2)
else:
    name__id_list_c2, id_name_c2 = get_name_id_dict(lines_c2)

#%% REVERSE TILING
reverse_tiling_c2 = ReverseTiling.ReverseTiling(workspace_c2, rootname, buffer=buffer,
                                  cores=cores,
                                  pt_src_id_as_line_number=pt_src_id_as_line_number,
                                  id_name=id_name_c2)

#%% GET LINE NUMBER POINT SOURCE ID DICTIONARY
dir_c3 = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\Ardeche_01102021\C3_after_corr\correction_refraction'
lines_c3 = glob.glob(os.path.join(dir_c3, '*.laz'))
id_name_file_c3 = os.path.join(dir_c3, 'id_name.json')

if os.path.exists(id_name_file_c3):
    print(f'found an existing dictionary {id_name_file_c3}')
    id_name_c3 = load_id_name_dictionary(id_name_file_c3)
else:
    name__id_list_c3, id_name_c3 = get_name_id_dict(lines_c3)

#%% REVERSE TILING
reverse_tiling_c3 = ReverseTiling.ReverseTiling(workspace_c3, rootname,  # rootname unused
                                  buffer=buffer,
                                  cores=cores,
                                  pt_src_id_as_line_number=pt_src_id_as_line_number,
                                  id_name=id_name_c3)