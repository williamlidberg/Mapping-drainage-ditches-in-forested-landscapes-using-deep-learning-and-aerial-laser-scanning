# delete tiles with less than 262 ditch pixels to combat class imbalance. It might be a good idea to have a backup of the data before running this script
combined_images_training = 'Y:/William/Skogsstyrelsen/dataprocessing/DitchNet/TrainingData/exported/images/'
combained_labels_training = 'Y:/William/Skogsstyrelsen/dataprocessing/DitchNet/TrainingData/exported/labels/'
import util.Functions
print('Delete no-ditch chips')
util.Functions.Delete_tiles(combined_images_training, combained_labels_training, 262) #262 is 0.01 % of a 512 x 512 image chip
