from model import *
from data import *

#os.environ["CUDA_VISIBLE_DEVICES"] = "0"

# Class = 0 is non-ditch
# Class = 1 is ditch
class_weight_ditch = {0: 1.,
                1: 160.,
                2: 0.,
                3: 0.}

data_gen_args = dict(rotation_range=0.0,
                    width_shift_range=0.05,
                    height_shift_range=0.05,
                    shear_range=0.05,
                    zoom_range=0.05,
                    horizontal_flip=True,
                    fill_mode='nearest')
myGene = trainGenerator(2,'/tmp/data/train','images','labels',data_gen_args,save_to_dir = None)

model = unet()
model_checkpoint = ModelCheckpoint('unet_ditch.hdf5', monitor='loss',verbose=1, save_best_only=True, save_weights_only=True)
model.fit_generator(myGene,steps_per_epoch=40,epochs=1, callbacks=[model_checkpoint])

#testGene = testGenerator("/tmp/data/test/images")
#results = model.predict_generator(testGene,5,verbose=1)
#saveResult("/tmp/data/test/images",results)