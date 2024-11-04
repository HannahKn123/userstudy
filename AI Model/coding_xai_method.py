#Importiere alle notwendigen Pakete
import time
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import skdim
import random
import numpy as np
import math
import pandas as pd
import keras
import cv2
import skdim
import tensorflow as tf
import seaborn as sns

from tensorflow.keras.utils import to_categorical
from collections import Counter
from PIL import Image
#from google.colab.patches import cv2_imshow
from tensorflow.keras.applications import MobileNetV2
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
from scipy.stats import wasserstein_distance

from scipy.stats import mannwhitneyu
from scipy.stats import f_oneway
from scipy.stats import ttest_ind
from scipy.stats import wilcoxon

def import_data(folder_path, train):
  """
    Importiere Bilder und Labels aus den spezifischen Ordnern und formatiere die Daten für das Modell.

    Argumente:
    - folder_path: Pfad zum Datenordner
    - train: Markierung (0 = Testdaten, 1 = Trainingsdaten, 2 = Erklärungsdaten)

    Rückgabewerte:
    - images_array: Numpy-Array der Bilder
    - int_ground_truth_labels: Integer-Labels der Bilder
    - cat_ground_truth_labels: Kategorisierte Labels
    - str_ground_truth_labels: Original-Labels als Strings
  """

  # Festlegen des spezifischen Pfades basierend auf dem Datentyp
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

  # Initialisieren der Listen für Bilder und Labels
  images = []
  ground_truth_labels = []

 # Iteriere über Klassenordner und importiere Bilder
  for class_folder in class_folders:
        class_folder_path = os.path.join(folder_path, class_folder)
        image_files = [f for f in os.listdir(class_folder_path) if f.endswith('.jpg') or f.endswith('.png')]

        for image_file in image_files:
            image_path = os.path.join(class_folder_path, image_file)
            img = cv2.imread(image_path)
            #resized_img = cv2.resize(img, target_size)
            images.append(img)
            ground_truth_labels.append(class_folder)

  # Konvertiere die Bildliste in ein Numpy-Array
  images_array = np.array(images)
  print('Imported', images_array.shape[0], 'images of shape', images_array.shape[1:4])

  str_ground_truth_labels = np.array(ground_truth_labels)

  # Label-Zuordnung und Zählung
  label_mapping = {"Tel Aviv": "TelAviv",
          "Jerusalem": "Jerusalem",
          "Hamburg": "Hamburg",
          "Berlin": "Berlin"}

  # Label-Zuordnung und Zählung
  str_ground_truth_labels = np.array([label_mapping[label] for label in str_ground_truth_labels])
  print('Remapped to the following classes: ', np.unique(str_ground_truth_labels, return_counts=True)[0])
  print('Found', np.unique(str_ground_truth_labels, return_counts=True)[1], 'examples for the different classes respectively')

  # Umwandeln der Labels von Strings zu Integern
  int_ground_truth_labels = strLabel_to_intLabel_mapping(str_ground_truth_labels)

  # Kategorisieren der Labels
  cat_ground_truth_labels = to_categorical(int_ground_truth_labels, 4)

  return images_array, int_ground_truth_labels, cat_ground_truth_labels, str_ground_truth_labels

def strLabel_to_intLabel_mapping(y):
  """
  input:
    y is the array of string labels
  output:
    int_labels_mapped is the array of the corresponding integer labels
  """''
  # Create a dictionary to map string labels to int labels
  label_mapping = {'TelAviv': 2, 'Jerusalem': 3, 'Berlin': 0, 'Hamburg': 1}
  # Map string labels to int labels using the created dictionary
  int_labels_mapped = np.array([label_mapping[val] for val in y])
  return int_labels_mapped

data_dir='Data'
X_train, y_int_train, y_cat_train, y_str_train= import_data(data_dir, train = 1)

plt.imshow(cv2.cvtColor(X_train[0], cv2.COLOR_BGR2RGB))

X_test, y_int_test, y_cat_test, y_str_test = import_data(data_dir, train = 0)

plt.imshow(cv2.cvtColor(X_test[0], cv2.COLOR_BGR2RGB))

X_expl, y_int_expl, y_cat_expl, y_str_expl = import_data(data_dir, train = 2)


IMG_SIZE = (448, 448)
IMG_SHAPE = IMG_SIZE + (3,)
base_model = tf.keras.applications.MobileNetV2(input_shape=IMG_SHAPE, include_top=False, weights='imagenet')

base_model.trainable = False
global_average_layer = tf.keras.layers.GlobalAveragePooling2D()
prediction_layer = tf.keras.layers.Dense(4, activation='softmax')
preprocess_input = tf.keras.applications.mobilenet_v2.preprocess_input

