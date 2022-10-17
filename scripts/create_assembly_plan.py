# Thomas Bernard
# 11/10/2022

import glob

from lidar_platform.qc import assembly_plan as ap

lines = glob.glob('G:\RENNES1\ThomasBernard\Ardeche_assembly_plan\Ardeche_01102021\C2_temp\*.laz')
odir = 'G:\RENNES1\ThomasBernard\Ardeche_assembly_plan\Ardeche_01102021\Assembly_plan'

out = ap.from_lines(lines, odir, epsg_src="epsg:2154", epsg_dst="epsg:4171")