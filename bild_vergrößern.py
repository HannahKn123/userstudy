import os
from PIL import Image

# Ordnerpfade
input_folder = "1_org_image"
output_folder = "1_study_input"

# Erstelle den Ausgabeordner, falls er noch nicht existiert
os.makedirs(output_folder, exist_ok=True)

# Durchlaufe alle Dateien im Eingabeordner
for filename in os.listdir(input_folder):
    if filename.endswith(".jpg") or filename.endswith(".png"):  # Passe die Dateiendungen bei Bedarf an
        # Lade das Bild
        image_path = os.path.join(input_folder, filename)
        image = Image.open(image_path)

        # Vergrößere das Bild (hier auf das Doppelte der Originalgröße)
        new_width = image.width * 2
        new_height = image.height * 2
        resized_image = image.resize((new_width, new_height), Image.LANCZOS)

        # Speichere das vergrößerte Bild im Ausgabeordner unter demselben Namen
        output_path = os.path.join(output_folder, filename)
        resized_image.save(output_path)
        print(f"{filename} wurde erfolgreich vergrößert und gespeichert in {output_folder}")

print("Alle Bilder wurden erfolgreich vergrößert und gespeichert.")
