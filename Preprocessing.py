# Ignore the errors. its working as intended.
import os
import sys
import glob
import arcpy
from arcpy.sa import *
from arcpy import env
import time
import shutil
import util.Functions

sys.path.insert(1, 'Y:/WBT/')
from whitebox_tools import WhiteboxTools
whitebox_dir = os.path.dirname('Y:/WBT/')
whitebox = WhiteboxTools()
whitebox.set_whitebox_dir(whitebox_dir)

arcpy.env.compression = "NONE"
arcpy.env.pyramid = "NONE"
arcpy.env.overwriteOutput = True
sr = arcpy.SpatialReference(3006)

VectorDitches = 'Y:/William/DeepLearning/Writing/supplementary/data/ditchlines/' #Ditches split based on dem tiles
DEMTILES = 'Y:/William/DeepLearning/Writing/supplementary/data/rastertiles/' # copied demtiles that intersect with study areas
HPMF = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/Processing/HighPassMedianFilter05m/'
RasterDitches = 'C:/Temp/RASTERDITCHES/'
ReclassifiedDitches = 'C:/Temp/ReclassifiedRASTERDITCHES/'
BufferRaster = 'C:/Temp/BufferRaster/'
ReclassHPMF = 'C:/Temp/ReclassHPMF/'
MultiplyStreamsWithBufferRaster = 'C:/Temp/MultiplyStreamsWithBufferRaster/'
SmoothStreamBuffer = 'C:/Temp/SmoothStreamBuffer/'
OR = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/Processing/BinaryLabels05mDEM/' #These are combined variable width labels with high pas smedian filter


# convert vector ditches to raster labels
for file in os.listdir(DEMTILES):
    if file.endswith('.tif'):

        # convert vectorditches to raster
        VectorditchFile = VectorDitches + file.replace('.tif', '.shp')
        RasterditchFile = RasterDitches + file
        ReclassifiedRasterDitches = ReclassifiedDitches + file
        DemFile = DEMTILES + file
        args_rasterditch = ['--input=' + VectorditchFile,'--field=' + "FID", '--output=' + RasterditchFile, '--base=' + DemFile]

        # reclassify raster ditches to 1 and 0
        reclassifiedditches = ReclassifiedDitches + file
        reclassvalues = '1.0;1;100000' #(new value; from value; to less than)
        reclassify_args = ['--input=' + RasterditchFile, '--output=' + reclassifiedditches, '--reclass_vals=' + reclassvalues]

        # High pass median filter
        DemFile = DEMTILES + file
        HighPassMedianFilter = HPMF + file
        args_HPMF = ['--input=' + DemFile, '--output=' + HighPassMedianFilter, '--filterx=11', '--filtery=11', '--sig_digits=2']

        # Reclass HPMF
        ReclassifiedHPMF = ReclassHPMF  + file
        LessThan_args = ['--input1=' + HighPassMedianFilter,'--input2=-0.075',  '--output=' + ReclassifiedHPMF, '--reclass_vals=' + reclassvalues]

        # BufferRaster by 6 cells or 3 meters. Average ditch width in sweden + 1 stdv is 3 meter.
        BufferRasterOutput = BufferRaster + file
        args_BufferRaster = ['--input=' + reclassifiedditches, '--output=' + BufferRasterOutput, '--size=3']

        # Multiply hpmf with areas of interest 3 m from digitized ditch lines.
        MultiplyOutput = MultiplyStreamsWithBufferRaster + file
        args_multiply = ['--input1=' + ReclassifiedHPMF, '--input2=' + BufferRasterOutput, '--output=' + MultiplyOutput]

        #majority filter
        smooth = SmoothStreamBuffer + file
        args_smooth = ['--input=' + MultiplyOutput, '--output=' + smooth, '--filterx=3', '--filtery=3']

        # Alogical or operation will flag pixels that have high pass median filter lower than -0.075 OR was digitized as ditches
        Or = OR + file
        args_OR = ['--input1=' + reclassifiedditches, '--input2=' + smooth, '--output=' + Or]

        try:
            arcpy.DefineProjection_management(DemFile, sr)
            arcpy.DefineProjection_management(VectorditchFile, sr)
            whitebox.run_tool('HighPassMedianFilter', args_HPMF)
            whitebox.run_tool("VectorLinesToRaster", args_rasterditch)
            whitebox.run_tool("Reclass", reclassify_args)
            whitebox.run_tool('LessThan', LessThan_args)
            whitebox.run_tool('BufferRaster', args_BufferRaster)
            whitebox.run_tool('Multiply', args_multiply)
            whitebox.run_tool('MajorityFilter', args_smooth)
            whitebox.run_tool('Or', args_OR)

            print('Delete temp files')
            arcpy.Delete_management(reclassifiedditches)
            arcpy.Delete_management(ReclassifiedHPMF)
            arcpy.Delete_management(BufferRasterOutput)
            arcpy.Delete_management(MultiplyOutput)
            arcpy.Delete_management(smooth)
        except:
            print('Unexpected error:', sys.exc_info()[0])
            raise

