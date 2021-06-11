from tensorflow.keras import backend as K
from tensorflow.python.ops import math_ops


def cross_entropy(y_true, y_pred, weight=0.1):
    bce = y_true[:, :, 1] * math_ops.log(y_pred[:, :, 1] + 0.00001)
    bce2 = y_true[:, :, 0] * math_ops.log(y_pred[:, :, 0] + 0.00001)
    bce += weight * bce2
    return -K.sum(bce)


def jaccard_distance_loss(y_true, y_pred, smooth=100):
    """
    Jaccard = (|X & Y|)/ (|X|+ |Y| - |X & Y|)
            = sum(|A*B|)/(sum(|A|)+sum(|B|)-sum(|A*B|))

    The jaccard distance loss is usefull for unbalanced datasets. This has been
    shifted so it converges on 0 and is smoothed to avoid exploding or
    disapearing gradient.

    Ref: https://en.wikipedia.org/wiki/Jaccard_index

    @url: https://gist.github.com/wassname/f1452b748efcbeb4cb9b1d059dce6f96
    @author: wassname
    """
    intersection = K.sum(K.abs(y_true * y_pred), axis=-1)
    sum_ = K.sum(K.abs(y_true) + K.abs(y_pred), axis=-1)
    jac = (intersection + smooth) / (sum_ - intersection + smooth)
    return (1 - jac) * smooth
