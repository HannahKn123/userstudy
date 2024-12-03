from PIL import Image, ImageDraw
import pandas as pd
import os

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



def get_pixels_in_polygon(polygon_points, width, height):
    # Leere Maske erstellen
    mask = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(mask)

    # Polygon auf Maske zeichnen
    # Koordinaten zu Ganzzahlen umwandeln
    flat_points = [(int(x), int(y)) for x, y in polygon_points]
    draw.polygon(flat_points, outline=1, fill=1)

    # Pixel innerhalb des Polygons extrahieren
    pixels = [(x, y) for y in range(height) for x in range(width) if mask.getpixel((x, y)) == 1]
    return pixels



# Function to extract the name part from a CSV file name
def extract_name_from_csv(csv_name):
    parts = csv_name.split("_")
    if len(parts) > 7:
        return "_".join(parts[2:7])
    return None


# Iteration über alle CSV-Dateien
for csv_file_name in os.listdir(csv):
    if csv_file_name.endswith(".csv"):
        extracted_name = extract_name_from_csv(csv_file_name)
        if extracted_name:
            xai_image_file_name = f"{extracted_name}.png"
            xai_image_path = os.path.join(img_xai, xai_image_file_name)

            if os.path.exists(xai_image_path):
                csv_file_path = os.path.join(csv, csv_file_name)
                data = pd.read_csv(csv_file_path)

                # Originalbild laden, um Dimensionen zu erhalten
                original_image = Image.open(xai_image_path)
                width, height = original_image.size

                # Alle Pixel innerhalb der Polygone sammeln
                all_pixels = []
                for polygon_id, group in data.groupby('polygon_id'):
                    polygon_points = group[['x', 'y']].values.tolist()  # Liste von [x, y]-Paaren
                    polygon_points = [(int(x), int(y)) for x, y in polygon_points]  # In Ganzzahlen umwandeln
                    pixels_in_polygon = get_pixels_in_polygon(polygon_points, width, height)
                    all_pixels.extend(pixels_in_polygon)

                # Pixel als DataFrame speichern
                pixel_data = pd.DataFrame(all_pixels, columns=['x', 'y'])
                excel_output_path = os.path.join(human_pixel_csv, f"{os.path.splitext(csv_file_name)[0]}.xlsx")
                pixel_data.to_excel(excel_output_path, index=False)
                print(f"Gespeicherte Pixel-Daten für {csv_file_name} in {human_pixel_csv}")
            else:
                print(f"XAI-Bild nicht gefunden für {csv_file_name} (Erwarteter Name: {xai_image_file_name})")
        else:
            print(f"Name konnte nicht aus {csv_file_name} extrahiert werden")