inputs = tf.keras.Input(shape=(448, 448, 3))
x = preprocess_input(inputs)
x = base_model(x, training=False)
x = global_average_layer(x)
x = tf.keras.layers.Dropout(0.2)(x)
outputs = prediction_layer(x)
model = tf.keras.Model(inputs, outputs)

base_learning_rate = 0.0001
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=base_learning_rate),
              loss='categorical_crossentropy',
              metrics=['accuracy'])

model_dir='Models'
model.load_weights(filepath = os.path.join(model_dir, 'best_model.keras'))

pred_test = np.argmax(model.predict(X_test), axis = 1)
#%%
accuracy = accuracy_score(y_int_test, pred_test)
print(f"Accuracy: {accuracy:.4f}")

class_report = classification_report(y_int_test, pred_test)
print("Classification Report:")
print(class_report)

conf_matrix = confusion_matrix(y_int_test, pred_test)
print("Confusion Matrix:")
print(conf_matrix)

IMG_SIZE = (448, 448)
IMG_SHAPE = IMG_SIZE + (3,)
base_model = tf.keras.applications.MobileNetV2(input_shape=IMG_SHAPE, include_top=False, weights='imagenet')

base_model.trainable = False
global_average_layer = tf.keras.layers.GlobalAveragePooling2D()
prediction_layer = tf.keras.layers.Dense(4, activation='softmax')
preprocess_input = tf.keras.applications.mobilenet_v2.preprocess_input

inputs = tf.keras.Input(shape=(448, 448, 3))
x = preprocess_input(inputs)
x = base_model(x, training=False)

grad_model = tf.keras.Model(inputs, x)

grad_model.summary()

grad_model.load_weights(filepath = os.path.join(model_dir, 'best_model.keras'))


layer_names = [layer.name for layer in model.layers]
classifier_layer_names = layer_names[-3:]
print(classifier_layer_names)


def gradCAMplusplus(img_array, model, grad_conv_model, classifier_layer_names, threshold=0.5):
    classifier_input = tf.keras.Input(shape=grad_conv_model.output.shape[1:])
    x = classifier_input
    for layer_name in classifier_layer_names:
        x = model.get_layer(layer_name)(x)
    classifier_model = keras.Model(classifier_input, x)

    with tf.GradientTape() as tape1:
        with tf.GradientTape() as tape2:
            with tf.GradientTape() as tape3:
                last_conv_layer_output = grad_conv_model(img_array)
                preds = classifier_model(last_conv_layer_output)
                top_pred_index = tf.argmax(preds[0])
                top_class_channel = preds[:, top_pred_index]

                conv_first_grad = tape3.gradient(top_class_channel, last_conv_layer_output)
            conv_second_grad = tape2.gradient(conv_first_grad, last_conv_layer_output)
        conv_third_grad = tape1.gradient(conv_second_grad, last_conv_layer_output)

    global_sum = np.sum(last_conv_layer_output, axis=(0, 1, 2))
    alpha_num = conv_second_grad[0]
    alpha_denom = conv_second_grad[0] * 2.0 + conv_third_grad[0] * global_sum
    alpha_denom = np.where(alpha_denom != 0.0, alpha_denom, 1e-10)

    alphas = alpha_num / alpha_denom
    alpha_normalization_constant = np.sum(alphas, axis=(0, 1))
    alphas /= alpha_normalization_constant

    weights = np.maximum(conv_first_grad[0], 0.0)
    deep_linearization_weights = np.sum(weights * alphas, axis=(0, 1))
    grad_cam_map = np.sum(deep_linearization_weights * last_conv_layer_output[0], axis=2)

    heatmap = np.maximum(grad_cam_map, 0)
    max_heat = np.max(heatmap)
    if max_heat == 0:
        max_heat = 1e-10
    heatmap /= max_heat

    # Skalierung der Heatmap auf Bildgröße
    heatmap_resized = cv2.resize(heatmap, (img_array.shape[2], img_array.shape[1]))

    # Extraktion der wichtigen Pixel mit X/Y-Koordinaten
    important_pixels = []
    for y in range(heatmap_resized.shape[0]):
        for x in range(heatmap_resized.shape[1]):
            if heatmap_resized[y, x] > threshold:
                important_pixels.append((x, y, heatmap_resized[y, x]))

    return heatmap, important_pixels


def upsample_gradCAM(activations):
    heatmap = cv2.resize(activations, (448, 448))
    heatmap /= np.sum(heatmap)

    return heatmap