print("Label tiles complete")
print('Create a file geodatabase')
arcpy.CreateFileGDB_management('Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/Processing/Geodatabases05m', 'HPMF.gdb')

# Create a ampty raster dataset within the geodatabase
mdnameLabel = 'HPMF' #name of raster dataset
gdbname = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/Processing/Geodatabases05m/HPMF.gdb'
mdname = "MosaicHPMF"
prjfile = "PROJCS['SWEREF99_TM',GEOGCS['GCS_SWEREF99',DATUM['D_SWEREF99',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',15.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]"
noband = "1"
pixtype = '32_BIT_FLOAT'
pdef = "NONE"
wavelength = ""

# Create empty dataset
print('Create empty dataset')
arcpy.CreateMosaicDataset_management(gdbname, mdname, prjfile, noband, pixtype, pdef, wavelength)

mdname = "Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/Processing/Geodatabases05m/HPMF.gdb/MosaicHPMF"
rastype = "Raster Dataset"
inpath = HPMF

# Add HPMF tiles to dataset
print('Add HPMF tiles to dataset')
arcpy.AddRastersToMosaicDataset_management(mdname,  rastype, inpath)


#Labels
print('create a file geodatabase')
arcpy.CreateFileGDB_management('Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/Processing/Geodatabases05m', 'Labels.gdb')
print('Create a ampty raster dataset within the geodatabase')
mdnameLabel = "Labels"

gdbname = "Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/Processing/Geodatabases05m/Labels.gdb"
mdname = "MosaicLabels05m_3m"
prjfile = "PROJCS['SWEREF99_TM',GEOGCS['GCS_SWEREF99',DATUM['D_SWEREF99',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',15.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]"
noband = "1"
pixtype = "8_BIT_UNSIGNED"
pdef = "NONE"
wavelength = ""

arcpy.CreateMosaicDataset_management(gdbname, mdname, prjfile, noband,pixtype, pdef, wavelength)


mdname = "Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/Processing/Geodatabases05m/Labels.gdb/MosaicLabels05m_3m"
rastype = "Raster Dataset"
inpath = OR #Binary labels

print('add Binary labes to dataset')
arcpy.AddRastersToMosaicDataset_management(mdname,  rastype, inpath)

# transform the data to 8 bit thematic raster and create a attribute table which is required for the export training data for deep learning tool.
out8bit = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/Processing/Exported8bitLabels/LabelsMosaic05m_3m.tif'
extents = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/Processing/Extents/'
labelsdir = 'D:/AI/Exported05mLabels/'
for file in os.listdir(extents):
    if file.endswith('.shp'):
        try:
            print('describe extent of', file.replace('.shp','.tif'))
            extentfile = extents + file
            desc = arcpy.Describe(extentfile)
            ext = desc.extent
            arcpy.env.extent = ext
            out8bit = labelsdir + file.replace('.shp', '.tif')
            print('Copy', out8bit, 'to 8 bit unsigned')
            arcpy.CopyRaster_management(mdname, out8bit,"","","","NONE","NONE","8_BIT_UNSIGNED","NONE","NONE", "TIFF", "NONE", "ALL_SLICES", "TRANSPOSE")
            print('Set raster properties to THEMATIC')
            arcpy.SetRasterProperties_management(out8bit, "THEMATIC","", "#", "#")
            print('Build Raster attribute table')
            arcpy.BuildRasterAttributeTable_management(out8bit, "Overwrite")
            print('Add field')
            arcpy.AddField_management(out8bit, 'ClassValue', "TEXT")
            print('Calculate field')
            arcpy.CalculateField_management(out8bit, 'ClassValue', "!Value!","PYTHON3")
        except:
            print('Unexpected error:', sys.exc_info()[0])
            raise

