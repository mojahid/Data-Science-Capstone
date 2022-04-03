import matplotlib.pyplot as plt
import numpy as np
import os
import PIL
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, Model
from tensorflow.keras.models import Sequential
from keras.applications.vgg16 import VGG16

data_dir = r"C:\Users\minaf\Documents\GWU\Capstone\Data\lagos\Google_Images42\Train\png"

MODEL_SERIAL = 'Pre_bn09'

batch_size = 48
img_height = 10
img_width = 10
epochs = 100


def scheduler(epoch, lr):
    lr_0 = lr
    lr_max = 0.001
    lr_0_steps = 5
    lr_max_steps = 5
    lr_min = 0.0005
    lr_decay = 0.9
    if epoch < lr_0_steps:
        lr = lr_0 + ((lr_max - lr_min) / lr_0_steps) * (epoch - 1)
    elif epoch < lr_0_steps + lr_max_steps:
        lr = lr_max
    else:
        lr = max(lr_max * lr_decay ** (epoch - lr_0_steps - lr_max_steps), lr_min)
    return lr


train_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir,
    label_mode="categorical",
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=(32, 32),
    batch_size=batch_size)

val_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir,
    label_mode="categorical",
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=(32, 32),
    batch_size=batch_size)


data_augmentation = keras.Sequential(
  [
    layers.RandomFlip(input_shape=(img_height,
                                  img_width,
                                  3)),
    #layers.Resizing(32, 32),
  ])

base_model = tf.keras.applications.VGG16(weights='imagenet', include_top=False,
                                         input_shape=(32, 32, 3))

for layer in base_model.layers:
    layer.trainable = False

# print(base_model.summary())

x = layers.Flatten()(base_model.output)
x = layers.Dense(200, activation='relu')(x)
x = layers.Dropout(0.2)(x)
x = layers.Dense(200, activation='relu')(x)
x = layers.Dropout(0.25)(x)
x = layers.Dense(250, activation='relu')(x)
x = layers.Dropout(0.25)(x)
x = layers.Dense(250, activation='relu')(x)
x = layers.Dropout(0.2)(x)
predictions = layers.Dense(2, activation = 'softmax')(x)

head_model = Model(inputs=base_model.input, outputs=predictions)
head_model.compile(optimizer='adamax', loss=tf.keras.losses.BinaryCrossentropy(), metrics=['accuracy'])

callback = tf.keras.callbacks.LearningRateScheduler(scheduler)
early_stop = tf.keras.callbacks.EarlyStopping(monitor='accuracy', patience=15)
check_point = tf.keras.callbacks.ModelCheckpoint('model_{}.h5'.format(MODEL_SERIAL),
                                                 monitor='accuracy',
                                                 save_best_only=True)

class_weight = {0:1 , 1:15}#, 2:0.5 }

history = head_model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=epochs,
    callbacks=[early_stop, check_point, callback],
    class_weight = class_weight
)

fig, axs = plt.subplots(2, 1, figsize=(15, 15))
axs[0].plot(history.history['loss'])
axs[0].plot(history.history['val_loss'])
axs[0].title.set_text('Training Loss vs Validation Loss')
axs[0].set_xlabel('Epochs')
axs[0].set_ylabel('Loss')
axs[0].legend(['Train', 'Val'])
axs[1].plot(history.history['accuracy'])
axs[1].plot(history.history['val_accuracy'])
axs[1].title.set_text('Training Accuracy vs Validation Accuracy')
axs[1].set_xlabel('Epochs')
axs[1].set_ylabel('Accuracy')
axs[1].legend(['Train', 'Val'])

plt.savefig('model_pre_{}.png'.format(MODEL_SERIAL))
plt.show()