# %%
def explain_gradCAM(activations, img_index):
    heatmap = cv2.resize(activations, (448, 448))
    heatmap = np.expand_dims(heatmap, axis=-1)
    heatmap /= np.sum(heatmap)
    explanation = heatmap * X_expl[img_index]
    explanation -= np.min(explanation)
    explanation /= np.max(explanation)
    explanation = cv2.cvtColor(explanation, cv2.COLOR_BGR2RGB)
    # plt.matshow(explanation)
    # plt.show()

    return explanation


# %%
def visualize_gradCAM(activations, img_index, alpha):
    heatmap = cv2.resize(activations, (448, 448))
    heatmap = (heatmap * 255).astype("uint8")
    heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
    superimposed_img = heatmap * alpha + X_expl[img_index]
    superimposed_img = np.clip(superimposed_img, 0, 255).astype("uint8")
    superimposed_img = cv2.cvtColor(superimposed_img, cv2.COLOR_BGR2RGB)

    # plt.matshow(superimposed_img)
    # plt.show()

    return superimposed_img


def plot_attention_map(attention_map):
    plt.imshow(attention_map)
    plt.colorbar()
    plt.show()


def save_important_pixels_to_excel(important_pixels, output_path):
    # Umwandeln der wichtigen Pixel in ein DataFrame
    df = pd.DataFrame(important_pixels, columns=["X", "Y", "Importance"])
    # Speichern als Excel-Datei
    df.to_excel(output_path, index=False)
    print(f"Important pixels saved to {output_path}")


def save_heatmap_overlay(img, heatmap, output_path):
    # Heatmap in Größe des Bildes skalieren
    heatmap_resized = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
    heatmap_resized = (heatmap_resized * 255).astype("uint8")
    heatmap_colored = cv2.applyColorMap(heatmap_resized, cv2.COLORMAP_JET)

    # Überlagerung der Heatmap auf das Originalbild
    overlay = cv2.addWeighted(heatmap_colored, 0.5, img, 0.5, 0)
    overlay_rgb = cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)

    # Speichern des überlagerten Bildes
    plt.imsave(output_path, overlay_rgb)
    print(f"Overlay heatmap saved to {output_path}")


def save_transparent_highlight(img, important_pixels, output_path):
    # Erstellen einer Kopie des Originalbildes für die Markierung
    highlighted_img = img.copy()

    # Markiere alle wichtigen Pixel (Wichtigkeit > 0.5) in transparentem Rot
    for x, y, importance in important_pixels:
        if importance > 0.5:
            # Markierung in leicht transparentem Rot (R=255, G=0, B=0, Transparenz=0.4)
            highlighted_img[y, x] = (0.6 * img[y, x] + 0.4 * np.array([255, 0, 0])).astype(np.uint8)

    # Speichern des markierten Bildes
    plt.imsave(output_path, cv2.cvtColor(highlighted_img, cv2.COLOR_BGR2RGB))
    print(f"Transparent highlighted image saved to {output_path}")


# Mapping der Label-Indexe zu Klassennamen
label_mapping = {0: "Berlin", 1: "Hamburg", 2: "TelAviv", 3: "Jerusalem"}

# Hauptschleife für jedes Bild in X_expl
for i, img in enumerate(X_expl):
    img_array = np.expand_dims(img, axis=0)
    heatmap, important_pixels = gradCAMplusplus(img_array, model, grad_model, classifier_layer_names, threshold=0.5)

    # Tatsächliche Klasse und Vorhersageklasse bestimmen
    true_class = label_mapping[y_int_expl[i]]
    pred_class_index = np.argmax(model.predict(img_array), axis=1)[0]
    pred_class = label_mapping[pred_class_index]

    # Erstellen des Bildordners mit tatsächlicher und vorhergesagter Klasse
    image_folder = os.path.join("ImportantPixels", f"image_{i}_{true_class}_{pred_class}")
    os.makedirs(image_folder, exist_ok=True)

    # Speichern der wichtigen Pixel als Excel in den Bildordner
    excel_path = os.path.join(image_folder, "important_pixels.xlsx")
    save_important_pixels_to_excel(important_pixels, excel_path)

    # Speichern der überlagerten Heatmap in den Bildordner
    heatmap_path = os.path.join(image_folder, "heatmap_overlay.png")
    save_heatmap_overlay(img, heatmap, heatmap_path)

    # Speichern des transparent hervorgehobenen Bildes
    highlighted_image_path = os.path.join(image_folder, "highlighted_important_pixels.png")
    save_transparent_highlight(img, important_pixels, highlighted_image_path)




