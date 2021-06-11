import tensorflow as tf
import cv2
import numpy as np
import os
import tifffile


class DataGenerator(tf.keras.utils.Sequence):
    def __init__(self, img_path, gt_path, batch_size=1, augment=True,
                 steps_per_epoch=None, seed=None, size=None, include=None,
                 exclude=None, zero_class_weight=None):
        # Either size, include or exclude must be specified
        assert ((size is None and include is None and exclude is not None)
                or (size is not None and include is None and exclude is None)
                or (size is None and include is not None and exclude is None))
        self.batch_size = batch_size
        self.augment = augment
        self.zero_class_weight = zero_class_weight
        self.steps_per_epoch = steps_per_epoch
        self.paths = self.__read_paths(img_path, gt_path)
        self.input_shape = self.__get_input_shape(self.paths)
        self.rng = np.random.default_rng(seed)
        self.selected = self.__select_imgs(self.paths, size, include, exclude,
                                           self.rng)

        self.on_epoch_end()

    def __get_input_shape(self, paths):
        # assume all images have the same shape
        # img = cv2.imread(paths[0][0])
        img = tifffile.imread(paths[0][0])
        print(paths[0][0])
        return (img.shape[0], img.shape[1], 1)

    def __select_imgs(self, paths, size, include, exclude, rng):
        if size is not None:
            tmp = np.arange(len(paths))
            rng.shuffle(tmp)
            size = int(np.round(size * len(paths)))
            selected = tmp[:size]
        elif include is not None:
            with open(include, 'r') as f:
                selected = []
                for line in f:
                    selected.append(int(line))
        else:
            selected = [f for f in range(len(paths)) if f not in exclude]

        return selected

    def __read_paths(self, img_path, gt_path):
        paths = []
        imgs = [os.path.join(img_path, f) for f in os.listdir(img_path)
                if not f.startswith('._') and f.endswith('.tif')]
        imgs = sorted(imgs)
        gts = [os.path.join(gt_path, f) for f in os.listdir(gt_path)
               if not f.startswith('._') and f.endswith('.tif')]
        gts = sorted(gts)

        for img, gt in zip(imgs, gts):
            img_base = os.path.basename(img)
            gt_base = os.path.basename(gt)
            msg = 'Name mismatch {} - {}'.format(img_base, gt_base)
            assert img_base == gt_base, msg

            paths.append((img, gt))

        return paths

    def __len__(self):
        if self.steps_per_epoch is None:
            length = len(self.index) // self.batch_size
        else:
            length = self.steps_per_epoch
        return length

    def __getitem__(self, index):
        index = self.index[index * self.batch_size:
                           (index + 1) * self.batch_size]
        batch = [self.paths[k] for k in index]

        return self.__get_data(batch)

    def on_epoch_end(self):
        print('New Epoch')
        self.index = self.selected.copy()
        self.rng.shuffle(self.index)

    def __get_data(self, batch):
        X = []
        y = []
        weights = []

        for img_path, gt_path in batch:
            # img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            img = tifffile.imread(img_path)
            # gt = cv2.imread(gt_path, cv2.IMREAD_GRAYSCALE)
            gt = tifffile.imread(gt_path)

            if self.augment:
                #select = self.rng.integers(0, 2, 3)
                select = self.rng.integers(0, 2, 2)
                if select[0]:
                    img, gt = self.create_rotation_augmentation(img, gt,
                                                                self.rng)
                if select[1]:
                    img, gt = self.create_flip_augmentation(img, gt, self.rng)
                # if select[2]:
                #     img, gt = self.create_affine_transform_augmentation(
                #                                                     img, gt,
                #                                                     self.rng)
            #
            # # img = img.astype(np.float32) / 255.
            img = img.astype(np.float32)
            X.append(img.reshape(self.input_shape))
            # y.append(gt.reshape(self.input_shape))
            gt_new = np.zeros(2 * gt.shape[0] *
                              gt.shape[1]).reshape((*gt.shape, 2))
            # non-ditch image
            gt_new[:, :, 0] = 1 - gt
            # ditch image
            gt_new[:, :, 1] = gt
            y.append(gt_new.reshape((-1, 2)))

            if self.zero_class_weight is not None:
                w = np.zeros(gt.shape[0] * gt.shape[1]).reshape(*gt.shape)
                w += gt + (1 - gt) * self.zero_class_weight
                weights.append(w.flatten())

        if self.zero_class_weight is None:
            return np.array(X), np.array(y)
        else:
            return np.array(X), np.array(y), np.array(weights)

    def create_flip_augmentation(self, img, gt, rng):
        select = rng.integers(0, 4)
        if select == 0:
            img = cv2.flip(img, 0)
            gt = cv2.flip(gt, 0)
        elif select == 1:
            img = cv2.flip(img, 1)
            gt = cv2.flip(gt, 1)
        elif select == 2:
            img = cv2.flip(img, -1)
            gt = cv2.flip(gt, -1)

        return img, gt

    def create_rotation_augmentation(self, img, gt, rng):
        angle = rng.integers(0, 360)
        center = np.array(img.shape) / 2
        transform_matrix = cv2.getRotationMatrix2D(tuple(center), angle, 1)

        return self.__warp_imgs(img, gt, transform_matrix)

    def __warp_imgs(self, img, gt, transform):
        y, x = img.shape[:2]

        borderValue = 0
        warped_img = cv2.warpAffine(img, transform, dsize=(x, y),
                                    borderValue=borderValue)
        warped_gt = cv2.warpAffine(gt, transform, dsize=(x, y),
                                   borderValue=borderValue)
        warped_gt = np.round(warped_gt)

        return warped_img, warped_gt

    def create_affine_transform_augmentation(self, img, gt, rng,
                                             random_limits=(0.8, 1.1)):
        '''
        Creates an augmentation by computing a homography from three
        points in the image to three randomly generated points
        Note: base implementation from PHOCNet
        '''
        assert img.shape[0] == gt.shape[0] and img.shape[1] == gt.shape[1]
        y, x = img.shape[:2]
        fx = float(x)
        fy = float(y)
        src_point = np.float32([[fx/2, fy/3, ],
                                [2*fx/3, 2*fy/3],
                                [fx/3, 2*fy/3]])
        random_shift = ((rng.random(6).reshape((3, 2)) - 0.5) * 2
                        * (random_limits[1]-random_limits[0])/2
                        + np.mean(random_limits))
        dst_point = src_point * random_shift.astype(np.float32)
        transform = cv2.getAffineTransform(src_point, dst_point)

        return self.__warp_imgs(img, gt, transform)
