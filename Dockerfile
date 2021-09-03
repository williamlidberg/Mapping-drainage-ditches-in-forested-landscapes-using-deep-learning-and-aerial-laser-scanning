# Build image
docker build --no-cache -t crfasrnn-gpu:latest .

# run image
nvidia-docker run -v /home/azureuser/cloudfiles/code/Users/:/mnt/ -it crfasrnn-gpu:latest bash

# Dockerfile
# Use a specific version from https://mcr.microsoft.com/v2/azureml/openmpi3.1.2-cuda10.1-cudnn7-ubuntu18.04/tags/list
FROM mcr.microsoft.com/azureml/openmpi3.1.2-cuda10.1-cudnn7-ubuntu18.04:20210615.v1
#FROM mcr.microsoft.com/azureml/openmpi3.1.2-cuda10.1-cudnn7-ubuntu18.04
RUN echo "Custom container downloaded!"
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

ENV PYTHONPATH="/mnt/OneMeterDem/WorkingLocalCRFsetup/crfasrnn_keras-gpu_support_cuda10/src:$PYTHONPATH"
ENV LD_LIBRARY_PATH="/usr/local/cuda-10.1/targets/x86_64-linux/lib:/opt/miniconda/lib/python3.7/site-packages/tensorflow_core:/usr/local/nvidia/lib:/usr/local/nvidia/lib64:/usr/local/cuda/lib64:/usr/local/cuda/extras/CUPTI/lib64"
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Install gdal with pip
RUN pip install GDAL==2.4.2
RUN echo "Done installing conda packages in container!"