# this scripts uses arcpy to export high pass median filter and manuay mapped ditches as training dataset
# Import system modules and check out ArcGIS Image Analyst extension license
import arcpy, os
arcpy.CheckOutExtension("ImageAnalyst")
from arcpy.ia import *
arcpy.env.compression = "NONE"
arcpy.env.pyramid = "NONE"
arcpy.env.overwriteOutput = True

folderwithlabels = 'D:/AI/Exported05mLabels/'

# inraster is the high pass s median filter that will be exported with the labels
inRaster = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/Processing/Geodatabases05m/HPMF.gdb/MosaicHPMF'
#This is the labels
in_training = 'D:/AI/Exported05mLabels/ExtentCenter.tif'

# The data will be split by 80 % training and 20 % testing. The training data have overlapping tiles to augment more data. The testing data do not have any overlap.
out_folder_training = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/TrainingData/HighPassMedianFilter3mDEM05mNonoverlapping/CenterTrainingTiles3'
out_folder_testing = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/TrainingData/HighPassMedianFilter3mDEM05m/CenterTestingTiles3'

#training lidar
lidarsquares = 'Y:/William/DeepLearning/Writing/supplementary/data/vectorfiles/digitizedsquares.shp'
trainingtiles = "Y:/William/DeepLearning/DitchnetProduction/Digitaliserade_rutor_20191202/training.shp"
testingtiles = "Y:/William/DeepLearning/DitchnetProduction/Digitaliserade_rutor_20191202/testing.shp"
# split input lidar squares into 80 % traning and 20 % testing
size_of_training_dataset = "80"
subsizeUnits = "PERCENTAGE_OF_INPUT"
# Execute SubsetFeatures
arcpy.SubsetFeatures_ga(lidarsquares, trainingtiles, testingtiles,trainData, subsizeUnits)

# Center
print('Export training data')
image_chip_format = "TIFF"
tile_size_x = "512"
tile_size_y = "512"
stride_x= "512"
stride_y= "512"
output_nofeature_tiles= "ONLY_TILES_WITH_FEATURES"
metadata_format= "Classified_Tiles"
start_index = 0
classvalue_field = 'Value'
buffer_radius = 0 # This is somehing to consider. Right now the model trains untill the very edge of the tiles
in_mask_polygons = "Y:/William/DeepLearning/DitchnetProduction/Digitaliserade_rutor_20191202/training.shp" # only data within these polygons will be exported. This is to avoid exporting large areas of no data.
rotation_angle = 0
reference_system = "MAP_SPACE"
processing_mode = "PROCESS_AS_MOSAICKED_IMAGE"
blacken_around_feature = ""
crop_mode = ""

# Execute
ExportTrainingDataForDeepLearning(inRaster, out_folder_training, in_training,
    image_chip_format,tile_size_x, tile_size_y, stride_x,
    stride_y,output_nofeature_tiles, metadata_format, start_index,
    classvalue_field, buffer_radius, in_mask_polygons, rotation_angle,
    reference_system, processing_mode, blacken_around_feature, crop_mode)

#Export testing data
# note that the test data is not being rotaded and there is no overlap.
image_chip_format = "TIFF"
tile_size_x = "512"
tile_size_y = "512"
stride_x= "512" # Stride means that the tiles will have overlap in both x and y directions
stride_y= "512"
output_nofeature_tiles= "ONLY_TILES_WITH_FEATURES"
metadata_format= "Classified_Tiles"
start_index = 0
classvalue_field = 'Value'
buffer_radius = 0 # This is somehing to consider. Right now the model trains untill the very edge of the tiles
in_mask_polygons = "Y:/William/DeepLearning/DitchnetProduction/Digitaliserade_rutor_20191202/testing.shp" # only data within these polygons will be exported. This is to avoid exporting large areas of no data.
rotation_angle = 0
reference_system = "MAP_SPACE"
processing_mode = "PROCESS_AS_MOSAICKED_IMAGE"
blacken_around_feature = ""
crop_mode = ""

