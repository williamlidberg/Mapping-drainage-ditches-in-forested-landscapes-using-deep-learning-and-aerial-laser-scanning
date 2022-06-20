## Some notes on how to run inference for the webpage

The ditchnet docker container is used for inference on GPU: https://hub.docker.com/r/williamlidberg/ditchnet

<p>The script "process_new_img_from_dem.py" takes a dem as input, applies a high pass median filter. This new image is then split into 512x512 patches and the model is aplied to each patch. Once all patches are complete they are merged together into the size of the orignal image. The extent and projection is then copied from the input image and applied to the output. Finally the output is saved as a geotiff.</p>

There are two models to choose from

1.DitchNet_1m.h5\
2.DitchNet_05m.h5

## Docker
Go to the right directory:

    cd /mnt/nas1_extension_100tb/William/GitHub/Mapping-drainage-ditches-in-forested-landscapes-using-deep-learning-and-aerial-laser-scanning/webpage/

build image and include code

    docker build -t ditchnet .

Run container

    docker run -it --gpus=all ditchnet

Test inference

    python /min/modell/script.py /min/modell/testtile/ /min/output/ --temp_dir=/min/temp_dir/ --model=/min/modell/DitchNet_1m.h5





