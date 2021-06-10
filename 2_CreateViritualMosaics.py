import os
import sys
import arcpy
from arcpy.sa import *
from arcpy import env

sys.path.insert(1, 'Y:/William/Skogsstyrelsen/dataprocessing/DitchNet/Preprocessing/util/WBT/')
from whitebox_tools import WhiteboxTools
whitebox_dir = os.path.dirname('Y:/William/Skogsstyrelsen/dataprocessing/DitchNet/Preprocessing/util/WBT/')
whitebox = WhiteboxTools()
whitebox.set_whitebox_dir(whitebox_dir)

arcpy.env.compression = "NONE"
arcpy.env.pyramid = "NONE"
arcpy.env.overwriteOutput = True
arcpy.env.parallelProcessingFactor = "0%"

HPMF = 'Y:/William/Skogsstyrelsen/dataprocessing/DitchNet/HighPassMedianFilter/'
OR = 'Y:/William/Skogsstyrelsen/dataprocessing/DitchNet/OR/' #

print('Create a file geodatabase')
#arcpy.CreateFileGDB_management('Y:/William/Skogsstyrelsen/dataprocessing/DitchNet/databases', 'HPMF.gdb')

# Create a ampty raster dataset within the geodatabase
mdnameLabel = 'HPMF' #name of raster dataset
gdbname = 'Y:/William/Skogsstyrelsen/dataprocessing/DitchNet/databases/HPMF.gdb'
mdname = "MosaicHPMF"
prjfile = "PROJCS['SWEREF99_TM',GEOGCS['GCS_SWEREF99',DATUM['D_SWEREF99',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',15.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]"
noband = "1"
pixtype = '32_BIT_FLOAT'
pdef = "NONE"
wavelength = ""

# Create empty dataset
print('Creating empty dataset for hpmf')
#arcpy.CreateMosaicDataset_management(gdbname, mdname, prjfile, noband, pixtype, pdef, wavelength)

mdname = "Y:/William/Skogsstyrelsen/dataprocessing/DitchNet/databases/HPMF.gdb/MosaicHPMF"
rastype = "Raster Dataset"
inpath = HPMF
print('Adding HPMF tiles to dataset')
#arcpy.AddRastersToMosaicDataset_management(mdname,  rastype, inpath)


#Labels
print('creating geodatabase for labels')
#arcpy.CreateFileGDB_management('Y:/William/Skogsstyrelsen/dataprocessing/DitchNet/databases', 'Labels.gdb')
mdnameLabel = "Labels"
gdbname = "Y:/William/Skogsstyrelsen/dataprocessing/DitchNet/databases/Labels.gdb"
mdname = "MosaicLabels1m"
prjfile = "PROJCS['SWEREF99_TM',GEOGCS['GCS_SWEREF99',DATUM['D_SWEREF99',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',15.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]"
noband = "1"
pixtype = "8_BIT_UNSIGNED"
pdef = "NONE"
wavelength = ""
print('Creating a ampty raster dataset within the geodatabase')
arcpy.CreateMosaicDataset_management(gdbname, mdname, prjfile, noband,pixtype, pdef, wavelength)

mdname = "Y:/William/Skogsstyrelsen/dataprocessing/DitchNet/databases/Labels.gdb/MosaicLabels1m"
rastype = "Raster Dataset"
inpath = OR #Binary labels
print('Adding Binary labels to dataset')
arcpy.AddRastersToMosaicDataset_management(mdname,  rastype, inpath)

# transform the data to 8 bit thematic raster and create a attribute table which is required for the export training data for deep learning tool.
out8bit = 'Y:/William/Skogsstyrelsen/dataprocessing/DitchNet/Exported8bitlabels/LabelsMosaic1m.tif'
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
print('Done')