# Execute
print('exporting testingdata center')
ExportTrainingDataForDeepLearning(inRaster, out_folder_testing, in_training,
    image_chip_format,tile_size_x, tile_size_y, stride_x,
    stride_y,output_nofeature_tiles, metadata_format, start_index,
    classvalue_field, buffer_radius, in_mask_polygons, rotation_angle,
    reference_system, processing_mode, blacken_around_feature, crop_mode)

#This is the North
in_training = 'D:/AI/Exported05mLabels/ExtentNorth.tif'
#in_training = folderwithlabels + region
#in_training = '"Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/Processing/Geodatabases05m/Labels.gdb/MosaicLabels05m_3m"'
#in_training = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/Processing/Exported8bitLabels/LabelsMosaic05m_3m.tif'
# The data will be split by 80 % training and 20 % testing. The training data have overlapping tiles to augment more data. The testing data do not have any overlap.
out_folder_training = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/TrainingData/HighPassMedianFilter3mDEM05mNonoverlapping//NorthTrainingTiles3'
out_folder_testing = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/TrainingData/HighPassMedianFilter3mDEM05m/NorthTestingTiles3'

#training lidar
trainingtiles = "Y:/William/DeepLearning/DitchnetProduction/Digitaliserade_rutor_20191202/training.shp"
testingtiles = "Y:/William/DeepLearning/DitchnetProduction/Digitaliserade_rutor_20191202/testing.shp"
# split input lidar squares into 80 % traning and 20 % testing
size_of_training_dataset = "80"
subsizeUnits = "PERCENTAGE_OF_INPUT"
# Execute SubsetFeatures
arcpy.SubsetFeatures_ga(lidarsquares, trainingtiles, testingtiles,trainData, subsizeUnits)


# Export training data
image_chip_format = "TIFF"
tile_size_x = "512"
tile_size_y = "512"
stride_x= "512" # Stride means that the tiles will have overlap in both x and y directions
stride_y= "512"
output_nofeature_tiles= "ONLY_TILES_WITH_FEATURES"
metadata_format= "Classified_Tiles"
start_index = 0
classvalue_field = 'Value'
buffer_radius = 0 # This is somehing to consider. Right now the model trains untill the very edge of the tiles
in_mask_polygons = "Y:/William/DeepLearning/DitchnetProduction/Digitaliserade_rutor_20191202/training.shp" # only data within these polygons will be exported. This is to avoid exporting large areas of no data.
rotation_angle = 0 # a rotation of 90 degrees will be applied to the training data
reference_system = "MAP_SPACE"
processing_mode = "PROCESS_AS_MOSAICKED_IMAGE"
blacken_around_feature = ""
crop_mode = ""

print('exporting training north')
# Execute
ExportTrainingDataForDeepLearning(inRaster, out_folder_training, in_training,
    image_chip_format,tile_size_x, tile_size_y, stride_x,
    stride_y,output_nofeature_tiles, metadata_format, start_index,
    classvalue_field, buffer_radius, in_mask_polygons, rotation_angle,
    reference_system, processing_mode, blacken_around_feature, crop_mode)

#Export testing data
# note that the test data is not being rotaded and there is no overlap.
image_chip_format = "TIFF"
tile_size_x = "512"
tile_size_y = "512"
stride_x= "512" # Stride means that the tiles will have overlap in both x and y directions
stride_y= "512"
output_nofeature_tiles= "ONLY_TILES_WITH_FEATURES"
metadata_format= "Classified_Tiles"
start_index = 0
classvalue_field = 'Value'
buffer_radius = 0 # This is somehing to consider. Right now the model trains untill the very edge of the tiles
in_mask_polygons = "Y:/William/DeepLearning/DitchnetProduction/Digitaliserade_rutor_20191202/testing.shp" # only data within these polygons will be exported. This is to avoid exporting large areas of no data.
rotation_angle = 0
reference_system = "MAP_SPACE"
processing_mode = "PROCESS_AS_MOSAICKED_IMAGE"
blacken_around_feature = ""
crop_mode = ""

# Execute
print('exporting testingdata north')
ExportTrainingDataForDeepLearning(inRaster, out_folder_testing, in_training,
    image_chip_format,tile_size_x, tile_size_y, stride_x,
    stride_y,output_nofeature_tiles, metadata_format, start_index,
    classvalue_field, buffer_radius, in_mask_polygons, rotation_angle,
    reference_system, processing_mode, blacken_around_feature, crop_mode)


