# implementation adapted from:
# https://keras.io/examples/vision/oxford_pets_image_segmentation/

from tensorflow import keras
from tensorflow.keras import layers

from crfrnn_layer import CrfRnnLayer # don't forget to add this to path: export PYTHONPATH=/home/william/Downloads/crfasrnn_keras-master/src/:$PYTHONPATH


class XceptionUNet(object):

    def __init__(self, input_shape, depth=None, activation='softmax'):
        self.input_shape = input_shape

        depth = 2 if depth is None else depth
        self.activation = activation
        self.classes = 2
        self.__set_depth(depth)
        self.model = self.__setup_model()

    def __set_depth(self, depth):
        #self.down_sample = [2**i for i in range(6, 6+depth)]
        self.down_sample = [2**i for i in range(7, 7+depth)]
        #self.down_sample = [2**i for i in range(8, 8+depth)]
        # for deeper networks, reduce number of kernels to fit model into GPU
        # memory
        if depth == 3:
            self.down_sample[2] = self.down_sample[2] // 2
        self.up_sample = self.down_sample.copy()
        self.up_sample.reverse()
        self.up_sample.append(32)

    def __setup_model(self):
        inputs = keras.Input(shape=self.input_shape)

        # -- [First half of the network: downsampling inputs] -- #

        # Entry block
        x = layers.Conv2D(32, 3, strides=2, padding="same")(inputs)
        x = layers.BatchNormalization()(x)
        x = layers.Activation("relu")(x)

        previous_block_activation = x  # Set aside residual

        # Blocks 1, 2, 3 are identical apart from the feature depth.
        for filters in self.down_sample:
            x = layers.Activation("relu")(x)
            x = layers.SeparableConv2D(filters, 3, padding="same")(x)
            x = layers.BatchNormalization()(x)

            x = layers.Activation("relu")(x)
            x = layers.SeparableConv2D(filters, 3, padding="same")(x)
            x = layers.BatchNormalization()(x)

            x = layers.MaxPooling2D(3, strides=2, padding="same")(x)

            # Project residual
            residual = layers.Conv2D(filters, 1, strides=2, padding="same")(
                previous_block_activation
            )
            x = layers.add([x, residual])  # Add back residual
            previous_block_activation = x  # Set aside next residual

        # -- [Second half of the network: upsampling inputs] -- #

        for filters in self.up_sample:
            x = layers.Activation("relu")(x)
            x = layers.Conv2DTranspose(filters, 3, padding="same")(x)
            x = layers.BatchNormalization()(x)

            x = layers.Activation("relu")(x)
            x = layers.Conv2DTranspose(filters, 3, padding="same")(x)
            x = layers.BatchNormalization()(x)

            x = layers.UpSampling2D(2)(x)

            # Project residual
            residual = layers.UpSampling2D(2)(previous_block_activation)
            residual = layers.Conv2D(filters, 1, padding="same")(residual)
            x = layers.add([x, residual])  # Add back residual
            previous_block_activation = x  # Set aside next residual

        # Add a per-pixel classification layer
        # outputs = layers.Conv2D(self.num_classes, 3, activation="softmax",
        #                        padding="same")(x)
        outputs = layers.Conv2D(self.classes, 3, activation=self.activation,
                                padding="same")(x)
        # reshape to make loss weighting possible
        outputs = layers.Reshape((-1, self.classes))(outputs)

        # Define the model
        model = keras.Model(inputs, outputs)
        return model


class XceptionUNetCRF(XceptionUNet):

    def __init__(self, input_shape, model_path=None, iterations=10):
        super().__init__(input_shape, activation=None)
        if model_path is not None:
            self.model.load_weights(model_path)
        self.iterations = iterations
        self.crf_model = self.__setup_crf_model()

    def __setup_crf_model(self):
        self.model.trainable = False

        outputs = layers.Reshape((self.input_shape[0],
                                  self.input_shape[1],
                                  self.classes))(self.model.outputs[0])
        # create fake RGB image
        inputs = layers.concatenate([self.model.inputs[0],
                                     self.model.inputs[0],
                                     self.model.inputs[0]], axis=3)
        crf_layer = CrfRnnLayer(image_dims=self.input_shape[:-1],
                                num_classes=self.classes,
                                theta_alpha=3.,
                                theta_beta=160.,
                                theta_gamma=3.,
                                num_iterations=self.iterations,
                                name='crfrnn')([outputs,
                                               inputs])
        # reshape to make loss weighting possible
        outputs = layers.Reshape((-1, self.classes))(crf_layer)
        # apply softmax
        outputs = layers.Softmax()(outputs)

        model = keras.Model(inputs=self.model.input,
                            outputs=outputs)
        return model


class UNet(object):

    def __init__(self, input_shape, depth=None):
        self.input_shape = input_shape

        depth = 4 if depth is None else depth
        self.__set_depth(depth)
        self.model = self.__setup_model()

    def __set_depth(self, depth):
        self.down_sample = [2**i for i in range(6, 6+depth)]
        #self.down_sample = [2**i for i in range(7, 7+depth)]
        #self.down_sample = [2**i for i in range(8, 8+depth)]
        self.up_sample = self.down_sample.copy()
        self.up_sample.reverse()

    def __setup_model(self):
        conv_layers = []
        inputs = keras.Input(self.input_shape)

        x = inputs
        # Down sampling
        for i, size in enumerate(self.down_sample):
            conv1 = layers.Conv2D(size, 3, activation='relu', padding='same',
                                  kernel_initializer='he_normal')(x)
            conv1 = layers.Conv2D(size, 3, activation='relu', padding='same',
                                  kernel_initializer='he_normal')(conv1)
            conv_layers.append(conv1)
            if i == (len(self.down_sample) - 1):
                conv1 = layers.Dropout(0.5)(conv1)
            x = layers.MaxPooling2D(pool_size=(2, 2))(conv1)

        # Middle
        size = self.down_sample[-1] * 2
        conv5 = layers.Conv2D(size, 3, activation='relu', padding='same',
                              kernel_initializer='he_normal')(x)
        conv5 = layers.Conv2D(size, 3, activation='relu', padding='same',
                              kernel_initializer='he_normal')(conv5)
        x = layers.Dropout(0.5)(conv5)

        # Up sampling
        for i, size in enumerate(self.up_sample):
            up6 = (layers.Conv2D(size, 2, activation='relu', padding='same',
                                 kernel_initializer='he_normal')
                   (layers.UpSampling2D(size=(2, 2))(x)))

            merge6 = layers.concatenate([conv_layers.pop(), up6], axis=3)
            conv6 = layers.Conv2D(size, 3, activation='relu', padding='same',
                                  kernel_initializer='he_normal')(merge6)
            x = layers.Conv2D(size, 3, activation='relu', padding='same',
                              kernel_initializer='he_normal')(conv6)

        conv9 = layers.Conv2D(2, 3, activation='relu', padding='same',
                              kernel_initializer='he_normal')(x)
        conv10 = layers.Conv2D(1, 1, activation='sigmoid')(conv9)

        model = keras.Model(inputs=inputs, outputs=conv10)
        return model
