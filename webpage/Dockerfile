FROM williamlidberg/ditchnet

RUN pip install whitebox
RUN mkdir /workspace/
RUN mkdir /workspace/data
RUN mkdir /workspace/code
COPY .  /workspace/code
# docker build -t ditchnet -f /mnt/Extension_100TB/william/GitHub/Mapping-drainage-ditches-in-forested-landscapes-using-deep-learning-and-aerial-laser-scanning/webpage/Dockerfile .
# docker run -it -v /mnt/Extension_100TB/temp/dem1m:/workspace/data -v /mnt/Extension_100TB/william/GitHub/Mapping-drainage-ditches-in-forested-landscapes-using-deep-learning-and-aerial-laser-scanning:/workspace/code -v /mnt/ramdisk:/workspace/temp ditchnet:latest
# python /workspace/code/process_new_img_from_dem.py /workspace/data/ /workspace/data/output /workspace/temp/ --model_path=/workspace/code/DitchNet_1m.h5
# docker run -it --gpus all -v /mnt/Extension_100TB/temp/dem1m:/workspace/data -v /mnt/Extension_100TB/william/GitHub/Mapping-drainage-ditches-in-forested-landscapes-using-deep-learning-and-aerial-laser-scanning:/workspace/code -v /mnt/ramdisk:/workspace/temp ditchdocker:latest 
#