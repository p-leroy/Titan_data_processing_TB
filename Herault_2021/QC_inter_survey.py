import glob
import os
import shutil

from joblib import delayed, Parallel

from lidar_platform import cc, global_shifts, misc

in_1 = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\Ardeche_01102021\C3_after_corr'  # Ardeche_01102021_L001_C2_r_1.laz
in_2 = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\Ardeche_18102021\C3_after_corr'  # Ardeche_18102021_L01_C2_r_1.laz
out = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\04-QC\Overlap\Ardeche_inter_survey'
dir_tiles_1 = os.path.join(out, 'C3_01102021')
dir_cores = os.path.join(dir_tiles_1, 'CORE_POINTS')
m3c2_dir = os.path.join(dir_tiles_1, 'M3C2')
dir_tiles_2 = os.path.join(out, 'C3_18102021')
params = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\04-QC\Overlap\Ardeche_inter_survey\m3c2_params.txt'
global_shift = global_shifts.Ardeche
FWF = False

cc_qlasio = r'G:\RENNES1\PaulLeroy\CloudCompare_20221202\CloudCompare.exe'

tile_size = 1000

def index_laz(lines):
    """
    Index laz files for better handling by lastile
    :param lines:
    :return:
    """
    misc.run(f'lasindex -i {lines} -cores 20')  # you have to index the data first


def make_tiles(lines, dir_tiles, o, buffer=250, cores=20, tile_size=1000):
    """
    Make tiles with a buffer
    :param lines:
    :param dir_tiles:
    :param buffer:
    :param o:
    :param cores:
    :return:
    """
    os.makedirs(dir_tiles, exist_ok=True)
    misc.run(f'lastile -i {lines} -tile_size {tile_size} -buffer {buffer} -cores {cores} -odir {dir_tiles} -o {o}')


def clean_lax(dir_):
    """
    Remove all lax files from the specified directory
    :param dir_:
    :return:
    """
    [os.remove(file) for file in glob.glob(os.path.join(dir_, '*.lax'))]


def clip_tile(tile, coordinates_position=1, tile_size=1000):

    head, tail = os.path.split(tile)
    odir = os.path.join(head, 'without_buffer')
    os.makedirs(odir, exist_ok=True)

    pc, sf, config = cc.read_sbf(tile)
    global_x, global_y, _ = eval(config['SBF']['GlobalShift'])
    x, y = pc[:, 0], pc[:, 1]
    x_min, y_min = [int(val) for val in tail.split('_')[coordinates_position:coordinates_position+2]]
    x_min += global_x
    y_min += global_y
    x_max = x_min + tile_size
    y_max = y_min + tile_size

    # look for data which falls inside the box
    index = (x_min < x) & (x < x_max) & (y_min < y) & (y < y_max)

    # save the data (same name but different directory)
    o = os.path.join(odir, tail)
    cc.write_sbf(o, pc[index, :], sf[index, :], config)

    return o, index

#%% make tiles epoch 1 C2 01 10 2021
lines_1 = os.path.join(in_1, '*_C3_r_1.laz')
o_1 = 'tile.laz'
index_laz(lines_1)
make_tiles(lines_1, dir_tiles_1, o_1, buffer=10)
clean_lax(in_1)

#%% make tiles epoch 2 18 10 2021
lines_2 = os.path.join(in_2, '*.laz')
o_2 = 'tile.laz'
index_laz(lines_2)
make_tiles(lines_2, dir_tiles_2, o_2, buffer=10)
clean_lax(in_2)

#%% compute core points
spacing=1
tiles_1 = glob.glob(os.path.join(dir_tiles_1, '*.laz'))
cores = Parallel(n_jobs=10, verbose=0)(
    delayed(cc.rasterize)(tile, spacing, ext='_RASTER', proj='AVG', global_shift='AUTO')
    for tile in tiles_1)

#%% move cores to a special directory
os.makedirs(dir_cores, exist_ok=True)
for core in cores:
    shutil.move(core, dir_cores)
    shutil.move(core + '.data', dir_cores)

