# import data using a function
import numpy as np
import os
import skimage
import keras
import skimage.io as io
import skimage.transform as trans
import numpy as np
from keras.models import *
from keras.layers import *
from keras.optimizers import *
from keras.callbacks import ModelCheckpoint, LearningRateScheduler
from keras import backend as keras
import tensorflow as tf
from keras import backend as K
from sklearn.utils import class_weight
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img
from skimage.transform import resize
from sklearn.model_selection import train_test_split
from keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import matplotlib.pyplot as plt
import tensorflow as tf
from PIL import Image
import tifffile
import pyrsgis
import numpy as np
import gdal, osr
import os
from Functions import get_images_from_path
# The size of the images loaded into the network.
im_width = 512
im_height = 512
border = 5 #whats this?
#ids = get_images_from_path("Y:/William/DeepLearning/UnetVersion2/unet/data/Smallerdataset-20210208T073759Z-001/Smallerdataset")
ids = get_images_from_path("Y:/William/DeepLearning/UnetVersion2/unet/data/ExportedChips4/images/")
ids.sort() #sort images on names
print('No. of images = ', len(ids))

# Reshape images
X = np.zeros((len(ids), im_height, im_width, 1), dtype=np.float32)
y = np.zeros((len(ids), im_height, im_width, 1), dtype=np.float32)

for n, fileName in enumerate(ids):
    if n < 10000:
        #print("Filename: ", fileName)
        # Load images
        img = load_img(fileName, color_mode='grayscale')
        x_img = img_to_array(img)
        x_img = resize(x_img, (512, 512, 1), mode = 'constant', preserve_range = True)
        # Load masks
        mask = img_to_array(load_img(fileName.replace('images', 'labels'), color_mode='grayscale'))
        mask = resize(mask, (512, 512, 1), mode = 'constant', preserve_range = True)

        # Save images
        X[n] = x_img/255.0

        # Here we are working on pixels 0-255.
        mask[mask == 1] = 1
        mask[mask == 0] = 0

        # Convert from 0-255 into 0.0-1.0
        y[n] = mask/255.0
y[1].shape

# Split data into training and testing
# Split train and valid
X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.1, random_state=42)
print('X_train length: ', len(X_train))
print('X_valid length: ', len(X_valid))

print('y_train length: ', len(y_train))
print('y_valid length: ', len(y_valid))

# set up custom loss Functions# Custom loss function
smooth = 1.

def dice_coef(y_true, y_pred):
    y_true_f = K.flatten(y_true)
    y_pred_f = K.flatten(y_pred)
    intersection = K.sum(y_true_f * y_pred_f)
    return (2. * intersection + smooth) / (K.sum(y_true_f) + K.sum(y_pred_f) + smooth)
def dice_coef_loss(y_true, y_pred):
    return 1 - dice_coef(y_true, y_pred)

#Run the model
# limit GPU memory
import tensorflow as tf
physical_devices = tf.config.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)

# model parameters
model = unet()

callbacks = [
    EarlyStopping(patience=10, verbose=1),
    ReduceLROnPlateau(factor=0.1, patience=5, min_lr=0.00001, verbose=1),
    ModelCheckpoint('unet_ditchsmalldataset.hdf5', monitor='loss', verbose=1, save_best_only=True, save_weights_only=True)
]

batchSize = 4
stpesPerEpoch = int(len(ids) / batchSize)
#stpesPerEpoch = 3727
#stpesPerEpoch = 500

results = model.fit(X_train, y_train, steps_per_epoch=stpesPerEpoch, batch_size=batchSize, epochs=20, callbacks=callbacks,\
                    validation_data=(X_valid, y_valid))

# save model
#model = 'unet_ditchsmalldataset.hdf5'
#model.save('Y:/William/DeepLearning/UnetVersion2/unet/SavedModels/LargeModel2/')
print("------------------ EVALUATION ---------------------")

# load the best model
model.load_weights('unet_ditchsmalldataset.hdf5')

# Evaluate on validation set (this must be equals to the best log_loss)
model.evaluate(X_valid, y_valid, batch_size=batchSize, verbose=1)

# Predict on train, val and test
preds_train = model.predict(X_train[:1], batch_size=batchSize, verbose=1)
preds_val = model.predict(X_valid[:1], batch_size=batchSize, verbose=1)
