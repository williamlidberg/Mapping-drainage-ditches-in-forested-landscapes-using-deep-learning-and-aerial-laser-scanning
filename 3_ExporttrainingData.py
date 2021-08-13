# This is the south
import arcpy, os
arcpy.CheckOutExtension("ImageAnalyst")
from arcpy.ia import *
arcpy.env.compression = "NONE"
arcpy.env.pyramid = "NONE"
arcpy.env.overwriteOutput = True
# These are the high HighPassMedianFilter
inRaster = 'Y:/William/Skogsstyrelsen/dataprocessing/DitchNet/databases/Labels.gdb/MosaicLabels1m'
#This are the labels
in_training = 'Y:/William/Skogsstyrelsen/dataprocessing/DitchNet/Exported8bitlabels/LabelsMosaic1m.tif'
# areas where training data will be exported from
trainingtiles = "Y:/William/DeepLearning/DitchnetProduction/Digitaliserade_rutor_20191202/Digitaliserade_rutor_20191202.shp"
# These are the image chips used for training
out_folder_training = 'Y:/William/Skogsstyrelsen/dataprocessing/DitchNet/TrainingData/exported'

# Export training data
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
in_mask_polygons = 'Y:/William/DeepLearning/DitchnetProduction/Digitaliserade_rutor_20191202/Digitaliserade_rutor_20191202.shp' # only data within these polygons will be exported. This is to avoid exporting large areas of no data.
rotation_angle = 0 # a rotation of 90 degrees will be applied to the training data
reference_system = "MAP_SPACE"
processing_mode = "PROCESS_AS_MOSAICKED_IMAGE"
blacken_around_feature = ""
crop_mode = ""

print('exporting training data')
# Execute
ExportTrainingDataForDeepLearning(inRaster, out_folder_training, in_training,
    image_chip_format,tile_size_x, tile_size_y, stride_x,
    stride_y,output_nofeature_tiles, metadata_format, start_index,
    classvalue_field, buffer_radius, in_mask_polygons, rotation_angle,
    reference_system, processing_mode, blacken_around_feature, crop_mode)
