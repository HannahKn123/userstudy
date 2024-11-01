library(shiny)
library(shinyjs)
library(tibble)
library(magick)
library(readr)
library(tidyverse)
library(shinyWidgets)
library(dplyr)
library(purrr)
library(ggplot2)

# Lade helper.R für die save_to_nextcloud Funktion
source("helper.R")



server <- function(input, output, session) {
  closeAllConnections()
  shinyjs::useShinyjs()
  
  # Nextcloud settings
  img_cloud_folder <- "annotation_result"
  csv_cloud_folder <- "annotation_result"
  username <- "zbc57"
  password <- "IBA2024Nein#"
  
  # Load images from directory
  img_dir <- "xai_image/"
  all_images <- list.files(img_dir, pattern = "\\.png$", full.names = TRUE)
  selected_images <- sample(all_images, 10)  # Randomly select 10 images
  
  # Function to extract class name from the filename
  extract_class_from_filename <- function(filename) {
    parts <- strsplit(basename(filename), "_")[[1]]
    class_name <- parts[length(parts)]
    class_name <- gsub("\\.png", "", class_name)
    return(class_name)
  }
  
  # Reactive values for page navigation, coordinates, and polygon IDs
  page <- reactiveVal(1)
  coords <- reactiveVal(value = tibble(x = numeric(), y = numeric(), polygon_id = integer(), name = character()))
  polygon_id <- reactiveVal(1)
  
  # Reactive value to store selected city for each image
  selected_city <- reactiveVal(rep("", 10))  # Initialize for 10 images
  
  # UI rendering for each page
  output$page_content <- renderUI({
    current_page <- page()
    if (current_page == 1) {  # Initial instructions page
      tagList(
        h3("Welcome to the 'Guess the City' study!"),
        p("The goal of this study is to explore how artificial intelligence (AI) and humans can work together effectively. To do this, we’ll show you 10 images of random locations from one of four cities: Berlin, Hamburg, Jerusalem, and Tel Aviv. Each image is a Google Maps photo from one of these cities."),
        h4("Here’s what you’ll do:"),
        tags$ol(
          tags$li(strong("City Classification:"), " Look at each image carefully and decide which of the four cities you think it shows. Our AI model has already made its own prediction, which we will share with you. Keep in mind that AI models can make mistakes, so the AI's choice may not always be correct."),
          tags$li(strong("Marking Important Areas:"), " After seeing the AI's prediction, you’ll also get a heat map highlighting which parts of the image influenced the AI's decision. Darker areas on the map indicate features that were more important to the AI. Your task is to mark the areas that are most important for your own decision. If you agree with the AI, you can mark similar areas, or you can mark completely different areas based on your perspective.")
        ),
        p("To proceed with the study, it’s essential that you complete both the classification and the marking tasks for each image."),
        h4("Bonus Opportunity:"),
        p("You can earn an additional payment by providing precise markings and achieving at least 90% correct classifications. This bonus will be an extra x cents."),
        p("Thank you for your participation!"),
        div(style = "text-align: center; margin-top: 20px;",
            actionButton("next_page", "Start Annotating", icon = icon("arrow-right"), class = "btn-primary")
        )
      )
    } else if (current_page >= 2 && current_page <= 11) {  # Annotation pages
      i <- current_page - 1  # Image index
      class_number <- extract_class_from_filename(selected_images[i])
      image <- image_read(selected_images[i])
      
      # Get image dimensions for original size display
      img_info <- image_info(image)
      img_width <- img_info$width
      img_height <- img_info$height
      
      # UI layout with AI and human decision boxes
      tagList(
        div(style = "display: flex; flex-direction: column; gap: 40px; width: 100%; margin: 0 auto;"),
        div(class = "highlight-container",
            style = "background-color: #e0e0e0; border-radius: 8px; display: flex; padding: 10px; width: 100%; max-width: 1200px;",  
            h4("AI Decision"),
            div(class = "flex-container", 
                style = "display: flex; gap: 40px; width: 100%; align-items: stretch;",
                div(style = "background-color: #ffffff; border-radius: 8px; display: flex; flex: 1; flex-basis: 34%; padding: 15px; min-height: 70px;",  
                    div(style = "display: flex; text-align: left; width: 100%;",  
                        p("The AI recognized this image as taken in ", 
                          span(style = "color: #800080; font-weight: bold;", class_number), ".")
                    )
                ),
                div(style = "background-color: #ffffff; border-radius: 8px; display: flex; flex: 1; flex-basis: 66%; padding: 15px; min-height: 70px;",  
                    div(style = "display: flex; text-align: left; width: 100%;",  
                        p("The ", span(style = "color: #800080; font-weight: bold;", "highlighted areas"), 
                          " shown below were key factors in its decision.")
                    )
                )
            )
        ),
        div(class = "decision-container",
            style = "background-color: #e0e0e0; border-radius: 8px; display: flex; padding: 10px; width: 100%; max-width: 1200px;",  
            h4("Human Decision"),
            div(class = "flex-container", 
                style = "display: flex; gap: 40px; width: 100%; align-items: stretch;",  
                div(style = "background-color: #ffffff; border-radius: 8px; display: flex; flex: 1; flex-basis: 34%; padding: 15px; flex-direction: column;",  
                    div(style = "display: flex; flex-direction: column; width: 100%; height: 100%; gap: 50px;",  
                        p("Take a close look at the image. Do you agree with the AI’s classification of this image as Berlin, or would you assign it to a different city? Please ", strong(style = "color: #4169E1;", "select your choice"), " below."),
                        div(class = "btn-group-container", style = "display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; margin-top: 20px;",
                            actionButton(inputId = paste0("class_", i, "_tel_aviv"), label = "Tel Aviv", class = "btn", style = "width: 150px; text-align: center;"),
                            actionButton(inputId = paste0("class_", i, "_jerusalem"), label = "Jerusalem", class = "btn", style = "width: 150px; text-align: center;"),
                            actionButton(inputId = paste0("class_", i, "_hamburg"), label = "Hamburg", class = "btn", style = "width: 150px; text-align: center;"),
                            actionButton(inputId = paste0("class_", i, "_berlin"), label = "Berlin", class = "btn", style = "width: 150px; text-align: center;")
                        )
                        
                    )
                ),
                div(style = "background-color: #ffffff; border-radius: 8px; display: flex; flex: 1; flex-basis: 66%; padding: 15px; flex-direction: column;",  
                    div(style = "width: 100%; text-align: left; margin-bottom: 10px;",
                        p("Review these highlighted areas carefully. Which parts of the image led you to your decision? Please ", span(style = "color: #4169E1; font-weight: bold;", "mark these key areas as precisely as possible"), " using the annotation tool. Before proceeding, ensure that you’ve marked all features you consider important.")
                    ),
                    div(style = "flex-grow: 1; display: flex; align-items: center; justify-content: center; width: 100%;",  
                        plotOutput(paste0("imagePlot", i), click = paste0("image_click_", i), 
                                   width = paste0(img_width, "px"), height = paste0(img_height, "px"))
                    ),
                    div(style = "display: flex; gap: 10px; margin-top: 5px; justify-content: center;",  
                        actionButton(paste0("clear_", i), "Clear All Annotations", icon = icon("trash"), 
                                     class = "btn-secondary", style = "padding: 5px 7px; font-size: 12px;"),  
                        actionButton(paste0("delete_last_polygon", i), "Delete Last Polygon", icon = icon("trash"), 
                                     class = "btn-secondary", style = "padding: 5px 7px; font-size: 12px;"),  
                        actionButton(paste0("end_polygon_", i), "Complete Polygon", icon = icon("check"), 
                                     class = "btn-secondary", style = "padding: 5px 7px; font-size: 12px;"),  
                        actionButton("next_page", "Next Image", icon = icon("arrow-right"), 
                                     class = "btn-primary", style = "padding: 5px 7px; font-size: 12px;")  
                    )
                )
            )
        )
        
      )
      
    } else {  # Completion page after annotations
      tagList(
        h3("Thank you for completing the study!"),
        p("All annotated images have been saved. Thank you for participating in the study! We will review your responses shortly and confirm your participation."),
        actionButton("close_app", "Close", class = "btn-primary", style = "margin-top: 20px;")
      )
    }
  })
  
  # Observers for annotation functionality and handling clicks
  lapply(1:10, function(i) {
    observeEvent(input[[paste0("class_", i, "_tel_aviv")]], {
      city_list <- selected_city()
      city_list[i] <- "Tel Aviv"
      selected_city(city_list)
    })
    observeEvent(input[[paste0("class_", i, "_jerusalem")]], {
      city_list <- selected_city()
      city_list[i] <- "Jerusalem"
      selected_city(city_list)
    })
    observeEvent(input[[paste0("class_", i, "_hamburg")]], {
      city_list <- selected_city()
      city_list[i] <- "Hamburg"
      selected_city(city_list)
    })
    observeEvent(input[[paste0("class_", i, "_berlin")]], {
      city_list <- selected_city()
      city_list[i] <- "Berlin"
      selected_city(city_list)
    })
    
    observeEvent(input[[paste0("image_click_", i)]], {
      current_coords <- coords()
      polygon_id_val <- polygon_id()
      
      # Store the coordinates directly for display with scaling applied
      adjusted_x <- input[[paste0("image_click_", i)]]$x
      adjusted_y <- input[[paste0("image_click_", i)]]$y
      
      current_coords <- add_row(
        current_coords,
        x = adjusted_x,
        y = adjusted_y,
        polygon_id = polygon_id_val,
        name = paste("polygon", i)
      )
      coords(current_coords)
    })
    
    # Render the original-size plot with annotations
    output[[paste0("imagePlot", i)]] <- renderPlot({
      img <- image_read(selected_images[i])
      img_raster <- as.raster(img)
      
      # Get image dimensions for each image dynamically
      img_info <- image_info(img)
      img_width <- img_info$width
      img_height <- img_info$height
      
      plot(img_raster, xlab = "", ylab = "", bty = "n", asp = img_height / img_width) 
      
      
      # Display annotations at original size
      all_polygons <- coords() %>% filter(name == paste("polygon", i))
      for (poly_id in unique(all_polygons$polygon_id)) {
        polygon_coords <- all_polygons %>% filter(polygon_id == poly_id)
        if (nrow(polygon_coords) > 2) {
          polygon(polygon_coords$x, polygon_coords$y, border = "blue", col = rgb(0, 0, 1, alpha = 0.2))
        }
      }
    })
    
    # Clear all annotations
    observeEvent(input[[paste0("clear_", i)]], {
      coords(coords() %>% filter(name != paste("polygon", i)))
    })
    
    # Delete last polygon
    observeEvent(input[[paste0("delete_last_polygon", i)]], {
      current_coords <- coords()
      
      # Find the maximum polygon_id for the current image (i)
      max_polygon_id <- max(current_coords %>% filter(name == paste("polygon", i)) %>% pull(polygon_id), na.rm = TRUE)
      
      # Remove all points with the maximum polygon_id for the current image
      updated_coords <- current_coords %>% 
        filter(!(name == paste("polygon", i) & polygon_id == max_polygon_id))
      
      coords(updated_coords)
    })
    
    # Finalize polygon
    observeEvent(input[[paste0("end_polygon_", i)]], {
      polygon_id(polygon_id() + 1)
    })
  })
  
  # Page navigation handling
  observeEvent(input$next_page, {
    current_page <- page()
    if (current_page >= 2 && current_page <= 11) {
      i <- current_page - 1
      selected_class <- selected_city()[i]  # Get selected city for current image
      input_filename <- tools::file_path_sans_ext(basename(selected_images[i]))
      class_AI <- extract_class_from_filename(selected_images[i])
      
      # Save only if both a city is selected and there is an annotation
      polygon_coords <- coords() %>% filter(name == paste("polygon", i))
      annotation_missing <- nrow(polygon_coords) < 3  
      city_not_selected <- selected_class == ""
      
      if (annotation_missing && city_not_selected) {
        showModal(modalDialog(
          title = "Please choose a city and annotate the picture!",
          "Make sure to select a city and annotate the picture before proceeding.",
          easyClose = TRUE
        ))
      } else if (annotation_missing) {
        showModal(modalDialog(
          title = "Please annotate the picture!",
          "Make sure to annotate the picture before proceeding.",
          easyClose = TRUE
        ))
      } else if (city_not_selected) {
        showModal(modalDialog(
          title = "Please choose a city!",
          "Make sure to select a city before proceeding.",
          easyClose = TRUE
        ))
      } else {
        # Show progress bar for saving
        showModal(modalDialog(
          title = "Saving, please wait...",
          progressBar(id = "save_progress", value = 0, display_pct = TRUE),
          footer = NULL,
          easyClose = FALSE
        ))
        
        # Progressively update the progress bar during saving
        for (progress in seq(0, 100, by = 20)) {
          Sys.sleep(0.2)
          updateProgressBar(session, id = "save_progress", value = progress)
        }
        
        # Adjust y-coordinates for saving (no scaling)
        img <- image_read(selected_images[i])
        img_height <- image_info(img)$height
        save_coords <- polygon_coords %>% mutate(y = img_height - y)
        
        # Save adjusted coordinates to CSV and upload to Nextcloud
        csv_temp_path <- tempfile(fileext = ".csv")
        write.csv(save_coords, csv_temp_path, row.names = FALSE)
        save_to_nextcloud(csv_temp_path, csv_cloud_folder, paste0(input_filename, "_", selected_class, ".csv"), username, password)
        
        # Draw polygons on the image for saving
        img <- image_draw(img)
        for (poly_id in unique(save_coords$polygon_id)) {
          poly_coords <- save_coords %>% filter(polygon_id == poly_id)
          polygon(poly_coords$x, poly_coords$y, border = "blue", col = rgb(0, 0, 1, 0.2))
        }
        dev.off()
        
        # Save the annotated image temporarily and upload to Nextcloud
        img_temp_path <- tempfile(fileext = ".png")
        image_write(img, path = img_temp_path, format = "png")
        save_to_nextcloud(img_temp_path, img_cloud_folder, paste0(input_filename, "_", selected_class, ".png"), username, password)
        
        removeModal()
        
        page(current_page + 1)
      }
    } else {
      page(current_page + 1)
    }
  })
}
