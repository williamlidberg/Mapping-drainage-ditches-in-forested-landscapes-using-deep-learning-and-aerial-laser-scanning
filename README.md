# Deep-unet-for-ditch-detection-from-lidar-data
This project aims to map small ditches from high resolution LiDAR data using deep learning

The PrepairDEMForPrediction.py script takes dem files as input and apply a feature preserv smoothing and then extracts a normalised high pass median filter. It also splits the input DEMs into smaller 512 x 512 tiles that can be used to predict ditches using the trained unet model.
