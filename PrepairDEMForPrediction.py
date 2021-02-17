# this script converts the raw DEM to high pass median filter files used for the prediction of ditches
# The Mode expects tiles of the size 512 x 512 pixels and one band.
# Values need to be rescaled between 0 and 1 and
# data type need to be unsigned 8 bit int (values between 0 and 255)

import os
import sys
import arcpy
import time
start = time.time()
arcpy.env.pyramid = 'NONE'
arcpy.env.parallelProcessingFactor = '0%' # This is faster without parallel processing
arcpy.env.overwriteOutput = True
sys.path.insert(1, r'C:\William_Program\WhiteboxTools_win_amd64\WBT') #This is where whitebox tools is stored.
from whitebox_tools import WhiteboxTools
arcpy.env.compression = "NONE"
sr = arcpy.SpatialReference(3006)

wb_dir = os.path.dirname('C:/William_Program/WhiteboxTools_win_amd64/WBT/')
wbt = WhiteboxTools()
wbt.set_whitebox_dir(wb_dir)
INPUTDEMS = 'Y:/William/DeepLearning/DitchnetProduction/RenamedDEMTiles/'
#INPUTDEMS = 'Y:/William/DeepLearning/1mDEM/Aggregateto1m/'
#FPSM = 'Y:/William/DeepLearning/1mDEM/FeaturePreservingSmooth/'
FPSM = 'R:/Temp/FeaturePreservingSmooth/'
HPMF = 'Y:/William/DeepLearning/1mDEM/HighPassMedianFilter/'
#HPMF = 'R:/Temp/HighPassMedianFilter/'
#HPMFInverted = 'Y:/William/DeepLearning/1mDEM/HighPassMedianFilterInverted/'
HPMFInverted = 'R:/Temp/HighPassMedianFilterInverted/'
#SplitDEM = 'Y:/William/DeepLearning/1mDEM/SplitTiles/'
HPMF8bit = 'R:/Temp/HPMF8bit/'
SplitDEM = 'R:/Temp/SplitTiles/'
for file in os.listdir(INPUTDEMS):
    if file.endswith('.tif'):
        rawdem = INPUTDEMS + file
        FeaturePreservSmoothed = FPSM + file
        HighPassMedianFilter = HPMF + file
        HighPassMedianFiterInverted = HPMFInverted + file
        args1 = ['--dem=' + rawdem, '--output=' + FeaturePreservSmoothed, '--filter=11', '--norm_diff=15.0', '--num_iter=3', '--max_diff=1.5']
        args2 = ['--input=' + FeaturePreservSmoothed, '--output=' + HighPassMedianFilter, '--filterx=5', '--filtery=5', '--sig_digits=2']
        args3 = ['--input1=' + HighPassMedianFilter, '--input2=' + '-100', '--output=' + HighPassMedianFiterInverted]
        Copyout8bit = HPMF8bit + file
        try:
            wbt.run_tool('FeaturePreservingSmoothing', args1)
            print('Smoothing complete for: ' + file)
            wbt.run_tool('HighPassMedianFilter', args2)
            print('HPMF complete for: ' + file)
            #arcpy.DefineProjection_management(HighPassMedianFilter, sr)
            #wbt.run_tool('Multiply', args3)
            #arcpy.env.parallelProcessingFactor = "0%"
            #arcpy.CopyRaster_management(HighPassMedianFiterInverted, Copyout8bit,"","","","","","8_BIT_UNSIGNED","","", "TIFF", "", "", "")
            #print('Copy complete for: ' + file)
            ##Equally split a large TIFF image by size of images
            #arcpy.SplitRaster_management(Copyout8bit, SplitDEM, file, "SIZE_OF_TILE","TIFF", "NEAREST", "#", "512 512", "10", "PIXELS",\
             #                "#")

        except:
            print('Unexpected error:', sys.exc_info()[0])
# from PIL import Image
# #from ImportData import write_gtiff
# import numpy
# import tifffile as tiff

# im_width = 512
# im_height = 512
# inputpath = 'R:/Temp/SplitTiles/'
# outputpath
# outputpathwithExtent
#
#
# inputpath = "Y:/William/DeepLearning/UnetVersion2/unet/data/ExportedChips4/testdata/"
# outputpath = 'Y:/William/DeepLearning/UnetVersion2/unet/data/temppreds/'
# outputpathwithExtent = 'Y:/William/DeepLearning/UnetVersion2/unet/data/predictionswithextent/'
# for file in os.listdir(inputpath):
#     if file.endswith('.tif'):
#         inputfile = inputpath + file
#         outputfile = outputpath + file
#         listofonefile = []
#         listofonefile.append(inputfile)
#         K = np.zeros((len(listofonefile), im_height, im_width, 1), dtype=np.float32)
#         img = load_img(inputfile, color_mode='grayscale')
#         x_img = img_to_array(img)
#         x_img = resize(x_img, (512, 512, 1), mode = 'constant', preserve_range = True)
#         K[:1] = x_img/255.0 # Original predictions are values between 0 and 1. Multiply it by 255 to get a 8 bit image or export as float.
#         #print(len(K[:1]))
# end = time.time()
# print('The whole script took ',end - start ,'seconds')
# input('Press ENTER to exit')

# os.chdir("R:/Temp/")
# for root, dirs, files in os.walk(".", topdown = False):
#    for file in files:
#       print(os.path.join(root, file))
#       os.remove(os.path.join(root, file))
