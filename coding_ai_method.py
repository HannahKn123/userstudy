#region Improtiere die relevanten Bibliotheken
# ============================ Import Libraries ============================
import tensorflow as tf
import time
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import skdim
import numpy as np
import math
import pandas as pd
import keras
import cv2
import skdim
import tensorflow as tf
from tensorflow.keras.utils import to_categorical
from collections import Counter
from PIL import Image
from matplotlib import pyplot as plt
from skopt import gp_minimize
from imblearn.over_sampling import RandomOverSampler
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.neighbors import NearestNeighbors
from itertools import combinations
from tqdm.notebook import tqdm
from scipy import stats
from sklearn.linear_model import Lasso, lars_path, Ridge, ElasticNet, LogisticRegression, SGDClassifier
from collections import Counter
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import *
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_breast_cancer
from sklearn.preprocessing import StandardScaler, MinMaxScaler
#endregion


#region Import data and convert to data and label
def import_data(folder_path, train):

  if train==1:
    folder_path = os.path.join(folder_path, "test_data_train")
    print('Importing Training data...')
  elif train == 2:
    print('Importing Explanation data...')
    folder_path = os.path.join(folder_path, "Pool25")
  elif train == 0:
    print('Importing Test data...')
    folder_path = os.path.join(folder_path, "test_data_test")

  class_folders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]

  # Initialize an empty list to store xai_pixel values
  images = []
  ground_truth_labels = []

  for class_folder in class_folders:
        class_folder_path = os.path.join(folder_path, class_folder)
        image_files = [f for f in os.listdir(class_folder_path) if f.endswith('.jpg') or f.endswith('.png')]

        for image_file in image_files:
            image_path = os.path.join(class_folder_path, image_file)
            img = cv2.imread(image_path)
            #resized_img = cv2.resize(img, target_size)
            images.append(img)
            ground_truth_labels.append(class_folder)

  images_array = np.array(images)
  print('Imported', images_array.shape[0], 'images of shape', images_array.shape[1:4])


  str_ground_truth_labels = np.array(ground_truth_labels)

  label_mapping = {"Tel Aviv": "TelAviv",
          "Jerusalem": "Jerusalem",
          "Hamburg": "Hamburg",
          "Berlin": "Berlin"}

  # Map original class labels to new label names
  str_ground_truth_labels = np.array([label_mapping[label] for label in str_ground_truth_labels])
  print('Remapped to the following classes: ', np.unique(str_ground_truth_labels, return_counts=True)[0])
  print('Found', np.unique(str_ground_truth_labels, return_counts=True)[1], 'examples for the different classes respectively')

  # Assuming you have a function strLabel_to_intLabel_mapping that converts string labels to integers
  int_ground_truth_labels = strLabel_to_intLabel_mapping(str_ground_truth_labels)

  cat_ground_truth_labels = to_categorical(int_ground_truth_labels, 4)

  return images_array, int_ground_truth_labels, cat_ground_truth_labels, str_ground_truth_labels


def strLabel_to_intLabel_mapping(y):
  """
  input:
    y is the array of string labels
  output:
    int_labels_mapped is the array of the corresponding integer labels
  """
  # Create a dictionary to map string labels to int labels
  label_mapping = {'TelAviv': 2, 'Jerusalem': 3, 'Berlin': 0, 'Hamburg': 1}
  # Map string labels to int labels using the created dictionary
  int_labels_mapped = np.array([label_mapping[val] for val in y])
  return int_labels_mapped

#Herunterladen des Test und Trainingsdatensatzes
X_train, y_int_train, y_cat_train, y_str_train = import_data(r"C:\Users\maxim\OneDrive\Desktop\Ausbildung\Master Wiwi\Master Thesis\AI_XAI_Methode\userstudy", train=1)

X_test, y_int_test, y_cat_test, y_str_test = import_data(r"C:\Users\maxim\OneDrive\Desktop\Ausbildung\Master Wiwi\Master Thesis\AI_XAI_Methode\userstudy", train = 0)

X_expl, y_int_expl, y_cat_expl, y_str_expl = import_data(r"C:\Users\maxim\OneDrive\Desktop\Ausbildung\Master Wiwi\Master Thesis\AI_XAI_Methode\userstudy", train = 2)

