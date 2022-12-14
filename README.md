# Titan_data_processing_TB information

Titan_data_processing_TB contains scripts and workflows developped by Thomas Bernard that aim to be used by anyone.
So before to use them please read this README file first to understand how it is structured.

You will find further details and descriptions in each of the following files.

There are four folders:
- ***"/Ardeche_2021"*** contains all scripts used to process the LiDAR data of the Ardeche
- ***"/Herault_2021"*** contains all scripts used to process the LiDAR data of the Herault
- ***"/scripts"*** contains some scripts, module and functions.
- ***"/Workflows"*** contains all workflows developed by Thomas Bernard used to process lidar data.

Here are some descriptions of the scripts:
- ***QC_inter_survey.py*** : *"Inter-survey quality check using tiles and M3C2"*
- ***QC_recouvrement.py*** : *"Intra-survey quality check using flight line overlaps and M3C2"*
- ***cc_interp_SF.py*** : *"Interpolation of a given scalar field from a cloud to another cloud using Cloudcompare"*
- ***classify_bathy.py*** : *"This script allows to classify points located in rivers based on a C2C distance
                      from a water surface point cloud. Result: .laz files with a new SF "Classification"
                      with 1 and 9 for unclassified and bathy respectively."*
- ***create_assembly_plan.py*** : *Create an assembly plan from .laz files in a given directory."*
- ***custom_c2c.py*** : *Custom cloud-to-cloud distance for FWF data using Cloudcompare with the Qlasio plugin".*

Here are some descriptions of the workflows:
 - ***SA_workflow*** : *"This workflow consists in applying StripAlign (SA) on multiple channels (C2/C3) and multiple epochs.
It take cares to first classify points in rivers (step 2) of all specified flight-lines from a water_surface
point cloud to exclude these points during the registration steps.
It is also possible to classify noisy points for FWF data using lastools (step 1).
In step 2bis you can classify points below a specified scan_angle absolute value.
Two quality check are performed: one before and one after the correction."*