# This is the south
inRaster = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/Processing/Geodatabases05m/HPMF.gdb/MosaicHPMF'
#This is the labels
in_training = 'D:/AI/Exported05mLabels/ExtentSouth.tif'

# The data will be split by 80 % training and 20 % testing. The training data have overlapping tiles to augment more data. The testing data do not have any overlap.
out_folder_training = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/TrainingData/HighPassMedianFilter3mDEM05mNonoverlapping/SouthTrainingTiles3'
out_folder_testing = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/TrainingData/HighPassMedianFilter3mDEM05m/SouthTestingTiles3'

#training lidar
trainingtiles = "Y:/William/DeepLearning/DitchnetProduction/Digitaliserade_rutor_20191202/training.shp"
testingtiles = "Y:/William/DeepLearning/DitchnetProduction/Digitaliserade_rutor_20191202/testing.shp"
# split input lidar squares into 80 % traning and 20 % testing
size_of_training_dataset = "80"
subsizeUnits = "PERCENTAGE_OF_INPUT"
# Execute SubsetFeatures
arcpy.SubsetFeatures_ga(lidarsquares, trainingtiles, testingtiles,trainData, subsizeUnits)


# Export training data
image_chip_format = "TIFF"
tile_size_x = "512"
tile_size_y = "512"
stride_x= "512" # Stride means that the tiles will have overlap in both x and y directions
stride_y= "512"
output_nofeature_tiles= "ONLY_TILES_WITH_FEATURES"
metadata_format= "Classified_Tiles"
start_index = 0
classvalue_field = 'Value'
buffer_radius = 0 # This is somehing to consider. Right now the model trains untill the very edge of the tiles
in_mask_polygons = "Y:/William/DeepLearning/DitchnetProduction/Digitaliserade_rutor_20191202/training.shp" # only data within these polygons will be exported. This is to avoid exporting large areas of no data.
rotation_angle = 0 # a rotation of 90 degrees will be applied to the training data
reference_system = "MAP_SPACE"
processing_mode = "PROCESS_AS_MOSAICKED_IMAGE"
blacken_around_feature = ""
crop_mode = ""

print('exporting training south')
# Execute
ExportTrainingDataForDeepLearning(inRaster, out_folder_training, in_training,
    image_chip_format,tile_size_x, tile_size_y, stride_x,
    stride_y,output_nofeature_tiles, metadata_format, start_index,
    classvalue_field, buffer_radius, in_mask_polygons, rotation_angle,
    reference_system, processing_mode, blacken_around_feature, crop_mode)

#Export testing data
# note that the test data is not being rotaded and there is no overlap.
image_chip_format = "TIFF"
tile_size_x = "512"
tile_size_y = "512"
stride_x= "512" # Stride means that the tiles will have overlap in both x and y directions
stride_y= "512"
output_nofeature_tiles= "ONLY_TILES_WITH_FEATURES"
metadata_format= "Classified_Tiles"
start_index = 0
classvalue_field = 'Value'
buffer_radius = 0 # This is somehing to consider. Right now the model trains untill the very edge of the tiles
in_mask_polygons = "Y:/William/DeepLearning/DitchnetProduction/Digitaliserade_rutor_20191202/testing.shp" # only data within these polygons will be exported. This is to avoid exporting large areas of no data.
rotation_angle = 0
reference_system = "MAP_SPACE"
processing_mode = "PROCESS_AS_MOSAICKED_IMAGE"
blacken_around_feature = ""
crop_mode = ""

# Execute
print('exporting testingdata south')
ExportTrainingDataForDeepLearning(inRaster, out_folder_testing, in_training,
    image_chip_format,tile_size_x, tile_size_y, stride_x,
    stride_y,output_nofeature_tiles, metadata_format, start_index,
    classvalue_field, buffer_radius, in_mask_polygons, rotation_angle,
    reference_system, processing_mode, blacken_around_feature, crop_mode)



print('rename north')
north_images_training = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/TrainingData/HighPassMedianFilter3mDEM05mNonoverlapping/NorthTrainingTiles3/images'
north_labels_training = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/TrainingData/HighPassMedianFilter3mDEM05mNonoverlapping/NorthTrainingTiles3/labels'
# north_images_testing = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/TrainingData/HighPassMedianFilter3mDEM05mNonoverlapping/NorthTestingTiles3/images'
# north_labels_testing = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/TrainingData/HighPassMedianFilter3mDEM05mNonoverlapping/NorthTestingTiles3/labels'
util.Functions.rename_images(north_images_training, 'north')
util.Functions.rename_images(north_labels_training, 'north')
util.Functions.rename_images(north_images_testing, 'north')
util.Functions.rename_images(north_labels_testing, 'north')

