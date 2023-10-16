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
import glob

from lidar_platform import cc, las
from lidar_platform.config import global_shifts
from lidar_platform.config.config import cc_custom, cc_std, cc_std_alt,cc_2023_01_06
from scripts import custom_c2c as cc2c


#%% Compute C2C distances

def classify_bathy(workspace,epoch,Channels,max_dist,reference, out_dir, global_shift):
    # fixed parameters
    # rewrite C2C scalar fields (if use '-SPLIT_XYZ' option. Used by default)
    scalar_fields_old = ['C2C absolute distances[<20] (X)', 'C2C absolute distances[<20] (Y)','C2C absolute distances[<20] (Z)']
    scalar_fields_new = ['C2C (X)', 'C2C (Y)', 'C2C (Z)']

    # code
    for i in range(0,len(epoch)):
        for ii in range(0,len(Channels)):
            Channel = Channels[ii]
            path_temp = os.path.join(workspace, epoch[i], Channel)
            lines = [os.path.splitext(path)[0] for path in glob.glob(path_temp + '\*.laz')]

            for iii in range(0,len(lines)):
                file_path = lines[iii]
                if Channel=='C3_fwf' and i==0:
                    output = cc2c.custom_c2c(file_path+'.laz',  workspace + '\\' + reference, max_dist=max_dist, split_XYZ=True,
                                                 remove_C2C_SF=True, octree_level=11, global_shift=global_shift, silent= True,cc_exe=cc_2023_01_06)
                    if os.path.exists(output):
                        print('This solution does not work currently so you have to class all points with (C2C absolute distances[<20] (Z) < 1) & (classification == 0) as 9 in Cloudcompare')
                        # Operations
                        # The following operations with las.py does not work, there is a problem when using the function read_bfe and WriteLAS --> Error: "laszip.LaszipError: reading point 0 of 0 total points"
                        # --> when opening point cloud with las.read_bfe --> all array are filled of zeero and XYZ position is a single coordinate.
                        # So I did these operations directly in cloudcompare.
                        #outlas = las.read_bfe(file_path + f'_C2C_DIST_MAX_DIST_{max_dist}_SF_RENAMED.laz', extra_fields=True)
                        #new_classification = outlas.classification
                        #new_classification[(outlas['c2c_z'] <= 1) & (outlas.classification == 0)] = 9
                        #outlas.classification = new_classification
                        #c2c_z = outlas['c2c_z']
                        #extra_field = [(("c2c_z","float32"),c2c_z)]
                        #las.WriteLAS(file_path + f'_C2C_DIST.laz', outlas, format_id=4, extra_fields=extra_field)

                        # clean
                        #os.remove(file_path+'.laz')
                        #os.remove(file_path + f'_C2C_DIST_MAX_DIST_{max_dist}.laz')
                        #os.remove(file_path + f'_C2C_DIST_MAX_DIST_{max_dist}_SF_RENAMED.laz')
                        #os.rename(file_path + f'_C2C_DIST.laz', file_path+'.laz')
                    else:
                        outlas = las.read_bfe(file_path + '.laz')
                        new_classification = outlas.classification
                        new_classification[outlas.classification >= 0] = 1
                        outlas.classification = new_classification
                        las.WriteLAS(file_path + '_class.laz', outlas, format_id=4)
                        # Clean
                        os.remove(file_path + '.laz')
                        os.rename(file_path + '_class.laz', file_path + '.laz')

                else:
                    output=cc.c2c_dist(file_path+'.laz', workspace + '\\' + reference, global_shift=global_shift,
                                       max_dist=max_dist, split_XYZ=True, octree_level=11, odir=out_dir, export_fmt='SBF', silent=True)

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

                        print('Save SBF file in LAZ...')
                        cc.to_laz(output, remove=True, silent=True, cc_exe=cc_std_alt)

                        # Clean
                        file_name = os.path.basename(file_path)
                        #os.remove(os.path.join(path_temp, file_name + '.laz' ))
                        outlas = las.read_bfe(os.path.join(path_temp, file_name + f'_C2C_DIST_MAX_DIST_{max_dist}.laz'))
                        las.WriteLAS(os.path.join(path_temp, file_name + '.laz'), outlas)
                        os.remove(os.path.join(path_temp, file_name + f'_C2C_DIST_MAX_DIST_{max_dist}.laz'))

                    else:
                        outlas = las.read_bfe(file_path + '.laz')
                        new_classification = outlas.classification
                        new_classification[outlas.classification >= 0] = 1
                        outlas.classification = new_classification
                        las.WriteLAS(file_path + '_class.laz', outlas, format_id = 1)
                        #Clean
                        os.remove(file_path + '.laz')
                        os.rename(file_path + '_class.laz', file_path + '.laz' )


