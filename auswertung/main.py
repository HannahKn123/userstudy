from PIL import Image, ImageDraw
import pandas as pd
import os

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
def process_csv_file(csv_file_path, xai_image_path, output_dir):
    # CSV-Daten laden
    data = pd.read_csv(csv_file_path)

    # Originalbild laden, um Dimensionen zu erhalten
    original_image = Image.open(xai_image_path)
    width, height = original_image.size

    # Alle Pixel innerhalb der Polygone sammeln
    all_pixels = []
    for polygon_id, group in data.groupby('polygon_id'):
        polygon_points = group[['x', 'y']].values.tolist()
        pixels_in_polygon = get_pixels_in_polygon(polygon_points, width, height)
        all_pixels.extend(pixels_in_polygon)

    # Pixel als DataFrame speichern
    pixel_data = pd.DataFrame(all_pixels, columns=['x', 'y'])
    excel_output_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(csv_file_path))[0]}.xlsx")
    pixel_data.to_excel(excel_output_path, index=False)

    print(f"Gespeicherte Pixel-Daten für {csv_file_path} in {output_dir}")

# Funktion zur Extraktion des Dateinamens
def extract_name_from_csv(csv_name):
    parts = csv_name.split("_")
    if len(parts) > 7:
        return "_".join(parts[2:7])
    return None




# Funktion, um Pixel auf zugehörigen Bildern zu markieren
def mark_pixels_for_csv_files(csv_dir, img_dir, output_dir):
    for csv_file_name in os.listdir(csv_dir):
        if csv_file_name.endswith(".csv"):
            # Extrahiere Namen aus der CSV-Datei
            extracted_name = extract_name_from_csv(csv_file_name)
            if extracted_name:
                # Erstelle den zugehörigen Bildnamen
                img_file_name = f"{extracted_name}.png"
                image_path = os.path.join(img_dir, img_file_name)
                csv_file_path = os.path.join(csv_dir, csv_file_name)

                if os.path.exists(xai_image_path):
                    # Markiere die Pixel auf dem Bild
                    pixel_output_image = os.path.join(output_dir, f"marked_{extracted_name}.png")
                    pixel_data_output = os.path.join(output_dir, f"{os.path.splitext(csv_file_name)[0]}.xlsx")

                    # Verarbeite die CSV und markiere Pixel
                    process_csv_file(csv_file_path, xai_image_path, output_dir)
                    highlight_pixels_on_image(xai_image_path, pixel_data_output, pixel_output_image)
                else:
                    print(f"XAI-Bild nicht gefunden für {csv_file_name} (Erwarteter Name: {xai_image_file_name})")
            else:
                print(f"Name konnte nicht aus {csv_file_name} extrahiert werden")
















# Hauptmethode
def main():
    # Directories for input
    # Control
    c_csv = './study_output_data/control/control_csv'
    c_org_img = './input_study_data/control/all'

    # Treatment
    t_csv = './study_output_data/treatment/treatment_csv'
    t_xai_img = './input_study_data/treatment/all'

    # Directories for output
    # Control
    c_blanko_pixel = 'auswertung_output_data/control/blanko_pixel'
    c_org_pixel = 'auswertung_output_data/control/org_pixel'
    c_xai_pixel = 'auswertung_output_data/control/xai_pixel'
    c_pixel = 'auswertung_output_data/control/human_pixel_csv'

    # Treatment
    t_blanko_pixel = 'auswertung_output_data/treatment/blanko_pixel'
    t_org_pixel = 'auswertung_output_data/treatment/org_pixel'
    t_xai_pixel = 'auswertung_output_data/treatment/xai_pixel'
    t_pixel = 'auswertung_output_data/treatment/human_pixel_csv'

    # Define whether to use "treatment" or "control"
    t_or_c = "t"  # Change to "c" for control
    csv = t_csv if t_or_c == "t" else c_csv
    img_xai = t_xai_img if t_or_c == "t" else c_org_img
    img_org = c_org_img if t_or_c == "c" else None
    blanko_pixel = t_blanko_pixel if t_or_c == "t" else c_blanko_pixel
    org_pixel = t_org_pixel if t_or_c == "t" else c_org_pixel
    xai_pixel = t_xai_pixel if t_or_c == "t" else c_xai_pixel
    human_pixel_csv = t_pixel if t_or_c == "t" else c_pixel

    # Create the output directories if they don't exist
    os.makedirs(blanko_pixel, exist_ok=True)
    os.makedirs(org_pixel, exist_ok=True)
    os.makedirs(xai_pixel, exist_ok=True)
    os.makedirs(human_pixel_csv, exist_ok=True)


    # Alle CSV-Dateien verarbeiten
    for csv_file_name in os.listdir(csv_dir):
        if csv_file_name.endswith(".csv"):
            extracted_name = extract_name_from_csv(csv_file_name)
            if extracted_name:
                xai_image_file_name = f"{extracted_name}.png"
                xai_image_path = os.path.join(img_dir, xai_image_file_name)
                csv_file_path = os.path.join(csv_dir, csv_file_name)

                if os.path.exists(xai_image_path):
                    process_csv_file(csv_file_path, xai_image_path, output_dir)
                else:
                    print(f"XAI-Bild nicht gefunden für {csv_file_name} (Erwarteter Name: {xai_image_file_name})")
            else:
                print(f"Name konnte nicht aus {csv_file_name} extrahiert werden")





# Skript ausführen
if __name__ == "__main__":
    main()