#%% Drop classes
bin_lastools = 'C:/opt/LAStools/bin'
epsg=2154
tiles_1 = glob.glob(os.path.join(dir_tiles_1, '*.laz'))
tiles_2 = glob.glob(os.path.join(dir_tiles_2, '*.laz'))
list_tiles = [tiles_1, tiles_2]
count= 0
for tiles in list_tiles:
    for tile in tiles:
        cmd = os.path.join(bin_, 'las2las')
        args = f' -i {tile} -odix _filtered -olaz'
        args += (f' -drop_class 7 9') # drop noise and water
        if count > 0 and FWF == True:
            args += (' -drop_intensity_below 50')
        args += f' -epsg {epsg} -meter -elevation_meter'
        misc.run(cmd + args)

        #clean
        infile = os.path.splitext(tile)[0]
        if os.path.exists(infile + '_filtered.laz'):
            os.remove(tile)
            os.rename(infile+'_filtered.laz', infile + '.laz')
    count = count + 1

#%% build M3C2 configuration to be computed at the next step
tiles_2 = glob.glob(os.path.join(dir_tiles_2, '*.laz'))
no_correspondence = []
correspondences = []
for tile_1 in tiles_1:
    head_1, tail_1 = os.path.split(tile_1)
    root_1, ext_1 = os.path.splitext(tail_1)
    tile_2 = os.path.join(dir_tiles_2, tail_1)
    if tile_2 in tiles_2:
        core_1 = os.path.join(dir_cores, root_1 + '_RASTER.sbf')
        correspondences.append((tile_1, tile_2, core_1))
    else:
        print(f'no corresponding tile in epoch 2 for {tile_1}')
        no_correspondence.append(tile_1)

#%% compute M3C2 distances
results = Parallel(n_jobs=10, verbose=0)(
    delayed(cc.m3c2)(tile_1, tile_2, params, core_1, global_shift='AUTO', debug=True, cc=cc_qlasio)
    for tile_1, tile_2, core_1 in correspondences)

#%% move M3C2 results in a specific directory
os.makedirs(m3c2_dir, exist_ok=True)
list_m3c2 = glob.glob(os.path.join(dir_tiles_1, '*_M3C2.sbf'))
for file in list_m3c2:
    shutil.move(file, m3c2_dir)
    shutil.move(file + '.data', m3c2_dir)

#%% remove buffers
to_clip = glob.glob(os.path.join(m3c2_dir, '*.sbf'))
for tile in to_clip:
    clip_tile(tile, coordinates_position=1, tile_size=tile_size)

#%% merge results
to_merge = glob.glob(os.path.join(m3c2_dir, 'without_buffer', '*.sbf'))
merged = cc.merge(to_merge, debug=True, global_shift=global_shift)

#####################
# ADDITIONAL MATERIAL
#####################

#%% get x and y ranges
x_list = []
y_list = []
for file in glob.glob(r'G:\RENNES1\ThomasBernard\test_m3c2_inter_survey\C2_01102021\*.laz'):
    head, tail = os.path.split(file)
    root, ext = os.path.splitext(tail)
    x_list.append(int(root.split('_')[1]))
    y_list.append(int(root.split('_')[2]))
x_min, x_max = min(x_list), max(x_list)
y_min, y_max = min(y_list), max(y_list)
center_x = (x_max - x_min) / 2
center_y = (y_max - y_min) / 2
print(f'x range {x_min} {x_max}, center {x_min + center_x}, delta {x_max - x_min}')
print(f'y range {y_min} {y_max}, center {y_min + center_y}, delta {y_max - y_min}')

#%% count points in sbf files
files = glob.glob(r'G:\RENNES1\ThomasBernard\test_m3c2_inter_survey\C2_01102021\M3C2\without_buffer\*.sbf')
N = 0
for file in files:
    config = cc.read_sbf_header(file)
    N += int(config['SBF']['Points'])