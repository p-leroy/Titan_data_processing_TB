# Thomas Bernard
# 07/10/2022
"""
This script allows to classify points located in rivers based on a C2C distance
from a water surface point cloud.
Result: .laz files with a new SF "Classification" with 1 and 9 for unclassified and bathy respectively.
You can see an example of using this function in the SA_workflow.py file
"""
import os
import numpy as np

from lidar_platform import cc, las
from lidar_platform.config import global_shifts


#%% Compute C2C distances

def classify_bathy(workspace,epoch,Num_lines_a,Num_lines_b,Channels,max_dist,reference,out_dir,global_shift,path_output):
    # fixed parameters
    # rewrite C2C scalar fields (if use '-SPLIT_XYZ' option. Used by default)
    scalar_fields_old = ['C2C absolute distances[<20] (X)', 'C2C absolute distances[<20] (Y)','C2C absolute distances[<20] (Z)']
    scalar_fields_new = ['C2C (X)', 'C2C (Y)', 'C2C (Z)']
    nb_lines = len(Num_lines_a)  # Number of line per channel

    # code
    for i in range(0,len(epoch)):
        for ii in range(0,len(Channels)):
            Channel = Channels[ii]
            path_temp = workspace + '\\' + epoch[i] + '\\' + Channel + '\\'
            for iii in range(0,nb_lines):
                if i == 0:
                    num_line = Num_lines_a[iii]
                else:
                    num_line = Num_lines_b[iii]

                file_name = epoch[i] + f'_L{num_line}_{Channel}_r_1'
                output=cc.c2c_dist(path_temp + file_name + '.laz', workspace + '\\' + reference, global_shift, max_dist=max_dist, split_XYZ=True, odir=out_dir, export_fmt='SBF', silent=True)
                # Operations on sfs
                if os.path.exists(output):
                    pc, sf, config = cc.read_sbf(output)
                    for iv in range (0,len(scalar_fields_new)):
                        if iv == len(scalar_fields_new)-1:
                            cc.rename_sf(scalar_fields_old[iv], scalar_fields_new[iv],config)
                        else:
                            sf, config = cc.remove_sf(scalar_fields_old[iv],sf,config)

                    sf, config = cc.remove_sf('C2C absolute distances[<20]' , sf, config)
                    name_index = cc.get_name_index_dict(config)
                    index = name_index[scalar_fields_new[-1]]
                    sf_C2C_Z = sf[:,index]
                    sf_to_add = np.copy(sf_C2C_Z)
                    sf_to_add[sf_C2C_Z <= 1] = 9
                    sf_to_add[sf_C2C_Z > 1] = 1
                    sf = cc.add_sf('Classification',sf,config,sf_to_add)
                    sf, config = cc.remove_sf(scalar_fields_new[-1], sf, config)
                    cc.write_sbf(output,pc,sf,config)
                    cc.to_laz(output)
                    # Clean
                    root, ext = os.path.splitext(file_name)
                    os.remove(path_output + epoch[i] + '/' + Channel + '/'+ root + f'_C2C_DIST_MAX_DIST_{max_dist}.sbf')
                    os.remove(path_output + epoch[i] + '/' + Channel + '/'+ root + f'_C2C_DIST_MAX_DIST_{max_dist}.sbf.data')
                    os.remove(path_output + epoch[i] + '/' + Channel + '/'+ root + '.laz' )
                    outlas = las.read(workspace + f'\{epoch[i]}\{Channel}\{file_name}_C2C_DIST_MAX_DIST_{max_dist}.laz')
                    las.WriteLAS(workspace + f'\{epoch[i]}\{Channel}\{file_name}.laz', outlas)
                    os.remove(path_output + epoch[i] + '/' + Channel + '/'+ root + f'_C2C_DIST_MAX_DIST_{max_dist}.laz')
                else:
                    outlas = las.read(path_temp + file_name + '.laz')
                    class_field = np.ones(np.shape(outlas['point_source_id']))
                    extra_field = [(("Classification", "uint8"), class_field)]
                    las.WriteLAS(path_temp + file_name + '_class.laz', outlas, format_id = 1, extra_fields = extra_field)
                    os.remove(path_temp + file_name + '.laz')
                    os.rename(path_temp + file_name + '_class.laz', path_temp + file_name + '.laz' )


