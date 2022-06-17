FROM nvcr.io/nvidia/tensorflow:22.04-tf1-py3

RUN echo "Custom container downloaded!"

RUN apt-get -y update --fix-missing
RUN apt-get -y install libopencv-highgui-dev ffmpeg libsm6 libxext6 software-properties-common
RUN echo "Done installing conda packages in container!"
# setup files
RUN mkdir /workspace/data
RUN mkdir /workspace/code
COPY .  /workspace/code
RUN echo "files copied to container"

# pip installations
RUN pip install --upgrade pip
RUN pip install whitebox==2.0.3
RUN pip install pillow
RUN pip install opencv-python==4.5.5.64
RUN pip install tifffile==2022.4.26
RUN pip install pandas==1.4.2
RUN pip install scikit-learn==1.0.2
RUN pip install imagecodecs
RUN echo "Installed python packages!"

# install GDAL
RUN add-apt-repository ppa:ubuntugis/ppa && apt-get update
#RUN apt-get install gdal-bin -y
RUN apt-get install -y libgdal-dev --no-install-recommends && \
     apt-get clean -y
#RUN apt-get install libgdal-dev -y
RUN export CPLUS_INCLUDE_PATH=/usr/include/gdal
RUN export C_INCLUDE_PATH=/usr/include/gdal
RUN pip install setuptools==57.5.0
RUN pip install GDAL==3.3.2
RUN pip install h5py==2.10.0
RUN echo "Gdal installed!"

# set up CRF
RUN ln -s /usr/local/lib/python3.8/dist-packages/tensorflow_core/libtensorflow_framework.so.1 /usr/local/lib/python3.8/dist-packages/tensorflow_core/libtensorflow_framework.so

WORKDIR /workspace/code/utils/crfasrnn_keras-gpu_support/src/cpp
RUN make clean
RUN make

WORKDIR /workspace/code/utils/crfasrnn_keras-master/src/cpp
RUN make clean
RUN make

WORKDIR /workspace/code

# set up environment variables
# this python path points to the CPU version of the CRF layer
#ENV PYTHONPATH="/workspace/code/utils/crfasrnn_keras-master/src:${PYTHONPATH}"
ENV PYTHONPATH="/workspace/code/utils/crfasrnn_keras-gpu_support/src:${PYTHONPATH}"
ENV LD_LIBRARY_PATH="/usr/local/lib/python3.8/dist-packages/tensorflow_core/:${LD_LIBRARY_PATH}"
ENV export CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV export C_INCLUDE_PATH=/usr/include/gdal

COPY .  /workspace/model
RUN echo "files copied to container"