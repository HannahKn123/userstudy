from PIL import Image, ImageDraw
import pandas as pd
import os
import csv
import pandas as pd
from shapely.geometry import Polygon, Point
import os
import shutil


def extract_name_from_csv(csv_name):
    # Suche nach der Position des Wortes 'img'
    if 'img' in csv_name:
        start_index = csv_name.find('img')
        # Schneide den String ab dem Wort 'img'
        cropped_name = csv_name[start_index:]
        # Teile den abgeschnittenen String anhand von Unterstrichen
        parts = cropped_name.split("_")
        # Wenn es mehr als 7 Teile gibt, kombiniere die ersten 7
        if len(parts) >= 7:
            return "_".join(parts[:5])
    return None


# Funktion zur Pixel-Extraktion innerhalb eines Polygons
def get_pixels_in_polygon(polygon_points, width, height):
    # Leere Maske erstellen
    mask = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(mask)

    # Polygon auf Maske zeichnen (Koordinaten in Ganzzahlen umwandeln)
    flat_points = [(int(x), int(y)) for x, y in polygon_points]
    draw.polygon(flat_points, outline=1, fill=1)

    # Pixel innerhalb des Polygons extrahieren
    pixels = [(x, y) for y in range(height) for x in range(width) if mask.getpixel((x, y)) == 1]
    return pixels


# Funktion zur Verarbeitung einer einzelnen CSV-Datei
def process_csv_file(csv_file_path, image_path, output_dir, base_name):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Load CSV data
    data = pd.read_csv(csv_file_path)

    # Load original image to get dimensions
    original_image = Image.open(image_path)
    width, height = original_image.size

    # Collect all pixels within the polygons
    all_pixels = []
    for polygon_id, group in data.groupby('polygon_id'):
        polygon_points = group[['x', 'y']].values.tolist()
        pixels_in_polygon = get_pixels_in_polygon(polygon_points, width, height)
        all_pixels.extend(pixels_in_polygon)

    # Save pixels as a DataFrame
    pixel_data = pd.DataFrame(all_pixels, columns=['x', 'y'])
    pixel_file_path = os.path.join(output_dir, f"{base_name}.xlsx")
    # Save DataFrame to Excel
    pixel_data.to_excel(pixel_file_path, index=False)
    print(f"Gespeicherte Pixel-Daten für {base_name} in {output_dir}")

    return pixel_file_path

def highlight_pixels_on_image(pixel_file_path, image_path, output_dir, base_name, highlight_color=(255, 165, 0, 128)):
    # Bild laden und in RGBA konvertieren
    image = Image.open(image_path).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))  # Transparentes Overlay
    draw = ImageDraw.Draw(overlay)

    # Pixel-Daten laden
    pixel_data = pd.read_excel(pixel_file_path)

    # Pixel hervorheben
    for _, row in pixel_data.iterrows():
        x, y = int(row['x']), int(row['y'])
        draw.point((x, y), fill=highlight_color)

    # Overlay mit dem Originalbild kombinieren
    combined = Image.alpha_composite(image, overlay)

    # Ergebnis speichern
    output_path = os.path.join(output_dir, f"{base_name}.png")
    combined.save(output_path)

    print(f"Hervorgehobenes Bild gespeichert unter {output_path}")

