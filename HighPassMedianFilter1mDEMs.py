import os
import sys
sys.path.insert(1, 'Y:/William/Skogsstyrelsen/dataprocessing/DitchNet/Preprocessing/util/WBT/')
from whitebox_tools import WhiteboxTools
whitebox_dir = os.path.dirname('Y:/William/Skogsstyrelsen/dataprocessing/DitchNet/Preprocessing/util/WBT/')
whitebox = WhiteboxTools()
whitebox.set_whitebox_dir(whitebox_dir)

import arcpy
from arcpy.sa import *
from arcpy import env
arcpy.env.compression = "NONE"
arcpy.env.pyramid = "NONE"
arcpy.env.overwriteOutput = True
arcpy.env.parallelProcessingFactor = "0%"
sr = arcpy.SpatialReference(3006)

DEMS1m = 'Y:/Swedish1mDEM/tilessinglefolder/'
relevanttiles = 'Y:/William/DeepLearning/DitchnetProduction/DEM1m32bitfloat/HighPassMedianFilter32/'
HighPassMedianFilter1m = 'Y:/William/Skogsstyrelsen/dataprocessing/DitchNet/HighPassMedianFilter/'
for file in os.listdir(relevanttiles):
    if file.endswith('.tif'):
        DemFile = DEMS1m + file

        HighPassMedianFilter = HighPassMedianFilter1m + file
        args_HPMF = ['--input=' + DemFile, '--output=' + HighPassMedianFilter, '--filterx=5', '--filtery=5', '--sig_digits=2']
        try:
            print(DemFile)
            print(HighPassMedianFilter)
            #whitebox.run_tool('HighPassMedianFilter', args_HPMF)
        except:
            print('Unexpected error:', sys.exc_info()[0])
            raise
