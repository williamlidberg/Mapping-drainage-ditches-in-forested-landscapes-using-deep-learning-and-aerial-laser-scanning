from PIL import Image
#from ImportData import write_gtiff
import numpy
import tifffile as tiff

im_width = 512
im_height = 512
inputpath = "Y:/William/DeepLearning/UnetVersion2/unet/data/ExportedChips4/testdata/"
outputpath = 'Y:/William/DeepLearning/UnetVersion2/unet/data/temppreds/'
outputpathwithExtent = 'Y:/William/DeepLearning/UnetVersion2/unet/data/predictionswithextent/'
for file in os.listdir(inputpath):
    if file.endswith('.tif'):
        inputfile = inputpath + file
        outputfile = outputpath + file
        listofonefile = []
        listofonefile.append(inputfile)
        K = np.zeros((len(listofonefile), im_height, im_width, 1), dtype=np.float32)
        img = load_img(inputfile, color_mode='grayscale')
        x_img = img_to_array(img)
        x_img = resize(x_img, (512, 512, 1), mode = 'constant', preserve_range = True)
        K[:1] = x_img/255.0 # Original predictions are values between 0 and 1. Multiply it by 255 to get a 8 bit image or export as float.
        #print(len(K[:1]))
        predicted = model.predict(K[:1], batch_size=batchSize, verbose=1)
        tiff.imsave(outputfile, predicted.astype('uint8'))
        #copy extent from input file
        PredictedOutputWithExtent = outputpathwithExtent + file
        InutFileWithKnownExtent = gdal.Open(inputfile)
        OutputFileWithoutExtent = gdal.Open(outputfile)
        array1 = np.array(InutFileWithKnownExtent.GetRasterBand(1).ReadAsArray()) # convert file inputfile to array again
        array2 = np.array(OutputFileWithoutExtent.GetRasterBand(1).ReadAsArray()) # convert file outputfile to array again
        write_gtiff(array2, InutFileWithKnownExtent, PredictedOutputWithExtent) # save predicted file with extent of input file