def attentioncheck_list_to_csv(folder_path, output_csv_path):
    extracted_names = []

    # Gehe alle Dateien im angegebenen Ordner durch
    for file_name in os.listdir(folder_path):
        # Stelle sicher, dass es sich um eine Datei handelt
        if os.path.isfile(os.path.join(folder_path, file_name)):
            try:
                # Suche nach dem ersten Unterstrich
                first_underscore_index = file_name.index('_')  # Finde den ersten Unterstrich
                # Schneide ab dem ersten Unterstrich und entferne .txt, falls vorhanden
                extracted_part = file_name[first_underscore_index + 1:]
                if extracted_part.endswith('.txt'):
                    extracted_part = extracted_part[:-4]  # Entferne .txt
                extracted_names.append(extracted_part)
            except ValueError:
                # Wenn "_" nicht gefunden wird, überspringe diese Datei
                continue

    # Speichere die extrahierten Namen in einer CSV-Datei
    with open(output_csv_path, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Extracted Names'])  # Kopfzeile
        for name in extracted_names:
            writer.writerow([name])

    print(f"Die extrahierten Namen wurden in {output_csv_path} gespeichert.")

def filter_and_copy_images(excel_path, image_folder, output_folder):
    # 1. Excel lesen
    df = pd.read_csv(excel_path)

    # Extrahierte Namen aus der Excel-Tabelle
    failed_names = df['Extracted Names'].tolist()  # Passe Extracted Names an die tatsächliche Spaltenüberschrift an

    # Sicherstellen, dass der Zielordner existiert
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 2. Bilder im Ordner durchgehen
    for image_name in os.listdir(image_folder):
        image_path = os.path.join(image_folder, image_name)

        # Stelle sicher, dass es sich um eine Datei handelt
        if os.path.isfile(image_path):
            # Namen nach dem ersten "_" und vor "img" extrahieren
            try:
                first_underscore_index = image_name.index('_') + 1
                img_index = image_name.index('_test', first_underscore_index)
                extracted_name = image_name[first_underscore_index:img_index]
                print(extracted_name)

            except ValueError:
                continue  # Überspringe Dateien ohne "_" oder "img"

            # 3. Check: Ist der extrahierte Name in der Excel-Liste?
            if extracted_name in failed_names:
                # Kopiere die Datei in den neuen Ordner
                image_name = create_base_name2(image_name)
                shutil.copy(image_path, os.path.join(output_folder, image_name))

    print(f"Bilder wurden erfolgreich in {output_folder} kopiert.")

def truncate_filename(filename):
    # Split the filename by underscores
    parts = filename.rsplit(".", 0)
    # Keep only the part before the fourth last underscore
    truncated = parts[0]
    return truncated

def create_base_name(text):
    text = text.replace("treatment", "t")
    text = text.replace("control", "c")
    text = text.replace(".csv", "")
    return text

def create_base_name2(text):
    text = text.replace("treatment", "t")
    text = text.replace("control", "c")
    return text

def extract_userID(text):
    text = text.replace("treatment", "t")
    text = text.replace("control", "c")
    text = text.replace("_uebung.csv", "")
    return text



# Hauptmethode
def main():
    # Define whether to use "treatment" or "control"
    t_or_c = ["c", "t"]  # Change to "c" for control

    # Directories for input
    # Control
    c_csv = './study_output_data/control/control_csv'
    c_org_img = './input_study_data/control/all'

    # Treatment
    t_csv = './study_output_data/treatment/treatment_csv'
    t_xai_img = './input_study_data/treatment/all'

    # Directories for output
    # Control
    c_org_pixel = 'auswertung_study_output_data/control/org_pixel'
    c_xai_pixel = 'auswertung_study_output_data/control/xai_pixel'
    c_pixel = 'auswertung_study_output_data/control/human_pixel_csv'

    # Treatment
    t_org_pixel = 'auswertung_study_output_data/treatment/org_pixel'
    t_xai_pixel = 'auswertung_study_output_data/treatment/xai_pixel'
    t_pixel = 'auswertung_study_output_data/treatment/human_pixel_csv'

    # Gefailte Bilder in Ordner ablegen
    control_image_folder = 'study_output_data/control/control_attention_image'
    control_output_folder = 'auswertung_study_output_data/attention_check/control_failed'
    treatment_image_folder = 'study_output_data/treatment/treatment_attention_image'
    treatment_output_folder = 'auswertung_study_output_data/attention_check/treatment_failed'

    # UserID Liste
    control_fail = "./study_output_data/control/control_failures"
    treatment_fail = "./study_output_data/treatment/treatment_failures"
    c_attention_check_output_path = "./auswertung_study_output_data/attention_check/c_failed_attentioncheck.csv"
    t_attention_check_output_path = "./auswertung_study_output_data/attention_check/t_failed_attentioncheck.csv"

    for i in ["c", "t"]:
        t_or_c = i

        ######################################### AuswertungPixel  #########################################################
        csv = t_csv if t_or_c == "t" else c_csv
        img_org = c_org_img
        img_xai = t_xai_img

        org_pixel = t_org_pixel if t_or_c == "t" else c_org_pixel
        xai_pixel = t_xai_pixel if t_or_c == "t" else c_xai_pixel
        human_pixel_csv = t_pixel if t_or_c == "t" else c_pixel

        for csv_file_name in os.listdir(csv):
            if csv_file_name.endswith(".csv"):
                base_name = create_base_name(csv_file_name)
                extracted_name = extract_name_from_csv(csv_file_name)

                if extracted_name:
                    image_file_name = f"{extracted_name}.png"
                    org_image_path = os.path.join(img_org, image_file_name)
                    xai_image_path = os.path.join(img_xai, image_file_name)
                    csv_file_path = os.path.join(csv, csv_file_name)

                    if os.path.exists(org_image_path) & os.path.exists(xai_image_path):
                        # pixel in csv speichern
                        pixel_file_path = process_csv_file(csv_file_path, org_image_path, human_pixel_csv, base_name)
                        #pixel auf Bilder malen und speichern
                        highlight_pixels_on_image(pixel_file_path, org_image_path, org_pixel, base_name)
                        highlight_pixels_on_image(pixel_file_path, xai_image_path, xai_pixel, base_name)
                    else:
                        print(f"XAI-Bild nicht gefunden für {csv_file_name} (Erwarteter Name: {image_file_name})")
                else:
                    print(f"Name konnte nicht aus {csv_file_name} extrahiert werden")
            else:
                print(f"keine csv")



        ######################################### Auswertung Attention Check ###############################################
        fail = treatment_fail if t_or_c == "t" else control_fail
        attention_check_output_path = t_attention_check_output_path if t_or_c == "t" else c_attention_check_output_path

        attentioncheck_list_to_csv(fail, attention_check_output_path)

        image_folder = treatment_image_folder if t_or_c == "t" else control_image_folder
        output_folder = treatment_output_folder if t_or_c == "t" else control_output_folder

        filter_and_copy_images(attention_check_output_path, image_folder, output_folder)


        ######################################### Auswertung Übung #########################################################

        t_uebung = './study_output_data/treatment/treatment_uebung_csv'
        c_uebung = './study_output_data/control/control_uebung_csv'

        uebung = t_uebung if t_or_c == "t" else c_uebung
        uebung_image = "../userstudy_deploy_control/www/ueben_img.png"

        uebung_human_pixel_img = "auswertung_study_output_data/uebung/uebung_human_pixel_img"
        uebung_human_pixel_csv = "auswertung_study_output_data/uebung/uebung_human_pixel_csv"


        for csv_file_name in os.listdir(uebung):
            if csv_file_name.endswith(".csv"):
                UserID = extract_userID(csv_file_name)
                csv_file_path = os.path.join(uebung, csv_file_name)

                pixel_file_path = process_csv_file(csv_file_path, uebung_image, uebung_human_pixel_csv, UserID)
                highlight_pixels_on_image(pixel_file_path, uebung_image, uebung_human_pixel_img, UserID)
            else:
                print(f"keine csv")

        print("*************done", t_or_c)


# Skript ausführen
if __name__ == "__main__":
    main()
