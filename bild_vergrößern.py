import os
from PIL import Image

# Folder paths
input_folder = "1_org_image"
output_folder = "1_study_input"

# Create the output folder if it does not exist
os.makedirs(output_folder, exist_ok=True)

# Loop through all files in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith(".jpg") or filename.endswith(".png"):  # Adjust file extensions as needed
        # Load the image
        image_path = os.path.join(input_folder, filename)
        image = Image.open(image_path)

        # Double the image dimensions
        new_width = image.width * 2
        new_height = image.height * 2
        resized_image = image.resize((new_width, new_height), Image.LANCZOS)

        # Convert to JPEG to ensure better compression
        resized_image = resized_image.convert("RGB")  # Ensures compatibility with JPEG format

        # Set the output path
        output_filename = os.path.splitext(filename)[0] + ".jpg"  # Save as JPEG
        output_path = os.path.join(output_folder, output_filename)

        # Compress the image to get it under 20 KB
        quality = 85  # Start with a moderate quality level

        # Save the image, compressing until the file size is under 20 KB
        while True:
            resized_image.save(output_path, format="JPEG", quality=quality, optimize=True)
            if os.path.getsize(output_path) < 20 * 1024:  # 20 KB limit
                break
            quality -= 5  # Reduce quality further if size is still above 20 KB
            if quality < 10:  # Stop if quality gets too low
                break

        print(f"{filename} has been successfully resized and saved in {output_folder} with reduced file size.")

print("All images have been successfully resized and saved with reduced file size.")
