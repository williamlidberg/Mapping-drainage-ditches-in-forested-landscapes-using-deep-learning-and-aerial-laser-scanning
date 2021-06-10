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
sr = arcpy.SpatialReference(3006)

# Split vector lines based on raster tiles
#shapeditches = 'Y:/William/Skogsstyrelsen/dataprocessing/DitchNet/vectorditches/DitchesOutsideofKrycklan.shp' # shapefile with ditches
VectorDitches = 'Y:/William/Skogsstyrelsen/dataprocessing/DitchNet/clipped/' # Ditches split based on dem tiles
#VectorDitches = 'Y:/William/DeepLearning/Writing/supplementary/data/ditchlines/'
demtiles = 'Y:/William/Skogsstyrelsen/dataprocessing/DitchNet/TilesWithinAOI_Uncompressed/' # copied demtiles that intersect with study areas

HPMF = 'Y:/William/Skogsstyrelsen/dataprocessing/DitchNet/HighPassMedianFilter/'
RasterDitches = 'C:/Temp/RASTERDITCHES/'
ReclassifiedDitches = 'C:/Temp/ReclassifiedRASTERDITCHES/'
BufferRaster = 'C:/Temp/BufferRaster/'
ReclassHPMF = 'C:/Temp/ReclassHPMF/'
MultiplyStreamsWithBufferRaster = 'C:/Temp/MultiplyStreamsWithBufferRaster/'
SmoothStreamBuffer = 'C:/Temp/SmoothStreamBuffer/'
OR = 'Y:/William/Skogsstyrelsen/dataprocessing/DitchNet/OR/' #These are combined variable width labels with high pas smedian filter

# convert vector ditches to raster labels
for file in os.listdir(demtiles):
    if file.endswith('.tif'):

        # convert vectorditches to raster
        VectorditchFile = VectorDitches + file.replace('.tif', '.shp')
        RasterditchFile = RasterDitches + file
        ReclassifiedRasterDitches = ReclassifiedDitches + file
        DemFile = demtiles + file
        args_rasterditch = ['--input=' + VectorditchFile,'--field=' + "FID", '--output=' + RasterditchFile, '--base=' + DemFile]

        # reclassify raster ditches to 1 and 0
        reclassifiedditches = ReclassifiedDitches + file
        reclassvalues = '1.0;1;100000' #(new value; from value; to less than)
        reclassify_args = ['--input=' + RasterditchFile, '--output=' + reclassifiedditches, '--reclass_vals=' + reclassvalues]

        # High pass median filter
        DemFile = demtiles + file
        HighPassMedianFilter = HPMF + file
        args_HPMF = ['--input=' + DemFile, '--output=' + HighPassMedianFilter, '--filterx=5', '--filtery=5', '--sig_digits=2']

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
            #arcpy.DefineProjection_management(DemFile, sr)
            #arcpy.DefineProjection_management(VectorditchFile, sr)
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