print('rename center')
center_images_training = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/TrainingData/HighPassMedianFilter3mDEM05mNonoverlapping/centerTrainingTiles3/images'
center_labels_training = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/TrainingData/HighPassMedianFilter3mDEM05mNonoverlapping/centerTrainingTiles3/labels'
center_images_testing = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/TrainingData/HighPassMedianFilter3mDEM05mNonoverlapping/centerTestingTiles3/images'
center_labels_testing = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/TrainingData/HighPassMedianFilter3mDEM05mNonoverlapping/centerTestingTiles3/labels'
util.Functions.rename_images(center_images_training, 'center')
util.Functions.rename_images(center_labels_training, 'center')
util.Functions.rename_images(center_images_testing, 'center')
util.Functions.rename_images(center_labels_testing, 'center')

print('rename south')
south_images_training = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/TrainingData/HighPassMedianFilter3mDEM05mNonoverlapping/southTrainingTiles3/images'
south_labels_training = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/TrainingData/HighPassMedianFilter3mDEM05mNonoverlapping/southTrainingTiles3/labels'
south_images_testing = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/TrainingData/HighPassMedianFilter3mDEM05mNonoverlapping/southTestingTiles3/images'
south_labels_testing = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/TrainingData/HighPassMedianFilter3mDEM05mNonoverlapping/southTestingTiles3/labels'
util.Functions.rename_images(south_images_training, 'south')
util.Functions.rename_images(south_labels_training, 'south')
util.Functions.rename_images(south_images_testing, 'south')
util.Functions.rename_images(south_labels_testing, 'south')

# rexport south training


# move all training images to one folder
combined_images_training = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/TrainingData/HighPassMedianFilter3mDEM05mNonoverlapping/CombinedTraining/images'
combained_labels_training = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/TrainingData/HighPassMedianFilter3mDEM05mNonoverlapping/CombinedTraining/labels'
combined_images_testing = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/TrainingData/HighPassMedianFilter3mDEM05mNonoverlapping/CombinedTesting/images'
combined_labels_testing = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/TrainingData/HighPassMedianFilter3mDEM05mNonoverlapping/CombinedTesting/labels'

print('move north')
util.Functions.copy_data(north_images_training, combined_images_training)
util.Functions.copy_data(north_labels_training, combained_labels_training)
util.Functions.copy_data(north_images_testing, combined_images_testing)
util.Functions.copy_data(north_labels_testing, combined_labels_testing)

print('move center')
util.Functions.copy_data(center_images_training, combined_images_training)
util.Functions.copy_data(center_labels_training, combained_labels_training)
util.Functions.copy_data(center_images_testing, combined_images_testing)
util.Functions.copy_data(center_labels_testing, combined_labels_testing)

print('move south')
util.Functions.copy_data(south_images_training, combined_images_training)
util.Functions.copy_data(south_labels_training, combained_labels_training)
util.Functions.copy_data(south_images_testing, combined_images_testing)
util.Functions.copy_data(south_labels_testing, combined_labels_testing)

# delete tiles with less than 262 ditch pixels to combat class imbalance
combined_images_training = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/TrainingData/HighPassMedianFilter3mDEM05mNonoverlapping/CombinedTraining/images/'
combained_labels_training = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/TrainingData/HighPassMedianFilter3mDEM05mNonoverlapping/CombinedTraining/labels/'
combined_images_testing = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/TrainingData/HighPassMedianFilter3mDEM05mNonoverlapping/CombinedTesting/images/'
combined_labels_testing = 'Y:/William/DeepLearning/DitchnetProduction/HalfMeterDEM/TrainingData/HighPassMedianFilter3mDEM05mNonoverlapping/CombinedTesting/labels/'

print('Delete no-ditch chips')
util.Functions.Delete_tiles(combined_images_training, combained_labels_training, 262) #262 is 0.01 % of a 512 x 512 image chip
util.Functions.Delete_tiles(combined_images_testing, combined_labels_testing, 262)
