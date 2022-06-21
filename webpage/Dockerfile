FROM williamlidberg/ditchnet

RUN mkdir /min/
RUN mkdir /min/input
RUN mkdir /min/output
RUN mkdir /min/modell/
RUN mkdir /min/temp_dir/
COPY .  /min/modell/
# install whitebox on ubuntu 18.05 #from https://github.com/jblindsay/whitebox-tools/issues/112
RUN pip install whitebox==1.4.0

#RUN rm -rf /usr/local/lib/python3.7/dist-packages/whitebox/WBT
#RUN rm -rf /usr/local/lib/python3.7/dist-packages/whitebox/whitebox_tools
#RUN pip install whitebox==1.4.0


# docker build -t ditchnet -f /mnt/Extension_100TB/william/GitHub/Mapping-drainage-ditches-in-forested-landscapes-using-deep-learning-and-aerial-laser-scanning/webpage/Dockerfile .
# docker run -it -v /mnt/Extension_100TB/temp/dem1m:/workspace/data -v /mnt/Extension_100TB/william/GitHub/Mapping-drainage-ditches-in-forested-landscapes-using-deep-learning-and-aerial-laser-scanning:/workspace/code -v /mnt/ramdisk:/workspace/temp ditchnet:latest
# python /workspace/code/process_new_img_from_dem.py /workspace/data/ /workspace/data/output /workspace/temp/ --model_path=/workspace/code/DitchNet_1m.h5
# docker run -it --gpus all -v /mnt/Extension_100TB/temp/dem1m:/workspace/data -v /mnt/Extension_100TB/william/GitHub/Mapping-drainage-ditches-in-forested-landscapes-using-deep-learning-and-aerial-laser-scanning:/workspace/code -v /mnt/ramdisk:/workspace/temp ditchdocker:latest 
#
RUN python -c "exec('try:import whitebox\nexcept: pass')"