#Datenvisualisierung
import random
plt.figure(figsize=(10, 10))
for i in range(9):
    ax = plt.subplot(3, 3, i + 1)
    i = random.randint(0,23)
    plt.imshow(cv2.cvtColor(X_expl[i], cv2.COLOR_BGR2RGB))
    plt.title([y_str_expl[i], y_int_expl[i]])
    plt.axis("off")

#Aufteilung des Trainingsdatensatzes in Trainings- und Validierungsdatensatz
X_train_1, X_val, y_train_1, y_val = train_test_split(X_train, y_cat_train, test_size = 0.2)


#Künstliche Veränderung des Bildes zur Stabilisierung des Models
data_augmentation = tf.keras.Sequential([
  tf.keras.layers.RandomFlip('horizontal'),
  tf.keras.layers.RandomRotation(0.2),
])

#Laden des Models und Definition der Bildgröße
from tensorflow.keras.applications import MobileNetV2

IMG_SIZE = (448, 448)
IMG_SHAPE = IMG_SIZE + (3,)
base_model = tf.keras.applications.MobileNetV2(input_shape=IMG_SHAPE,
                                               include_top=False,
                                               weights='imagenet')

base_model.trainable = False
#%%
base_model.summary()
#%%
global_average_layer = tf.keras.layers.GlobalAveragePooling2D()
#%%
prediction_layer = tf.keras.layers.Dense(4, activation='sigmoid')
#%%
preprocess_input = tf.keras.applications.mobilenet_v2.preprocess_input
#%%
inputs = tf.keras.Input(shape=(448, 448, 3))
x = data_augmentation(inputs)
x = preprocess_input(x)
x = base_model(x, training=False)
x = global_average_layer(x)
x = tf.keras.layers.Dropout(0.2)(x)
outputs = prediction_layer(x)
model = tf.keras.Model(inputs, outputs)

#%%
model.summary()
#%%
base_learning_rate = 0.0001
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=base_learning_rate),
              loss='categorical_crossentropy',
              metrics=['accuracy'])

#%%
pred0 = model.predict(X_test)
#%%
#Evaluate on training data
accuracy = accuracy_score(y_int_test, np.argmax(pred0, axis =1))
print(f"Accuracy: {accuracy:.4f}")

# Generate a classification report
class_report = classification_report(y_int_test, np.argmax(pred0, axis =1))
print("Classification Report:")
print(class_report)

# Generate a confusion matrix
conf_matrix = confusion_matrix(y_int_test, np.argmax(pred0, axis =1))
print("Confusion Matrix:")
print(conf_matrix)
#%%
initial_epochs = 10

from keras.callbacks import ModelCheckpoint

checkpointer = ModelCheckpoint(filepath = 'XXX.keras', verbose = 2, save_best_only = True)

history = model.fit(x = X_train_1, y = y_train_1,
                    epochs=initial_epochs,
                    validation_data=(X_val,y_val), callbacks = [checkpointer], verbose = 2)

#%%
acc = history.history['accuracy']
val_acc = history.history['val_accuracy']

loss = history.history['loss']
val_loss = history.history['val_loss']


