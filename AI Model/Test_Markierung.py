# Import der notwendigen Pakete
import os
import numpy as np
import cv2
import matplotlib.pyplot as plt


# Funktion zur Markierung und Speicherung der wichtigen Pixel
def save_transparent_highlight(img, important_pixels, output_path, mark_size=3):
    """
    Markiert die wichtigen Pixel auf einem Bild in transparentem Lila und speichert das Bild.

    Argumente:
    - img: Originalbild als Numpy-Array
    - important_pixels: Liste der wichtigen Pixel mit Koordinaten (X, Y) und Wichtigkeit
    - output_path: Pfad zum Speichern des markierten Bildes
    - mark_size: Größe der Markierung um jedes wichtige Pixel
    """
    # Erstellen einer Kopie des Originalbildes für die Markierung
    highlighted_img = img.copy()

    # Markiere alle wichtigen Pixel (Wichtigkeit > 0.5) in transparentem Lila
    for x, y, importance in important_pixels:
        if importance > 0.5:
            # Markiere einen kleinen Bereich um das Pixel
            for dx in range(-mark_size, mark_size + 1):
                for dy in range(-mark_size, mark_size + 1):
                    # Stelle sicher, dass die Markierung innerhalb der Bildgrenzen bleibt
                    if 0 <= x + dx < img.shape[1] and 0 <= y + dy < img.shape[0]:
                        highlighted_img[y + dy, x + dx] = (
                                0.6 * img[y + dy, x + dx] + 0.4 * np.array([128, 0, 128])
                        ).astype(np.uint8)

    # Speichern des markierten Bildes
    plt.imsave(output_path, cv2.cvtColor(highlighted_img, cv2.COLOR_BGR2RGB))
    print(f"Transparent highlighted image saved to {output_path}")


# Suche nach dem einzigen Bild im Ordner "Test"
test_folder = "Test"
test_image_files = [f for f in os.listdir(test_folder) if f.endswith(('.jpg', '.png', '.jpeg'))]
if not test_image_files:
    raise FileNotFoundError(f"Kein Bild im Ordner '{test_folder}' gefunden.")
test_image_path = os.path.join(test_folder, test_image_files[0])
print(f"Gefundenes Testbild: {test_image_files[0]}")

# Bild laden
test_img = cv2.imread(test_image_path)
if test_img is None:
    raise FileNotFoundError(f"Das Bild {test_image_path} konnte nicht geladen werden.")

# Definieren gezielter wichtiger Pixel am Rand des Bildes
important_pixels_test = [
    (0, 0, 1.0),  # Linke obere Ecke
    (test_img.shape[1] - 1, 0, 1.0),  # Rechte obere Ecke
    (0, test_img.shape[0] - 1, 1.0),  # Linke untere Ecke
    (test_img.shape[1] - 1, test_img.shape[0] - 1, 1.0),  # Rechte untere Ecke
    (test_img.shape[1] // 2, 0, 1.0),  # Mitte obere Kante
    (test_img.shape[1] // 2, test_img.shape[0] - 1, 1.0),  # Mitte untere Kante
    (0, test_img.shape[0] // 2, 1.0),  # Mitte linke Kante
    (test_img.shape[1] - 1, test_img.shape[0] // 2, 1.0)  # Mitte rechte Kante
]

# Erstellen des Ordners "Test_ImportantPixels_Image" falls noch nicht vorhanden
os.makedirs("Test_ImportantPixels_Image", exist_ok=True)

# Pfad für das markierte Bild
highlighted_image_test_path = os.path.join("Test_ImportantPixels_Image", "test_highlighted_image.png")

# Verwenden der Funktion, um das Bild mit den definierten wichtigen Pixeln zu markieren
save_transparent_highlight(test_img, important_pixels_test, highlighted_image_test_path, mark_size=3)

print(f"Test image with highlighted important pixels saved to {highlighted_image_test_path}")
