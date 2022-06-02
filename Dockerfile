FROM mcr.microsoft.com/azureml/openmpi3.1.2-cuda10.1-cudnn7-ubuntu18.04:20210615.v1
#FROM mcr.microsoft.com/azureml/openmpi3.1.2-cuda10.1-cudnn7-ubuntu18.04
RUN echo "Custom container downloaded!"
RUN apt-get -y install wget

# Remove outdated Nvidia key, NVIDIA have updated their repository signing keys.
RUN apt-key del 7fa2af80
# Download new key package
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-keyring_1.0-1_all.deb

# Remove duplicate repository
RUN rm /etc/apt/sources.list.d/cuda.list*
RUN rm /etc/apt/sources.list.d/nvidia-ml.list*

# Install new keyring from NVIDIA
RUN dpkg -i cuda-keyring_1.0-1_all.deb

RUN apt-get -y update --fix-missing
RUN apt-get -y install libopencv-highgui-dev ffmpeg libsm6 libxext6 software-properties-common



# Install dependencis for gdal
RUN add-apt-repository -y ppa:ubuntugis/ppa
RUN apt-get update
RUN apt-get -y install gdal-bin libgdal-dev

RUN echo "Done installing packages in container!"

RUN conda update -n base -c defaults conda
RUN conda install -c anaconda opencv
RUN conda install -c conda-forge tensorflow-gpu=1.15
RUN conda install -c anaconda pillow
RUN conda install -c conda-forge tifffile
RUN conda install -c anaconda pandas
RUN conda install -c conda-forge scikit-learn
RUN conda install -c conda-forge imagecodecs
#RUN conda install -c conda-forge gdal

RUN apt-get install -y libgdal-dev g++ --no-install-recommends && \
    apt-get clean -y

COPY .  /bin
RUN echo "files copied to container"

ENV PYTHONPATH="/bin/utils/crfasrnn_keras-gpu_support/src:$PYTHONPATH"
ENV LD_LIBRARY_PATH="/usr/local/cuda-10.1/targets/x86_64-linux/lib:/opt/miniconda/lib/python3.7/site-packages/tensorflow_core:/usr/local/nvidia/lib:/usr/local/nvidia/lib64:/usr/local/cuda/lib64:/usr/local/cuda/extras/CUPTI/lib64"
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal


ENV export CPLUS_INCLUDE_PATH=/usr/include/gdal

ENV export C_INCLUDE_PATH=/usr/include/gdal


# Install gdal with pip
RUN pip install setuptools==57.5.0
RUN pip install GDAL==2.4.2

RUN pip install h5py==2.10.0

RUN mkdir /bin/probability
RUN mkdir /bin/classified
RUN echo "Done installing conda packages in container!"
