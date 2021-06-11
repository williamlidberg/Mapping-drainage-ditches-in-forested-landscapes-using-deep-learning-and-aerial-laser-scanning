import utils.generator
import utils.unet
import numpy as np
import pandas as pd
import sklearn.metrics


def evaluate(pred, gt):
    pred = np.round(pred).astype(int).flatten()
    gt = gt.flatten()

    fmes = sklearn.metrics.f1_score(gt, pred)
    acc = sklearn.metrics.accuracy_score(gt, pred)
    rec = sklearn.metrics.recall_score(gt, pred)
    cm = sklearn.metrics.confusion_matrix(gt, pred)
    jacc = sklearn.metrics.jaccard_score(gt, pred)
 
    return fmes, acc, rec, jacc, cm


def main(img_path, gt_path, selected_imgs, model_path, out_path, wo_crf, depth):
    valid_gen = utils.generator.DataGenerator(img_path, gt_path,
                                              include=selected_imgs,
                                              augment=False)
    if wo_crf:
        unet = utils.unet.XceptionUNet(valid_gen.input_shape, depth=depth)
        unet.model.load_weights(model_path)
        model = unet.model
    else:
        unet = utils.unet.XceptionUNetCRF(valid_gen.input_shape, iterations=20)
        unet.crf_model.load_weights(model_path)
        model = unet.crf_model

    results = {'fmes': [], 'acc': [], 'rec': [], 'cm': [], 'jacc': []}
    valid_it = iter(valid_gen)

    for img, gt in valid_it:
        out = model.predict(img)
        out = out[0, :, 1]  # .reshape(shape)
        gt = gt[0, :, 1]
        fmes, acc, rec, cm, jacc = evaluate(out, gt)
        results['fmes'].append(fmes)
        results['acc'].append(acc)
        results['rec'].append(rec)
        results['cm'].append(cm)
        results['jacc'].append(jacc)
        

    df = pd.DataFrame(results)
    df.to_csv(out_path, index=False)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
                       description='Evaluate model on given images',
                       formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('img_path', help='Path to image folder')
    parser.add_argument('gt_path')
    parser.add_argument('selected_imgs', help='Path to CSV file with '
                        'selected image indices')
    parser.add_argument('model_path')
    parser.add_argument('out_path', help='Path to output CSV file')
    parser.add_argument('--wo_crf', action='store_true')
    parser.add_argument('--depth', type=int, default=2)

    args = vars(parser.parse_args())
    main(**args)