plt.figure(figsize=(12, 6))
#plt.subplot(2, 1, 1)
plt.plot(acc, label='Training Accuracy')
plt.plot(val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.ylabel('Accuracy')
plt.xlabel('epoch')
plt.ylim([min(plt.ylim()),0.7])
plt.title('Training and Validation Accuracy (first training cycle)')
plt.savefig('acc_first_training_cycle.png', dpi=300)
plt.show()
#%%
#plt.subplot(2, 1, 2)
plt.figure(figsize=(12, 6))
plt.plot(loss, label='Training Loss')
plt.plot(val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.ylabel('Cross Entropy')
plt.ylim([0.6,1.5])
plt.title('Training and Validation Loss (first training cycle)')
plt.xlabel('epoch')
plt.savefig('loss_first_training_cycle.png', dpi=300)
plt.show()
#%%
pred0 = np.argmax(model.predict(X_test), axis = 1)
#%%
#Evaluate on training data
accuracy = accuracy_score(y_int_test, pred0)
print(f"Accuracy: {accuracy:.4f}")

# Generate a classification report
class_report = classification_report(y_int_test, pred0)
print("Classification Report:")
print(class_report)

# Generate a confusion matrix
conf_matrix = confusion_matrix(y_int_test, pred0)
print("Confusion Matrix:")
print(conf_matrix)
#%%
data_augmentation = tf.keras.Sequential([
  tf.keras.layers.RandomFlip('horizontal'),
  tf.keras.layers.RandomRotation(0.2),
])

from tensorflow.keras.applications import MobileNetV2

IMG_SIZE = (448, 448)
IMG_SHAPE = IMG_SIZE + (3,)
base_model = tf.keras.applications.MobileNetV2(input_shape=IMG_SHAPE,
                                               include_top=False,
                                               weights='imagenet')

# Let's take a look to see how many layers are in the base model
print("Number of layers in the base model: ", len(base_model.layers))

# Fine-tune from this layer onwards
fine_tune_at = 75

# Freeze all the layers before the `fine_tune_at` layer
for layer in base_model.layers[:fine_tune_at]:
  layer.trainable = False

inputs = tf.keras.Input(shape=(448, 448, 3))
x = data_augmentation(inputs)
x = preprocess_input(x)
x = base_model(x, training=False)
x = global_average_layer(x)
x = tf.keras.layers.Dropout(0.2)(x)
outputs = prediction_layer(x)
model = tf.keras.Model(inputs, outputs)

model.load_weights('XXX.keras')
#%%
model.summary()
#%%
base_learning_rate = 0.0001
model.compile(loss='categorical_crossentropy',
              optimizer = tf.keras.optimizers.RMSprop(learning_rate=base_learning_rate/10),
              metrics=['accuracy'])

#%%
model.summary()
#%%
fine_tune_epochs = 30
total_epochs =  initial_epochs + fine_tune_epochs
checkpointer = ModelCheckpoint(filepath = 'XXX.keras', verbose = 2, save_best_only = True)

history_fine = model.fit(x = X_train_1, y = y_train_1,
                         epochs=total_epochs,
                         initial_epoch=history.epoch[-1],
                         validation_data=(X_val,y_val), callbacks = [checkpointer], verbose = 2)

#%%
acc += history_fine.history['accuracy']
val_acc += history_fine.history['val_accuracy']

loss += history_fine.history['loss']
val_loss += history_fine.history['val_loss']

#%%
plt.figure(figsize=(12, 6))
#plt.subplot(2, 1, 1)
plt.plot(acc, label='Training Accuracy')
plt.plot(val_acc, label='Validation Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('epoch')
plt.ylim([0.3, 1])
plt.plot([initial_epochs,initial_epochs],
          plt.ylim(), label='Start Second Cycle of Fine Tuning')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy (both training cycles)')
plt.savefig('acc_both_training_cycle.png', dpi=300)
plt.show()
#%%
#plt.subplot(2, 1, 2)
plt.figure(figsize=(12, 6))
plt.plot(loss, label='Training Loss')
plt.plot(val_loss, label='Validation Loss')
plt.ylim([0, 1.4])
plt.ylabel('Cross Entropy')
plt.xlabel('epoch')
plt.plot([initial_epochs,initial_epochs],
         plt.ylim(), label='Start Second Cycle of Fine Tuning')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss (both training cycles)')
plt.xlabel('epoch')
plt.savefig('loss_both_training_cycle.png', dpi=300)
plt.show()

#%%
pred0 = np.argmax(model.predict(X_test), axis = 1)
#%%
#model.load_weights('fine_train_on_array.keras')
#%%
#Evaluate on training data
accuracy = accuracy_score(y_int_test, pred0)
print(f"Accuracy: {accuracy:.4f}")

# Generate a classification report
class_report = classification_report(y_int_test, pred0)
print("Classification Report:")
print(class_report)

# Generate a confusion matrix
conf_matrix = confusion_matrix(y_int_test, pred0)
print("Confusion Matrix:")
print(conf_matrix)
#%%
pred0 = np.argmax(model.predict(X_expl), axis = 1)
#%%
#Evaluate on training data
accuracy = accuracy_score(y_int_expl, pred0)
print(f"Accuracy: {accuracy:.4f}")

# Generate a classification report
class_report = classification_report(y_int_expl, pred0)
print("Classification Report:")
print(class_report)

# Generate a confusion matrix
conf_matrix = confusion_matrix(y_int_expl, pred0)
print("Confusion Matrix:")
print(conf_matrix)
#%%
keras.saving.save_model(model, 'MobileV2.keras')
#%%
model.summary()