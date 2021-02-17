import os
import sys

sys.path.insert(1, 'Y:/Sidd/WBT/') #the "r" infront means string litteral and means that you can have \ in the path instead of /.
from whitebox_tools import WhiteboxTools
whitebox_dir = os.path.dirname('Y:/Sidd/WBT/')
whitebox = WhiteboxTools()
whitebox.set_whitebox_dir(whitebox_dir)

import arcpy
from arcpy.sa import *
from arcpy import env
arcpy.env.compression = "NONE"
arcpy.env.pyramid = "NONE"
arcpy.env.overwriteOutput = True

DEMS = 'Y:/William/DeepLearning/DitchnetProduction/RenamedDEMTiles/'
FeaturePreservingSmoothing = 'R:/Temp/FeaturePreservingSmooth/'
HPMF = 'R:/Temp/HighPassMedianFilterUnsmoothed/'
VectorDitches = 'Y:/William/DeepLearning/DitchnetProduction/SplitDitchLines/'
RasterDitches = 'R:/Temp/RASTERDITCHES/'
ReclassifiedDitches = 'R:/Temp/ReclassifiedRASTERDITCHES/'
BufferRaster = 'R:/Temp/BufferRaster/'
ReclassHPMF = 'R:/Temp/ReclassHPMF/'
MultiplyStreamsWithBufferRaster = 'R:/Temp/MultiplyStreamsWithBufferRaster/'
#OR = 'R:/Temp/OR/'
OR = 'Y:/William/DeepLearning/DitchnetProduction/BinaryLabels/'
for file in os.listdir(DEMS):
    if file.endswith('.tif'):

        # convert vectorditches to raster
        VectorditchFile = VectorDitches + file.replace('.tif', '.shp')
        RasterditchFile = RasterDitches + file
        ReclassifiedRasterDitches = ReclassifiedDitches + file
        DemFile = DEMS + file
        args_rasterditch = ['--input=' + VectorditchFile,'--field=' + "FID", '--output=' + RasterditchFile, '--base=' + DemFile]

        # reclassify ditches to 1 and 0
        reclassifiedditches = ReclassifiedDitches + file
        reclassvalues = '1.0;1;100000' #(new value; from value; to less than)
        reclassify_args = ['--input=' + RasterditchFile, '--output=' + reclassifiedditches, '--reclass_vals=' + reclassvalues]

        # smooth dem
        FeaturePreservingSmooth = FeaturePreservingSmoothing + file
        args_featurepreservsmoothing = ['--dem=' + DemFile, '--output=' + FeaturePreservingSmooth, '--filter=11', '--norm_diff=15.0', '--num_iter=3', '--max_diff=1.5']

        # extract high pass median filter from smooth DEM
        HighPassMedianFilter = HPMF + file
        args_HPMF = ['--input=' + FeaturePreservingSmooth, '--output=' + HighPassMedianFilter, '--filterx=5', '--filtery=5', '--sig_digits=2']

        #Reclass HPMF
        ReclassifiedHPMF = ReclassHPMF  + file
        LessThan_args = ['--input1=' + HighPassMedianFilter,'--input2=-0.075',  '--output=' + ReclassifiedHPMF, '--reclass_vals=' + reclassvalues]

                # BufferRaster
        BufferRasterOutput = BufferRaster + file
        args_BufferRaster = ['--input=' + reclassifiedditches, '--output=' + BufferRasterOutput, '--size=6']

        # Multiply hpmf with areas of interest 6 m from digitized ditch lines.
        MultiplyOutput = MultiplyStreamsWithBufferRaster + file
        args_multiply = ['--input1=' + ReclassifiedHPMF, '--input2=' + BufferRasterOutput, '--output=' + MultiplyOutput]


        # AND. flag pixels that have high pass median filter lower than 0.1 OR was digitized as ditches
        Or = OR + file
        args_OR = ['--input1=' + reclassifiedditches, '--input2=' + MultiplyOutput, '--output=' + Or]


        try:
            whitebox.run_tool('FeaturePreservingSmoothing', args_featurepreservsmoothing)
            whitebox.run_tool("VectorLinesToRaster", args_rasterditch)
            whitebox.run_tool("Reclass", reclassify_args)
            whitebox.run_tool('HighPassMedianFilter', args_HPMF)
            whitebox.run_tool('LessThan', LessThan_args)
            whitebox.run_tool('BufferRaster', args_BufferRaster)
            whitebox.run_tool('Multiply', args_multiply)

            whitebox.run_tool('Or', args_OR)
        except:
            print('Unexpected error:', sys.exc_info()[0])
            raise

print("done")

os.chdir("R:/Temp/")
for root, dirs, files in os.walk(".", topdown = False):
   for file in files:
      print(os.path.join(root, file))
      os.remove(os.path.join(root, file))
# #Labels
# #create empty raster dataset for labels
# mdnameLabel = "mosaicLabels"
# arcpy.CreateMosaicDataset_management(gdbname, mdnameLabel, prjfile, noband,
#                                      pixtype, pdef, wavelength)
# mdname = "C:/SLU/William/ArcgisPro/WilliamDeepLearning/MosaicDatabase.gdb/mosaicLabels"
# inpathlabels = 'C:/SLU/William/Ditches/1mDEM/CopiedTrainingLabels/'
# #add labels to mosaic
# arcpy.AddRastersToMosaicDataset_management(
#      mdname,  rastype, inpathlabels)

#        arcpy.CopyRaster_management(outputreclass, out8bit,"","",65535,"NONE","NONE","8_BIT_UNSIGNED","NONE","NONE", "TIFF", "NONE", "ALL_SLICES", "TRANSPOSE")
#        arcpy.SetRasterProperties_management(out8bit, "THEMATIC","", "#", "#")
#        arcpy.BuildRasterAttributeTable_management(out8bit, "Overwrite")

# import arcpy
# arcpy.CheckOutExtension("ImageAnalyst")
# from arcpy.ia import *
#
# # Set local variables
# inRaster = "C:/SLU/William/ArcgisPro/WilliamDeepLearning/MosaicDatabase.gdb/mosaicds"
# out_folder = "D:/MosaicedLabels/ExportedChips4"
# in_training = "D:/MosaicedLabels/exportlabels.tif"
# image_chip_format = "TIFF"
# tile_size_x = "512"
# tile_size_y = "512"
# stride_x= "256"
# stride_y= "256"
# output_nofeature_tiles= "ONLY_TILES_WITH_FEATURES"
# metadata_format= "Classified_Tiles"
# start_index = 0
# classvalue_field = "ClassValue"
# buffer_radius = 0
# in_mask_polygons = 'C:/SLU/William/Ditches/1mDEM/SubsetSquares/TrainingSquares.shp'
# rotation_angle = 90
# reference_system = "MAP_SPACE"
# processing_mode = "PROCESS_AS_MOSAICKED_IMAGE"
# blacken_around_feature = ""
# crop_mode = ""
#
# # Execute
# ExportTrainingDataForDeepLearning(inRaster, out_folder, in_training,
#     image_chip_format,tile_size_x, tile_size_y, stride_x,
#     stride_y,output_nofeature_tiles, metadata_format, start_index,
#     classvalue_field, buffer_radius, in_mask_polygons, rotation_angle,
#     reference_system, processing_mode, blacken_around_feature, crop_mode)
