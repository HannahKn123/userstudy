import os
import shutil

# Pfade definieren
important_pixels_path = r"C:\Users\maxim\OneDrive\Desktop\Ausbildung\Master Wiwi\Master Thesis\AI_XAI_Methode\userstudy\AI Model\ImportantPixels"
important_pixels_us_path = r"C:\Users\maxim\OneDrive\Desktop\Ausbildung\Master Wiwi\Master Thesis\AI_XAI_Methode\userstudy\AI Model\ImportantPixels_us"
data_sampling_berlin_path = r"C:\Users\maxim\OneDrive\Desktop\Ausbildung\Master Wiwi\Master Thesis\AI_XAI_Methode\userstudy\AI Model\Data\data_sampling\Tel Aviv"

# Erstelle Zielordner, falls nicht existierend
os.makedirs(important_pixels_us_path, exist_ok=True)

# IDs und zugehörige Zahlen aus dem Ordner "data_sampling/Berlin" sammeln
berlin_files = os.listdir(data_sampling_berlin_path)
berlin_id_map = {}
for file in berlin_files:
    parts = file.split("_")
    if len(parts) > 2:  # Sicherstellen, dass Datei das richtige Format hat
        img_id = parts[1]  # Die ID extrahieren
        extra_number = parts[2]  # Die zusätzliche Zahl extrahieren
        berlin_id_map[img_id] = extra_number

# Dateien im Ordner "ImportantPixels" durchgehen und relevante kopieren
for file in os.listdir(important_pixels_path):
    parts = file.split("_")
    if len(parts) > 1:  # Sicherstellen, dass Datei das richtige Format hat
        img_id = parts[1]  # Die ID aus dem Dateinamen extrahieren
        if img_id in berlin_id_map:
            # Neue Zahl hinzufügen
            extra_number = berlin_id_map[img_id]
            new_filename = f"{parts[0]}_{img_id}_{extra_number}_{'_'.join(parts[2:])}"  # Neuer Dateiname
            src_file = os.path.join(important_pixels_path, file)
            dest_file = os.path.join(important_pixels_us_path, new_filename)
            shutil.copy2(src_file, dest_file)  # Datei kopieren
            print(f"Kopiert: {file} --> {new_filename}")

print("Vorgang abgeschlossen. Relevante Dateien wurden übertragen.")

