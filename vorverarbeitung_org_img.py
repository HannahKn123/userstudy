import os
from PIL import Image

# Folder paths
input_folder = "berlin"
output_folder = "berlin"

# Create the output folder if it does not exist
os.makedirs(output_folder, exist_ok=True)

# Loop through all files in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith(".jpg") or filename.endswith(".png"):  # Adjust file extensions as needed
        # Load the image
        image_path = os.path.join(input_folder, filename)

        try:
            image = Image.open(image_path)
        except IOError:
            print(f"Error opening {filename}. Skipping this file.")
            continue

        # Double the image dimensions if reasonably sized
        max_size = 2000  # Adjust if needed to limit maximum dimensions
        new_width = min(image.width * 1, max_size)
        new_height = min(image.height * 1, max_size)
        resized_image = image.resize((new_width, new_height), Image.LANCZOS)

        # Convert to JPEG to ensure better compression
        resized_image = resized_image.convert("RGB")  # Ensures compatibility with JPEG format

        # Set the output path
        output_filename = os.path.splitext(filename)[0] + ".jpg"  # Save as JPEG
        output_path = os.path.join(output_folder, output_filename)

        # Compress the image to get it under 100 KB
        quality = 85  # Start with a moderate quality level

        # Save the image, compressing until the file size is under 100 KB
        while True:
            resized_image.save(output_path, format="JPEG", quality=quality, optimize=True)
            if os.path.getsize(output_path) < 100 * 1024:  # 100 KB limit
                break
            quality -= 5  # Reduce quality further if size is still above 100 KB
            if quality < 10:  # Stop if quality gets too low
                print(f"Could not reduce {filename} below 100 KB at acceptable quality.")
                break

        print(f"{filename} has been successfully resized and saved in {output_folder} with reduced file size.")

print("All images have been successfully resized and saved with reduced file size.")
