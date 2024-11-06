import pandas as pd
import numpy as np
import cv2
import os
import matplotlib.pyplot as plt


# Directories for input and output
annotations_dir = '1_download_study/download_polygon_table'  # Folder containing CSV files
images_dir = '1_study_input'  # Folder containing image files in .png format
output_dir_1 = '1_auswertung_results/annotiert_blank_pixel_image'  # Folder to save results
output_dir_2 = '1_auswertung_results/annotiert_aus_polygon_image'
output_dir_3 = '1_auswertung_results/annotiert_pixel_table'

# Process each CSV file in the annotations directory
for csv_file in os.listdir(annotations_dir):
    if csv_file.endswith('.csv'):
        # Get the base name without extension
        base_name = os.path.splitext(csv_file)[0]

        # Remove the part after the SECOND last underscore
        image_base_name = '_'.join(base_name.split('_')[:-1])  # Removes everything after the last "_"
        image_base_name = '_'.join(image_base_name.split('_')[:-1])  # Removes everything after the last "_"
        print(image_base_name)

        new_filename = "_".join(image_base_name.split("_", 2)[1:])
        print(new_filename)

        # Define the paths for the CSV and the corresponding image
        csv_path = os.path.join(annotations_dir, csv_file)
        image_path = os.path.join(images_dir, f'{new_filename}.png')  # Image file with .png extension

        # Check if the corresponding image file exists
        if not os.path.exists(image_path):
            print(f"Image file {image_path} not found, skipping...")
            continue

        # Load the CSV data
        polygon_data = pd.read_csv(csv_path)

        # Ensure coordinates are numeric
        polygon_data['x'] = pd.to_numeric(polygon_data['x'], errors='coerce')
        polygon_data['y'] = pd.to_numeric(polygon_data['y'], errors='coerce')

        # Drop rows with non-numeric coordinates
        polygon_data = polygon_data.dropna(subset=['x', 'y'])

        # Load the image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Could not load image at {image_path}, skipping...")
            continue

        height, width = image.shape[:2]
        all_pixels = []  # List to store pixel data

        # Process each polygon in the CSV file
        for polygon_id, group in polygon_data.groupby('polygon_id'):
            # Get polygon points
            x_coords = group['x'].astype(int).values
            y_coords = group['y'].astype(int).values
            pts = np.array(list(zip(x_coords, y_coords)), np.int32).reshape((-1, 1, 2))

            # Create mask for polygon
            mask = np.zeros((height, width), dtype=np.uint8)
            cv2.fillPoly(mask, [pts], 1)

            # Find pixels inside the polygon
            indices = np.column_stack(np.where(mask == 1))

            # Append pixel data with polygon_id
            for y, x in indices:
                all_pixels.append({'x': x, 'y': y, 'polygon_id': polygon_id})

            # Draw polygon on image
            cv2.polylines(image, [pts], isClosed=True, color=(0, 0, 255), thickness=2)  # Red color

        # Create output paths for this file
        output_csv_path = os.path.join(output_dir_3, f'{base_name}_pixel_table.csv')
        output_image_path = os.path.join(output_dir_2, f'{base_name}_aus_polygon_image.jpg')
        output_blank_image_path = os.path.join(output_dir_1, f'{base_name}_blank_pixel_image.jpg')

        # Save pixel data to CSV file
        output_df = pd.DataFrame(all_pixels)
        output_df.to_csv(output_csv_path, index=False)
        print(f"Pixel data saved to {output_csv_path}")

        # Save image with polygons drawn
        cv2.imwrite(output_image_path, image)
        print(f"Image with polygons saved to {output_image_path}")

        # Display the image with polygons using matplotlib
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))  # Convert BGR to RGB for correct colors in matplotlib
        plt.axis('off')  # Hide axis for better view
        #plt.show()

        # Part 2: Create and save the blank image with colored pixels
        blank_image = np.zeros((height, width, 3), dtype=np.uint8)
        color = (0, 0, 255)  # Red in BGR format

        # Load the pixel data from the CSV file
        pixel_data = pd.read_csv(output_csv_path)

        # Iterate over each row in the CSV and color the corresponding pixel
        for _, row in pixel_data.iterrows():
            x, y = int(row['x']), int(row['y'])
            if 0 <= y < height and 0 <= x < width:
                blank_image[y, x] = color

        # Save the blank image with colored pixels
        cv2.imwrite(output_blank_image_path, blank_image)
        print(f"Blank image with colored pixels saved to {output_blank_image_path}")

        # Display the blank image with colored pixels using matplotlib
        plt.imshow(cv2.cvtColor(blank_image, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        #plt.show()

