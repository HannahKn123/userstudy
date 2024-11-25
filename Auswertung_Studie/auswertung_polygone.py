import pandas as pd
import os
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
from matplotlib import patches

# Directories for input
# Control
c_csv = './study_output_data/control/control_csv'
c_org_img = './input_study_data/control/all'

# Treatment
t_csv = './study_output_data/treatment/treatment_csv'
t_xai_img = './input_study_data/treatment/all'

# Directories for output
# Control
c_blanko_pixel = 'auswertung_study_output_data/control/blanko_pixel'
c_org_pixel = 'auswertung_study_output_data/control/org_pixel'
c_xai_pixel = 'auswertung_study_output_data/control/xai_pixel'
c_pixel = 'auswertung_study_output_data/control/human_pixel_csv'

# Treatment
t_blanko_pixel = 'auswertung_study_output_data/treatment/blanko_pixel'
t_org_pixel = 'auswertung_study_output_data/treatment/org_pixel'
t_xai_pixel = 'auswertung_study_output_data/treatment/xai_pixel'
t_pixel = 'auswertung_study_output_data/treatment/human_pixel_csv'

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
os.makedirs(xai_pixel, exist_ok=True)
os.makedirs(human_pixel_csv, exist_ok=True)

# Function to extract the name part from a CSV file name
def extract_name_from_csv(csv_name):
    parts = csv_name.split("_")
    if len(parts) > 7:
        return "_".join(parts[2:7])
    return None

# Iterate over all CSV files in the folder
for csv_file_name in os.listdir(csv):

    if csv_file_name.endswith(".csv"):

        extracted_name = extract_name_from_csv(csv_file_name)

        if extracted_name:
            xai_image_file_name = f"{extracted_name}.png"
            org_image_file_name = f"{extracted_name}.png"
            xai_image_path = os.path.join(img_xai, xai_image_file_name)
            org_image_path = os.path.join(img_org, org_image_file_name) if img_org else None

            if os.path.exists(xai_image_path):
                csv_file_path = os.path.join(csv, csv_file_name)
                data = pd.read_csv(csv_file_path)

                # Annotate and save the XAI image
                original_image = Image.open(xai_image_path)
                width, height = original_image.size
                fig, ax = plt.subplots(figsize=(width / 100, height / 100), dpi=100)
                ax.imshow(original_image)
                for polygon_id, group in data.groupby('polygon_id'):
                    polygon_points = group[['x', 'y']].values
                    polygon = patches.Polygon(
                        polygon_points,
                        closed=True,
                        fill=True,
                        edgecolor='orange',
                        facecolor='orange',
                        alpha=0.4,
                        linewidth=3
                    )
                    ax.add_patch(polygon)
                ax.axis('off')
                fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
                xai_annotated_path = os.path.join(xai_pixel, f"{os.path.splitext(csv_file_name)[0]}_xai.png")
                fig.savefig(xai_annotated_path, dpi=width / fig.get_size_inches()[0], bbox_inches='tight', pad_inches=0)
                plt.close(fig)
                print(f"Saved XAI annotated image for {csv_file_name} to {xai_pixel}")

                # Annotate and save the original image (if exists)
                if org_image_path and os.path.exists(org_image_path):
                    original_image = Image.open(org_image_path)
                    fig, ax = plt.subplots(figsize=(width / 100, height / 100), dpi=100)
                    ax.imshow(original_image)
                    for polygon_id, group in data.groupby('polygon_id'):
                        polygon_points = group[['x', 'y']].values
                        polygon = patches.Polygon(
                            polygon_points,
                            closed=True,
                            fill=True,
                            edgecolor='blue',
                            facecolor='blue',
                            alpha=0.4,
                            linewidth=3
                        )
                        ax.add_patch(polygon)
                    ax.axis('off')
                    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
                    org_annotated_path = os.path.join(org_pixel, f"{os.path.splitext(csv_file_name)[0]}_org.png")
                    fig.savefig(org_annotated_path, dpi=width / fig.get_size_inches()[0], bbox_inches='tight', pad_inches=0)
                    plt.close(fig)
                    print(f"Saved original annotated image for {csv_file_name} to {org_pixel}")

                # Create and save blank image with original dimensions
                blank_image = Image.new('RGB', (width, height), color=(255, 255, 255))
                draw = ImageDraw.Draw(blank_image)
                all_pixels = []

                for polygon_id, group in data.groupby('polygon_id'):
                    polygon_points = group[['x', 'y']].values
                    draw.polygon([(x, y) for x, y in polygon_points], outline=(255, 0, 0), fill=(255, 0, 0))
                    all_pixels.extend([(int(x), int(y)) for x, y in polygon_points])

                blank_image_path = os.path.join(blanko_pixel, f"{os.path.splitext(csv_file_name)[0]}_blank.png")
                blank_image.save(blank_image_path)
                print(f"Saved blank image for {csv_file_name} to {blanko_pixel}")

                # Create a DataFrame for pixel data
                pixel_data = pd.DataFrame(all_pixels, columns=['x', 'y'])

                # Save the pixel data to an Excel file with a proper extension
                excel_output_path = os.path.join(human_pixel_csv, f"{os.path.splitext(csv_file_name)[0]}.xlsx")
                pixel_data.to_excel(excel_output_path, index=False)
                print(f"Saved pixel data for {csv_file_name} to {human_pixel_csv}")

            else:
                print(f"XAI image not found for {csv_file_name} (Expected name: {xai_image_file_name})")
        else:
            print(f"Could not extract name from {csv_file_name}")
