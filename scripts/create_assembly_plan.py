# Thomas Bernard
# 11/10/2022

import glob

from lidar_platform.qc import assembly_plan as ap

lines = glob.glob('G:\RENNES1\ThomasBernard\StripAlign\Herault\Data\Herault_30092021\C2\*.laz')
odir = 'G:\RENNES1\ThomasBernard\Herault_assembly_plan\Assembly_plan'

out = ap.from_lines(lines, odir, epsg_src="epsg:2154", epsg_dst="epsg:4171")

