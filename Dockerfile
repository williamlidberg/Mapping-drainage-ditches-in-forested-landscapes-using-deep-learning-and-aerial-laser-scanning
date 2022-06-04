# FROM mcr.microsoft.com/azureml/openmpi3.1.2-cuda10.1-cudnn7-ubuntu18.04:20210615.v1
# #FROM mcr.microsoft.com/azureml/openmpi3.1.2-cuda10.1-cudnn7-ubuntu18.04
# RUN echo "Custom container downloaded!"
# RUN apt-get -y update --fix-missing
# RUN apt-get -y install libopencv-highgui-dev ffmpeg libsm6 libxext6 software-properties-common
# COPY .  /bin
# RUN echo "files copied to container"

# # Install dependencis for gdal
# RUN add-apt-repository -y ppa:ubuntugis/ppa
# RUN apt-get update
# RUN apt-get -y install gdal-bin libgdal-dev

# RUN echo "Done installing packages in container!"

# RUN conda update -n base -c defaults conda
# RUN conda install -c anaconda opencv
# RUN conda install -c conda-forge tensorflow-gpu=1.15
# RUN conda install -c anaconda pillow
# RUN conda install -c conda-forge tifffile
# RUN conda install -c anaconda pandas
# RUN conda install -c conda-forge scikit-learn
# RUN conda install -c conda-forge imagecodecs

# ENV PYTHONPATH="/bin/utils/crfasrnn_keras-gpu_support/src:$PYTHONPATH"
# ENV LD_LIBRARY_PATH="/usr/local/cuda-10.1/targets/x86_64-linux/lib:/opt/miniconda/lib/python3.7/site-packages/tensorflow_core:/usr/local/nvidia/lib:/usr/local/nvidia/lib64:/usr/local/cuda/lib64:/usr/local/cuda/extras/CUPTI/lib64"
# ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
# ENV C_INCLUDE_PATH=/usr/include/gdal

# # Install gdal with pip
# RUN pip install GDAL==2.4.2
# RUN echo "Done installing conda packages in container!"

FROM nvcr.io/nvidia/tensorflow:20.12-tf2-py3

RUN echo "Custom container downloaded!"
RUN apt-get -y update --fix-missing
RUN apt-get -y install libopencv-highgui-dev ffmpeg libsm6 libxext6 software-properties-common
RUN pip install --upgrade pip

RUN pip install whitebox==2.0.3
RUN pip install pillow
RUN pip install opencv-python==4.5.5.64 
RUN pip install tifffile==2022.4.26
RUN pip install pandas==1.4.2 
RUN pip install scikit-learn==1.0.2
RUN pip install imagecodecs
RUN echo "Installed python packages!"

RUN add-apt-repository ppa:ubuntugis/ppa && apt-get update
RUN apt-get install gdal-bin -y
RUN apt-get install libgdal-dev -y
RUN export CPLUS_INCLUDE_PATH=/usr/include/gdal
RUN export C_INCLUDE_PATH=/usr/include/gdal
RUN pip install GDAL
RUN echo "Gdal installed!"

# set up CRF
ENV PYTHONPATH="/bin/utils/crfasrnn_keras-gpu_support/src:$PYTHONPATH"
ENV LD_LIBRARY_PATH="/usr/local/cuda-10.1/targets/x86_64-linux/lib:/opt/miniconda/lib/python3.7/site-packages/tensorflow_core:/usr/local/nvidia/lib:/usr/local/nvidia/lib64:/usr/local/cuda/lib64:/usr/local/cuda/extras/CUPTI/lib64"
