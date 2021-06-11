import cv2
import os
import numpy as np
import tifffile
from osgeo import gdal
import utils.unet
import utils.WriteGeotiff

def patchify_x(img, start_y, patches, tile_size, margin, width):
    start_x = 0
    while start_x + tile_size <= width:
        patches.append(img[start_y:start_y+tile_size,
                           start_x:start_x+tile_size].copy())
        start_x += tile_size - 2 * margin
        assert patches[-1].shape == (tile_size, tile_size),\
            'shape: {}'.format(patches[-1].shape)
    # handle right boarder
    if start_x < width:
        start_x = width - tile_size
        patches.append(img[start_y:start_y+tile_size,
                           start_x:start_x+tile_size].copy())
        assert patches[-1].shape == (tile_size, tile_size)


def patchify(img, tile_size, margin):
    patches = []

    height, width = img.shape
    start_y = 0
    while start_y + tile_size <= height:
        patchify_x(img, start_y, patches, tile_size, margin, width)
        start_y += tile_size - 2 * margin
    # handle bottom boarder
    if start_y < height:
        start_y = height - tile_size
        patchify_x(img, start_y, patches, tile_size, margin, width)

    return patches


def start_and_end(base, tile_size, margin, limit, remainder):
    if base == 0:
        src_start = 0
        src_end = tile_size - margin
    elif base + (tile_size - margin) > limit:
        src_start = tile_size - remainder
        src_end = tile_size
    else:
        src_start = margin
        src_end = tile_size - margin

    return src_start, src_end


def unpatchify(shape, patches, tile_size, margin):
    img = np.zeros(shape)
    height, width = shape
    remain_height = height % tile_size
    remain_width = width % tile_size

    dest_start_y = 0
    dest_start_x = 0

    for i, patch in enumerate(patches):
        remain_width = width - dest_start_x
        remain_height = height - dest_start_y
        src_start_y, src_end_y = start_and_end(dest_start_y, tile_size, margin,
                                               height, remain_height)
        src_start_x, src_end_x = start_and_end(dest_start_x, tile_size, margin,
                                               width, remain_width)
        y_length = src_end_y - src_start_y
        x_length = src_end_x - src_start_x
        img[dest_start_y:dest_start_y+y_length,
            dest_start_x:dest_start_x+x_length] = patch[src_start_y:src_end_y,
                                                        src_start_x:src_end_x]
        dest_start_x += x_length
        if dest_start_x >= width:
            dest_start_x = 0
            dest_start_y += y_length

    return img

#def main(input_path, model_path, out_path, img_type, tile_size, margin,
#         threshold, wo_crf):
def main(input_path, model_path, out_path_prob, out_path_binary, img_type, tile_size, margin,
         threshold, wo_crf):

    # setup paths
    if not os.path.exists(input_path):
        raise ValueError('Input path does not exist: {}'.format(input_path))
    if os.path.isdir(input_path):
        imgs = [os.path.join(input_path, f) for f in os.listdir(input_path)
                if f.endswith('.tif')]

    else:
        imgs = [input_path]

    # check tile size
    if not wo_crf:
        if tile_size != 512:
            print('WARNING: setting tile size to 512')
            tile_size = 512

    # load model
    input_shape = (tile_size, tile_size, 1)
    if wo_crf:
        unet = utils.unet.XceptionUNet(input_shape)
        unet.model.load_weights(model_path)
        model = unet.model
    else:
        unet = utils.unet.XceptionUNetCRF(input_shape, iterations=20)
        unet.crf_model.load_weights(model_path)
        model = unet.crf_model

    for img_path in imgs:
        predicted = []

        img = tifffile.imread(img_path)
        img = img.astype(np.float32)

        # we do not need to patchify image if image is too small to be split
        # into patches - assume that img width == img height
        do_patchify = True if tile_size < img.shape[0] else False

        if do_patchify:
            patches = patchify(img, tile_size, margin)
        else:
            patches = [img]

        if wo_crf:
            # find suitable batch size
            for i in [8, 4, 2, 1]:
                if len(patches) % i == 0:
                    bs = i
                    break
        else:
            # CRF can only deal with a batch size of 1
            bs = 1

        # perform prediction
        for i in range(0, len(patches), bs):
            batch = np.array(patches[i:i+bs])
            batch = batch.reshape((bs, *input_shape))
            out = model.predict(batch)
            for o in out:
                # get only ditch channel
                o = o[:, 1]
                predicted.append(o.reshape(input_shape[:-1]))

        if do_patchify:
            out = unpatchify(img.shape, predicted, tile_size, margin)
        else:
            out = predicted[0]
        out[out < threshold] = 0

        # write image
        img_name = os.path.basename(img_path).split('.')[0]
        InutFileWithKnownExtent = gdal.Open(img_path)
        utils.WriteGeotiff.write_gtiff(out*100, InutFileWithKnownExtent, os.path.join(out_path_prob,'{}.{}'.format(img_name, img_type)))
        utils.WriteGeotiff.write_gtiff((np.round(out)), InutFileWithKnownExtent, os.path.join(out_path_binary,'{}.{}'.format(img_name, img_type)))
        #cv2.imwrite(os.path.join(out_path,'{}.{}'.format(img_name, img_type)), out)



if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
                       description='Run inference on given '
                                   'image(s)',
                       formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('input_path', help='Path to image or folder')
    parser.add_argument('model_path')
    parser.add_argument('out_path_prob', help='Path to output probability folder')
    parser.add_argument('out_path_binary', help='Path to output binary folder')
    parser.add_argument('--img_type', help='Output image file ending',
                        default='tif')
    # parser.add_argument('--tile_size', help='Tile size', type=int,
    #                     default=512)
    parser.add_argument('--tile_size', help='Tile size', type=int,
                        default=512)
    parser.add_argument('--margin', help='Margin', type=int, default=100)
    parser.add_argument('--threshold', help='Decision threshold', type=float,
                        default=0.5)
    parser.add_argument('--wo_crf', action='store_true')

    args = vars(parser.parse_args())
    main(**args)
