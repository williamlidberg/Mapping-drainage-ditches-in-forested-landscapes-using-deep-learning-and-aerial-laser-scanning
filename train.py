import utils.generator
import utils.unet
import utils.loss
import utils.metric
import tensorflow as tf

import os


UNETS = {'XceptionUNet': utils.unet.XceptionUNet,
         'UNet': utils.unet.UNet}


def write_dataset(selected, log_path, name):
    with open(os.path.join(log_path, name), 'w') as f:
        for path in selected:
            f.write('{}\n'.format(path))


def main(img_path, gt_path, log_path, unet, seed, epochs, depth,
         steps_per_epoch):
    train_gen = utils.generator.DataGenerator(img_path, gt_path, seed=seed,
                                              size=0.8,
                                              steps_per_epoch=steps_per_epoch,
                                              augment=True,
                                              zero_class_weight=0.1,
                                              batch_size=4)
    valid_gen = utils.generator.DataGenerator(img_path, gt_path, seed=seed,
                                              exclude=train_gen.selected,
                                              steps_per_epoch=steps_per_epoch,
                                              augment=False)

    write_dataset(train_gen.selected, log_path, 'train_imgs.txt')
    write_dataset(valid_gen.selected, log_path, 'valid_imgs.txt')

    unet = UNETS[unet](train_gen.input_shape, depth=depth)
    unet.model.compile(
                       # optimizer="rmsprop",
                       optimizer="adam",
                       # optimizer=tf.keras.optimizers.SGD(momentum=0.9),
                       # loss=jaccard_distance_loss,
                       # loss='binary_crossentropy',
                       loss='categorical_crossentropy',
                       sample_weight_mode="temporal",
                       # loss=utils.loss.cross_entropy,
                       metrics=['accuracy', tf.keras.metrics.Recall(),
                                tf.keras.metrics.MeanIoU(num_classes=2)
])
    # utils.metric.f1_m, utils.metric.recall_m])
    # "categorical_crossentropy")

    callbacks = [
        # tf.keras.callbacks.EarlyStopping(monitor='loss', patience=10,
        #                                  mode='min'),
        tf.keras.callbacks.ReduceLROnPlateau(monitor='loss', patience=10,
                                             min_lr=0.00001, mode='min'),
        tf.keras.callbacks.ModelCheckpoint(os.path.join(log_path, 'test.h5'),
                                           monitor='loss',
                                           save_weights_only=True,
                                           verbose=0, save_best_only=True),
        tf.keras.callbacks.TensorBoard(log_dir=log_path, histogram_freq=5,
                                       write_grads=True, batch_size=2,
                                       write_images=True),
        tf.keras.callbacks.CSVLogger(os.path.join(log_path, 'log.csv'),
                                     append=True, separator=';')
    ]
    unet.model.fit_generator(train_gen, epochs=epochs, verbose=0,
                             callbacks=callbacks,
                             validation_data=valid_gen)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Train Model')
    parser.add_argument('img_path')
    parser.add_argument('gt_path')
    parser.add_argument('log_path')
    parser.add_argument('unet', help='Choose UNet implementation',
                        choices=list(UNETS.keys()))
    parser.add_argument('--seed', help='Random seed', default=None, type=int)
    parser.add_argument('--depth', help='Depth of the used network',
                        default=None, type=int)
    parser.add_argument('--epochs', default=100, type=int)
    parser.add_argument('--steps_per_epoch', default=None, type=int)

    args = vars(parser.parse_args())
    main(**args)
