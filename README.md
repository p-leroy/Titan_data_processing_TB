# Titan_data_processing_TB information

Titan_data_processing_TB contains scripts and workflows developped by Thomas Bernard that aim to be used by anyone.
So before to use them please read this README file first to understand how it is structured.

You will find further details and descriptions in each of the following files.

There are two folders:
- ***"/scripts"*** contains some scripts, module and functions.
- ***"/Workflows"*** contains all workflows developed by Thomas Bernard used to process lidar data.

Here are some descriptions of the scripts:
 - ***classify_bathy.py*** : *"This script allows to classify points located in rivers based on a C2C distance
                       from a water surface point cloud. Result: .laz files with a new SF "Classification"
                       with 1 and 9 for unclassified and bathy respectively."*

Here are some descriptions of the workflows:
 - ***SA_workflow*** : *This workflow consists in applying StripAlign (SA) on multiple channels (C2/C3) and multiple epochs.
                 It take cares to first classify points in rivers of all specified flight-lines from a water_surface
                 point cloud to exclude these points during the registration steps.Two quality check are performed: one before and one after the correction."*