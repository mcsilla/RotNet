from __future__ import print_function

import os
import sys

from keras.callbacks import ModelCheckpoint, EarlyStopping, TensorBoard, ReduceLROnPlateau
from keras.applications.resnet50 import ResNet50
from keras.applications.imagenet_utils import preprocess_input
from keras.models import Model
from keras.layers import Dense, Flatten
from keras.optimizers import SGD
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import angle_error, RotNetDataGenerator
from data.arcanum_images import get_filenames


parser = argparse.ArgumentParser()
parser.add_argument('--batch_size', type=int, required=True)
parser.add_argument('--image_size', type=int, required=True)
parser.add_argument('--num_of_epochs', type=int, required=True)

args, _ = parser.parse_known_args()

file_patterns = [
    # '/home/mnt/noah/_HungaricanaPic/jpg/gallery/bflphoto/fofoto/6x6-6x9/**/*.jpg',
    '/home/mnt/noah/_HungaricanaPic/jpg/gallery/fortepan/**/*.jpg',
    '/home/mnt/noah/_HungaricanaPic/jpg/gallery/bflphoto/varosrendezesi/**/*.jpg',
    '/home/mnt/noah/_HungaricanaPic/jpg/gallery/fszekphoto/**/*.jpg/',
]

train_filenames, test_filenames = get_filenames(file_patterns)

print(len(train_filenames), 'train samples')
print(len(test_filenames), 'test samples')

model_name = 'rotnet_arcanum_resnet50'

# number of classes
nb_classes = 4
# input image shape
input_shape = (args.image_size, args.image_size, 3)

# load base model
base_model = ResNet50(weights='imagenet', include_top=False,
                      input_shape=input_shape)

# append classification layer
x = base_model.output
x = Flatten()(x)
final_output = Dense(nb_classes, activation='softmax', name='fc4')(x)

# create the new model
model = Model(inputs=base_model.input, outputs=final_output)

model.summary()

# model compilation
model.compile(loss='categorical_crossentropy',
              optimizer=SGD(lr=0.01, momentum=0.9),
              metrics=[angle_error])

# training parameters
batch_size = args.batch_size
nb_epoch = args.num_of_epochs

output_folder = f'/home/models/model_rotnet_SGD_batch_size{batch_size}_img_size_{args.image_size}'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# callbacks
monitor = 'val_angle_error'
checkpointer = ModelCheckpoint(
    filepath=os.path.join(output_folder, model_name + '.hdf5'),
    monitor=monitor,
    save_best_only=True
)
reduce_lr = ReduceLROnPlateau(monitor=monitor, patience=3)
early_stopping = EarlyStopping(monitor=monitor, patience=5)
tensorboard = TensorBoard()

# training loop
model.fit_generator(
    RotNetDataGenerator(
        train_filenames,
        input_shape=input_shape,
        batch_size=batch_size,
        preprocess_func=preprocess_input,
        crop_center=True,
        crop_largest_rect=True,
        shuffle=True
    ),
    steps_per_epoch=len(train_filenames) / batch_size,
    epochs=nb_epoch,
    validation_data=RotNetDataGenerator(
        test_filenames,
        input_shape=input_shape,
        batch_size=batch_size,
        preprocess_func=preprocess_input,
        crop_center=True,
        crop_largest_rect=True
    ),
    validation_steps=len(test_filenames) / batch_size,
    callbacks=[checkpointer, reduce_lr, early_stopping, tensorboard],
    workers=10
)
