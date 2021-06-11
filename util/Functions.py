import os
import shutil
import arcpy
import numpy as np
import sys

sys.path.insert(1, 'Y:/Sidd/WBT/')
from whitebox_tools import WhiteboxTools
whitebox_dir = os.path.dirname('Y:/Sidd/WBT/')
whitebox = WhiteboxTools()
whitebox.set_whitebox_dir(whitebox_dir)


def rename_images(path, s):
    files = os.listdir(path)
    for index, file in enumerate(files):
        ext = '.' + file.split('.')[-1]
        os.rename(os.path.join(path, file), os.path.join(path, file.replace(ext, s + ext)))

def move_data(inputdir, outputdir):
    file_names = os.listdir(inputdir)
    for file_name in file_names:
        shutil.move(os.path.join(inputdir, file_name), outputdir)

def copy_data(inputdir, outputdir):
    file_names = os.listdir(inputdir)
    for file_name in file_names:
        shutil.copy(os.path.join(inputdir, file_name), outputdir)


def Delete_tiles(imagedirectory, labeldirectory, numpixels):
    for tile in os.listdir(labeldirectory):
        if tile.endswith('.tif'):
            # input data
            imagewithpath = imagedirectory + tile
            labelwithpath = labeldirectory + tile

            npArray = arcpy.RasterToNumPyArray(labelwithpath)
            npArray1 = np.ma.masked_array(npArray, np.isnan(npArray))
            tilesum = np.sum(npArray)
            if tilesum < numpixels:
                #ListofTilesWithoutDitches.append(labelwithpath)
                arcpy.Delete_management(imagewithpath)
                arcpy.Delete_management(labelwithpath)

# smooth all files in input directory
def smooth_labels(originallabel, smoothedlabel):
    for file in os.listdir(originallabel):
        if file.endswith('.tif'):
            DemFile = originallabel + file
            smooth = smoothedlabel + file
            args_smooth = ['--input=' + DemFile, '--output=' + smooth, '--filterx=3', '--filtery=3']

            try:
                whitebox.run_tool('MajorityFilter', args_smooth)
                print('MajorityFilter complete for: ' + file)
            except:
                print('Unexpected error:', sys.exc_info()[0])
