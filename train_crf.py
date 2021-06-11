import utils.generator
import utils.unet

import os
import tensorflow as tf


def main(img_path, gt_path, model_path, log_path, train_imgs, seed, epochs,
         steps_per_epoch):

    train_gen = utils.generator.DataGenerator(img_path, gt_path, seed=seed,
                                              include=train_imgs,
                                              steps_per_epoch=steps_per_epoch,
                                              augment=True,
                                              zero_class_weight=0.1)
    valid_gen = utils.generator.DataGenerator(img_path, gt_path, seed=seed,
                                              exclude=train_gen.selected,
                                              steps_per_epoch=steps_per_epoch,
                                              augment=False)

    crf_unet = utils.unet.XceptionUNetCRF(train_gen.input_shape, model_path,
                                          iterations=5)
    crf_unet.crf_model.compile(
                       # optimizer="rmsprop",
                       # optimizer="adam",
                       optimizer=tf.keras.optimizers.SGD(momentum=0.99,
                                                         learning_rate=1e-13),
                       # loss=jaccard_distance_loss,
                       # loss='binary_crossentropy',
                       # loss='categorical_crossentropy',
                       # loss=util.loss.cross_entropy,
                       loss='categorical_crossentropy',
                       sample_weight_mode="temporal",
                       metrics=['accuracy', tf.keras.metrics.Recall()])
    # tf.keras.metrics.MeanIoU(num_classes=2)])
    # utils.metric.f1_m, util.metric.recall_m])
    # "categorical_crossentropy")

    callbacks = [
        # tf.keras.callbacks.EarlyStopping(monitor='loss', patience=10,
        #                                  mode='min'),
        tf.keras.callbacks.ReduceLROnPlateau(monitor='loss', patience=10,
                                             min_lr=1e-16, mode='min'),
        tf.keras.callbacks.ModelCheckpoint(os.path.join(log_path, 'test.h5'),
                                           monitor='loss',
                                           save_weights_only=True,
                                           verbose=0, save_best_only=True),
        # tf.keras.callbacks.TensorBoard(log_dir=log_path, histogram_freq=5,
        #                                write_grads=True, batch_size=4,
        #                                write_images=True)
        tf.keras.callbacks.CSVLogger(os.path.join(log_path, 'log.csv'),
                                     append=True, separator=';')
    ]

    crf_unet.crf_model.fit_generator(train_gen, epochs=epochs, verbose=0,
                                     callbacks=callbacks,
                                     validation_data=valid_gen)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Train CRF Model')
    parser.add_argument('img_path')
    parser.add_argument('gt_path')
    parser.add_argument('model_path')
    parser.add_argument('log_path')
    parser.add_argument('train_imgs', help='TXT file with selected training '
                        'image ids')
    parser.add_argument('--seed', help='Random seed', default=None, type=int)
    parser.add_argument('--epochs', default=100, type=int)
    parser.add_argument('--steps_per_epoch', default=None, type=int)

    args = vars(parser.parse_args())
    main(**args)
