library(shiny)
library(shinyjs) 
library(tibble)
library(magick)
library(shiny)
library(magick)
library(shinyjs)
library(readr)
library(tidyverse)
library(shiny)
library(shinyjs)
library(shinyWidgets)
library(ggplot2)  # or library(plotly)
library(magick)
library(shiny)
library(magick)
library(dplyr)
library(purrr)
library(ggplot2)  # Optional

#https://cloudstore.uni-ulm.de/remote.php/dav/files/zbc57/annotation_result/

# Adjusted save_to_nextcloud function for testing
save_to_nextcloud <- function(file_path, cloud_folder, file_name, username, password) {
  
  # Print file path and URL for debugging
  print(paste("Local file path:", file_path))
  print(paste("File name:", file_name))
  
  # Construct Nextcloud URL (example structure)
  url <- paste0("https://cloudstore.uni-ulm.de/remote.php/dav/files/zbc57/", cloud_folder, "/", URLencode(file_name))
  print(paste("Nextcloud URL:", url))
  
  # Perform the PUT request with httr for testing
  result <- httr::PUT(
    url,
    httr::authenticate(username, password),
    body = httr::upload_file(file_path)
  )
  
  # Check for successful status
  if (httr::status_code(result) == 201) {
    print("File uploaded successfully.")
  } else {
    print(httr::content(result))
  }
}
