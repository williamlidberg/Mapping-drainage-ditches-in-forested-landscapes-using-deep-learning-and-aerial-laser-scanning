export PYTHONPATH=/home/william/Downloads/crfasrnn_keras-master/src/:$PYTHONPATH
python /home/william/Downloads/implementation_v4/train.py /home/william/Downloads/TrainingData/HalfMeterDEm/HighPassMedianFilter3mDEM05mNonoverlapping/CombinedTraining/images /home/william/Downloads/TrainingData/HalfMeterDEm/HighPassMedianFilter3mDEM05mNonoverlapping/CombinedTraining/labels /home/william/Downloads/logfolder/log28/HalfMeter XceptionUNet --epochs 100 --steps_per_epoch 100

# Train CRF layer
python /home/william/Downloads/implementation_v4/train_crf.py /home/william/Downloads/TrainingData/HalfMeterDEm/HighPassMedianFilter3mDEM05mNonoverlapping/CombinedTraining/images /home/william/Downloads/TrainingData/HalfMeterDEm/HighPassMedianFilter3mDEM05mNonoverlapping/CombinedTraining/labels /home/william/Downloads/logfolder/log28/HalfMeter/test.h5 /home/william/Downloads/logfolder/log28/HalfMeterCRF /home/william/Downloads/logfolder/log28/HalfMeter/train_imgs.txt --epochs 42 --steps_per_epoch 100

# use model to predict test chips
python /home/william/Downloads/implementation_v4/process_img_new.py /home/william/Downloads/TrainingData/HalfMeterDEm/HighPassMedianFilter3mDEM05mNonoverlapping/CombinedTesting/images /home/william/Downloads/logfolder/log28/HalfMeterCRF/test.h5 /home/william/Downloads/TrainingData/HalfMeterDEm/HighPassMedianFilter3mDEM05mNonoverlapping/CombinedTesting/PredictWithoutExtent
# Predict internaltional areas (Finland)
python /home/william/Downloads/implementation_v4/process_img_InternationalAreas.py /home/william/Downloads/InternationalTestAreas/HalfMeterDEM/splithalfmeterDataAll/Finland/images /home/william/Downloads/logfolder/log28/HalfMeterCRF/test.h5 /home/william/Downloads/InternationalTestAreas/HalfMeterDEM/splithalfmeterDataAll/Finland/predswithoutextent
# Predict internaltional areas (Swweden)
python /home/william/Downloads/implementation_v4/process_img_InternationalAreas.py /home/william/Downloads/InternationalTestAreas/HalfMeterDEM/splithalfmeterDataAll/Sweden/images /home/william/Downloads/logfolder/log28/HalfMeterCRF/test.h5 /home/william/Downloads/InternationalTestAreas/HalfMeterDEM/splithalfmeterDataAll/Sweden/predswithoutextent
# Predict internaltional areas (Poland)
python /home/william/Downloads/implementation_v4/process_img_InternationalAreas.py /home/william/Downloads/InternationalTestAreas/HalfMeterDEM/splithalfmeterDataAll/Poland/images /home/william/Downloads/logfolder/log28/HalfMeterCRF/test.h5 /home/william/Downloads/InternationalTestAreas/HalfMeterDEM/splithalfmeterDataAll/Poland/predswithoutextent
# Predict internaltional areas (Latvia)
python /home/william/Downloads/implementation_v4/process_img_InternationalAreas.py /home/william/Downloads/InternationalTestAreas/HalfMeterDEM/splithalfmeterDataAll/Latvia/images /home/william/Downloads/logfolder/log28/HalfMeterCRF/test.h5 /home/william/Downloads/InternationalTestAreas/HalfMeterDEM/splithalfmeterDataAll/Latvia/predswithoutextent
