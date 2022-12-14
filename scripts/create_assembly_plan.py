# Thomas Bernard
# 11/10/2022

import glob

from lidar_platform.qc import assembly_plan as ap

lines = glob.glob(r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\04-QC\Overlap\Ardeche_inter_survey\C3_01102021_base_FWF\*.laz')
odir = r'G:\RENNES1\ThomasBernard\StripAlign\Ardeche\results\04-QC\Overlap\Ardeche_inter_survey\C3_01102021_base_FWF\Assembly_plan'

out = ap.from_lines(lines, odir, epsg_src="epsg:2154", epsg_dst="epsg:4171")

