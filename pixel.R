# install.packages("imager")

library(imager)
library(dplyr)
library(readr)
library(ggplot2)

# Directories for input and output
annotations_dir <- '/content/annotiert_polygon_table'  # Folder containing CSV files
images_dir <- '/content/org_image'                     # Folder containing image files in .png format
output_dir_1 <- '/content/annotiert_blank_pixel_image' # Folder to save blank images with colored pixels
output_dir_2 <- '/content/annotiert_aus_polygon_image' # Folder to save images with polygons drawn
output_dir_3 <- '/content/annotiert_pixel_table'       # Folder to save pixel data CSVs

# Ensure the output directory exists
if (!dir.exists(output_dir_1)) dir.create(output_dir_1)
if (!dir.exists(output_dir_2)) dir.create(output_dir_2)
if (!dir.exists(output_dir_3)) dir.create(output_dir_3)

# Process each CSV file in the annotations directory
csv_files <- list.files(annotations_dir, pattern = '\\.csv$', full.names = TRUE)

for (csv_file in csv_files) {
  # Get the base name without extension
  base_name <- tools::file_path_sans_ext(basename(csv_file))
  cat("Processing:", base_name, "\n")
  
  # Remove part after the second last underscore
  image_base_name <- gsub("_(?:[^_]*$|[^_]*_[^_]*$)", "", base_name)
  
  # Remove 'annotated_' prefix if it exists
  image_base_name <- sub("^annotated_", "", image_base_name)
  
  # Define paths for the CSV and the corresponding image
  csv_path <- file.path(annotations_dir, csv_file)
  image_path <- file.path(images_dir, paste0(image_base_name, '.png'))
  
  # Check if the corresponding image file exists
  if (!file.exists(image_path)) {
    cat("Image file not found, skipping...\n")
    next
  }
  
  # Load CSV data
  polygon_data <- read_csv(csv_path) %>%
    mutate(across(c(x, y), as.numeric)) %>%
    drop_na()
  
  # Load the image
  image <- load.image(image_path)
  height <- dim(image)[1]
  width <- dim(image)[2]
  all_pixels <- data.frame()  # Data frame to store pixel data
  
  # Process each polygon in the CSV file
  unique_polygons <- unique(polygon_data$polygon_id)
  
  for (polygon_id in unique_polygons) {
    polygon_points <- polygon_data %>%
      filter(polygon_id == polygon_id) %>%
      select(x, y)
    
    # Create a mask with the polygon
    mask <- matrix(0, height, width)
    points <- as.matrix(polygon_points)
    poly <- as.polygon(points)
    mask[poly] <- 1
    
    # Find pixels inside the polygon and store pixel data
    indices <- which(mask == 1, arr.ind = TRUE)
    pixels <- data.frame(x = indices[, 2], y = indices[, 1], polygon_id = polygon_id)
    all_pixels <- bind_rows(all_pixels, pixels)
    
    # Draw polygon on the image
    plot(image)
    lines(poly$x, poly$y, col = 'red', lwd = 2)
  }
  
  # Define output paths
  output_csv_path <- file.path(output_dir_3, paste0(base_name, "_pixel_table.csv"))
  output_image_path <- file.path(output_dir_2, paste0(base_name, "_aus_polygon_image.png"))
  output_blank_image_path <- file.path(output_dir_1, paste0(base_name, "_blank_pixel_image.png"))
  
  # Save pixel data to CSV file
  write_csv(all_pixels, output_csv_path)
  cat("Pixel data saved to", output_csv_path, "\n")
  
  # Save image with polygons
  save.image(image, output_image_path)
  cat("Image with polygons saved to", output_image_path, "\n")
  
  # Create and save blank image with colored pixels
  blank_image <- imfill(width, height, val = c(0, 0, 0))  # Black background
  for (i in 1:nrow(all_pixels)) {
    x <- all_pixels$x[i]
    y <- all_pixels$y[i]
    blank_image[x, y, 1] <- 1  # Set pixel to red
  }
  
  # Save blank image with colored pixels
  save.image(blank_image, output_blank_image_path)
  cat("Blank image with colored pixels saved to", output_blank_image_path, "\n")
}
