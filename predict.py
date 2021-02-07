from model import *
from data import *

#os.environ["CUDA_VISIBLE_DEVICES"] = "0"

model = unet("unet_ditch.hdf5")

testGene = testGenerator("/tmp/data/images")
results = model.predict_generator(testGene,100,verbose=1)
saveResult("/tmp/data/images",results)