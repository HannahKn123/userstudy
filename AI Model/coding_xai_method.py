#Importiere alle notwendigen Pakete
import os
import numpy as np
import pandas as pd
import cv2
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.utils import to_categorical
from tensorflow import keras
from tensorflow.keras.applications import MobileNetV2
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Funktion zum Laden und Vorverarbeiten von Bilddaten
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
    - image_names: Liste der Original-Bildnamen
    """
    # Festlegen des spezifischen Pfades basierend auf dem Datentyp
    if train == 1:
        folder_path = os.path.join(folder_path, "train_1")
        print('Importing Training data...')
    elif train == 0:
        print('Importing Test data...')
        folder_path = os.path.join(folder_path, "test_1")

    # Liste aller Klassenordner innerhalb des Pfads erstellen
    class_folders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]

    # Initialisieren der Listen für Bilder, Labels und Bildnamen
    images = []
    ground_truth_labels = []
    image_names = []  # Neue Liste zum Speichern der Bildnamen

    # Iteriere über Klassenordner und importiere Bilder
    for class_folder in class_folders:
        class_folder_path = os.path.join(folder_path, class_folder)
        image_files = [f for f in os.listdir(class_folder_path) if f.endswith('.jpg') or f.endswith('.png')]

        for image_file in image_files:
            image_path = os.path.join(class_folder_path, image_file)
            img = cv2.imread(image_path)
            images.append(img)
            ground_truth_labels.append(class_folder)
            image_names.append(image_file)  # Speichern des Bildnamens

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

    return images_array, int_ground_truth_labels, cat_ground_truth_labels, str_ground_truth_labels, image_names  # Rückgabe der Bildnamen


# Funktion zur Umwandlung von String-Labels zu Integer-Labels
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


# Datenpfad und Laden der Trainings-, Test- und Erklärungsdaten
data_dir='Data'
X_train, y_int_train, y_cat_train, y_str_train, image_names_train = import_data(data_dir, train=1)
X_test, y_int_test, y_cat_test, y_str_test, image_names_test = import_data(data_dir, train=0)

# Aufbau des Modells
IMG_SIZE = (448, 448)
IMG_SHAPE = IMG_SIZE + (3,)
base_model = tf.keras.applications.MobileNetV2(input_shape=IMG_SHAPE, include_top=False, weights='imagenet')

# Freezing der Basismodell-Gewichte
base_model.trainable = False
global_average_layer = tf.keras.layers.GlobalAveragePooling2D()
prediction_layer = tf.keras.layers.Dense(4, activation='softmax')
preprocess_input = tf.keras.applications.mobilenet_v2.preprocess_input

# Modell mit MobileNetV2 als Basismodell und benutzerdefiniertem Klassifikationskopf
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

# Laden der gespeicherten Modellgewichte
model_dir='Models'
model.load_weights(filepath = os.path.join(model_dir, 'best_model.keras'))


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

#Ímplementierung des Grad Models
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

    # Markiere alle wichtigen Pixel (Wichtigkeit > 0.5) in transparentem Lila
    for x, y, importance in important_pixels:
        if importance > 0.5:
            # Markierung in leicht transparentem Lila (R=128, G=0, B=128, Transparenz=0.4)
            highlighted_img[y, x] = (0.6 * img[y, x] + 0.4 * np.array([128, 0, 128])).astype(np.uint8)

    # Speichern des markierten Bildes
    plt.imsave(output_path, cv2.cvtColor(highlighted_img, cv2.COLOR_BGR2RGB))
    print(f"Transparent highlighted image saved to {output_path}")


# Mapping der Label-Indexe zu Klassennamen
label_mapping = {0: "Berlin", 1: "Hamburg", 2: "TelAviv", 3: "Jerusalem"}

# Hauptschleife für jedes Bild in X_test
for i, img in enumerate(X_test):
    img_array = np.expand_dims(img, axis=0)
    heatmap, important_pixels = gradCAMplusplus(img_array, model, grad_model, classifier_layer_names, threshold=0.5)

    # Tatsächliche Klasse und Vorhersageklasse bestimmen
    true_class = label_mapping[y_int_test[i]]
    pred_class_index = np.argmax(model.predict(img_array), axis=1)[0]
    pred_class = label_mapping[pred_class_index]

    # Verwenden des Originalnamens des Bildes ohne Dateiendung
    original_name = os.path.splitext(image_names_test[i])[0]  # Entfernt die Dateiendung (z. B. .png oder .jpg)

    # Sicherstellen, dass das Verzeichnis "ImportantPixels_Image" existiert
    os.makedirs("ImportantPixels_Image", exist_ok=True)
    os.makedirs("GradCAM", exist_ok=True)
    os.makedirs("ImportantPixels", exist_ok=True)

    # Pfad und Name für die Excel-Datei im Ordner "ImportantPixels"
    excel_filename = f"{original_name}_{true_class}_{pred_class}.xlsx"
    excel_path = os.path.join("ImportantPixels", excel_filename)
    save_important_pixels_to_excel(important_pixels, excel_path)

    # Pfad und Name für das GradCAM-Bild im Ordner "GradCAM"
    gradcam_filename = f"{original_name}_GradCAM.png"
    gradcam_path = os.path.join("GradCAM", gradcam_filename)
    save_heatmap_overlay(img, heatmap, gradcam_path)

    # Pfad und Name für das Bild mit den markierten wichtigen Pixeln im Ordner "ImportantPixels_Image"
    highlighted_image_filename = f"{original_name}_{true_class}_{pred_class}.png"
    highlighted_image_path = os.path.join("ImportantPixels_Image", highlighted_image_filename)
    save_transparent_highlight(img, important_pixels, highlighted_image_path)