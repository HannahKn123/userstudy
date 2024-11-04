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
  
  user_id <- reactiveVal("")
  
  
  # Load images from directory
  img_dir <- "xai_image_2/"
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
        div(style = "text-align: center; margin: 0 auto; max-width: 800px; padding: 20px; background-color: #f4f6f9; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);",
            h2("Welcome to this Annotation Study!", style = "color: #003366; font-weight: bold; text-align: center;"),
            
            # Paragraph with increased margin-bottom to add space
            p("In this study, we aim to explore how artificial intelligence (AI) and humans can collaborate effectively.",
              style = "text-align: center; margin-top: 50px; margin-bottom: 50px;"),
            
            # User ID input
            div(style = "display: flex; flex-direction: column; align-items: center; max-width: 400px; margin: 0 auto; padding: 15px; border-radius: 5px; border: 1px solid #ddd;",
                textInput("user_id_input", label = div(style = "font-weight: bold; color: #003366; text-align: center;", "Please enter your User ID:"),
                          placeholder = "User ID", width = '100%'),
                div(style = "font-size: 12px; color: #666; text-align: center;",
                    "The User ID is required to track your work.")
            ),
            
            # Continue button
            div(style = "display: flex; justify-content: center; margin-top: 30px;",
                actionButton("next_page", "Instructions", icon = icon("arrow-right"), class = "btn-primary btn-lg",
                             style = "background-color: #007bff; color: white; border: none; border-radius: 5px;")
            )
        )
      )
    } else if (current_page == 2) {  # Second introduction page
      tagList(
        div(style = "text-align: center; margin: 0 auto; max-width: 800px; padding: 20px; background-color: #f4f6f9; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);",
            h2("Instructions", style = "color: #003366; font-weight: bold; text-align: center;"),
            
            # New instructions text with structured layout
            
            h4("Your Task:", style = "text-align: center; color: #003366;"),
            
            p(HTML("You will be shown <span style='color: #003366; font-weight: bold;'>10 images</span> of random locations from one of four cities: <span style='color: #003366; font-weight: bold;'>Berlin, Hamburg, Jerusalem, and Tel Aviv</span>. Each image is a Google Maps photo from one of these cities."),
              style = "text-align: center; margin-bottom: 20px;"),
            
            tags$ol(
              tags$li(
                strong("City Classification:"), 
                " Look at each image carefully and decide which of the four cities you think it shows. Our AI model has already made its own prediction, which we will share with you."
              ),
              tags$li(
                strong("Marking Important Areas:"), 
                "You'll also be shown key areas of the image that had the greatest impact on the AI's decision. Your task is to highlight the areas that you find most important for your own judgment. If you agree with the AI, you can select similar areas, or you can choose entirely different areas based on your perspective."              )
            ),
            
            strong("Keep in mind that AI models can make mistakes, so the AI's choice may not always be correct."),
            
            h4("Bonus Opportunity:", style = "text-align: center; color: #003366; margin-top: 30px;"),
            
            p("You can earn an additional payment by providing precise markings and achieving at least 90% correct classifications. This bonus will be an extra x cents.",
              style = "text-align: center; margin-top: 10px;"),
            
            p("Thank you for your participation!", style = "text-align: center; margin-top: 20px; font-weight: bold; color: #003366;"),
            
            # Continue button
            div(style = "text-align: center; margin-top: 30px;",
                actionButton("next_page", "Annotation Instructions", icon = icon("arrow-right"), class = "btn-primary btn-lg",
                             style = "background-color: #007bff; color: white; border: none; border-radius: 5px;")
            )
        )
      )
    } else if (current_page == 3) {  # Third introduction page for polygon instructions
      tagList(
        div(style = "text-align: center; margin: 0 auto; max-width: 800px; padding: 20px; background-color: #f4f6f9; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);",
            
            # Page Title
            h2("Instructions for Marking Important Areas", style = "color: #003366; font-weight: bold; text-align: center;"),
            
            # Explanation for creating polygons
            p("To mark important areas in the images, click on the image to create points around the region. These points will form a polygon that outlines the area you consider important.",
              style = "text-align: center; margin-bottom: 20px;"),
            
            p("Please ensure to carefully place points around the boundary, capturing as many corners as necessary to create an as accurately as possible outline.",
              style = "text-align: center; margin-bottom: 20px; font-weight: bold;"),
            
            p("Here you can see a very good example on the left while the right is a very bad exaple"),
              
            # Display specific images (1.jpg, 2.jpg) from the www/examples folder
            div(style = "display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; margin-top: 50px;",
                # Load and display each specific image
                lapply(c("11.png", "12.png"), function(img_name) {
                  img_path <- file.path("examples", img_name)  # Use only the relative path from www
                  tags$img(src = img_path, style = "max-width: 300px; height: auto; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);")
                })
            ),
            
            # Continue button
            div(style = "text-align: center; margin-top: 30px;",
                actionButton("next_page", "Start", icon = icon("arrow-right"), class = "btn-primary btn-lg",
                             style = "background-color: #007bff; color: white; border: none; border-radius: 5px;")
            )
        )
      )
    }
    else if (current_page >= 4 && current_page <= 13) {  # Annotation pages
      i <- current_page - 3  # Image index
      class_number <- extract_class_from_filename(selected_images[i])
      image <- image_read(selected_images[i])
      
      # Get image dimensions for original size display
      img_info <- image_info(image)
      img_width <- img_info$width
      img_height <- img_info$height
      
      # UI layout with AI and human decision boxes
      tagList(
        div(style = "display: flex; flex-direction: column; gap: 10px; width: 100%; margin: 0 auto;",  # Set gap to 0px to remove extra space
            div(class = "highlight-container",
                style = "background-color: #e0e0e0; border-radius: 8px; display: flex; padding: 10px; width: 100%; max-width: 1500px; margin-bottom: 2px;",  # Reduced margin-bottom
                h4("AI Decision"),
                div(class = "flex-container", 
                    style = "display: flex; gap: 20px; width: 100%; align-items: stretch;",
                    div(style = "background-color: #ffffff; border-radius: 8px; display: flex; flex: 1; flex-basis: 28%; padding: 15px; min-height: 10px;",  
                        div(style = "display: flex; text-align: left; width: 100%;",  
                            p("The AI recognized this image as taken in ", 
                              span(style = "color: #800080; font-weight: bold;", class_number), ".")
                        )
                    ),
                    div(style = "background-color: #ffffff; border-radius: 8px; display: flex; flex: 1; flex-basis: 72%; padding: 15px; min-height: 10px;",  
                        div(style = "display: flex; text-align: left; width: 100%;",  
                            p("The ", span(style = "color: #800080; font-weight: bold;", "highlighted areas"), 
                              " shown below were key factors in its decision.")
                        )
                    )
                )
            ),
            div(class = "decision-container",
                style = "background-color: #e0e0e0; border-radius: 8px; display: flex; padding: 10px; width: 100%; max-width: 1500px; margin-top: 2px;",  # Reduced margin-top
                h4("Human Decision"),
                div(class = "flex-container", 
                    style = "display: flex; gap: 20px; width: 100%; align-items: stretch;",  
                    div(style = "background-color: #ffffff; border-radius: 8px; display: flex; flex: 1; flex-basis: 28%; padding: 15px; flex-direction: column;",  
                        div(style = "display: flex; flex-direction: column; width: 100%; height: 100%; gap: 30px;",  
                            p("Take a close look at the image. Do you agree with the AI’s classification of this image as Berlin, or would you assign it to a different city? Please ", strong(style = "color: #4169E1;", "select your choice"), " below."),
                            div(class = "btn-group-container", style = "display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; margin-top: 20px;",
                                actionButton(inputId = paste0("class_", i, "_tel_aviv"), label = "Tel Aviv", class = "btn", style = "width: 150px; text-align: center;"),
                                actionButton(inputId = paste0("class_", i, "_jerusalem"), label = "Jerusalem", class = "btn", style = "width: 150px; text-align: center;"),
                                actionButton(inputId = paste0("class_", i, "_hamburg"), label = "Hamburg", class = "btn", style = "width: 150px; text-align: center;"),
                                actionButton(inputId = paste0("class_", i, "_berlin"), label = "Berlin", class = "btn", style = "width: 150px; text-align: center;")
                            )
                        )
                    ),
                    div(style = "background-color: #ffffff; border-radius: 8px; display: flex; flex: 1; flex-basis: 72%; padding: 15px; flex-direction: column; align-items: center;",  
                        div(style = "width: 100%; text-align: left; margin-bottom: 10px;",
                            p("Review these highlighted areas carefully. Which parts of the image led you to your decision? Please ", span(style = "color: #4169E1; font-weight: bold;", "mark these key areas as precisely as possible"), " using the annotation tool. Before proceeding, ensure that you’ve marked all features you consider important.")
                        ),
                        # Outer div to center the image
                        div(style = paste("display: flex; justify-content: center; align-items: center; width:", img_width, "px; height:", img_height, "px; padding: 0; margin: 0;"),
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
                            actionButton("next_page", "Next", icon = icon("arrow-right"), 
                                         class = "btn-primary", style = "padding: 5px 7px; font-size: 12px;")  
                        )
                    )
                )
            )
        )
      )
    } else if (current_page == 14) {
      tagList(
        div(style = "text-align: center; margin-bottom: 20px;",
            h3("You are nearly done! Just answer the last two questions:")
        ),
        
        div(style = "background-color: #f9f9f9; padding: 20px; border-radius: 8px; max-width: 600px; margin: 0 auto; box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);",
            
            # Question 1
            div(style = "margin-bottom: 20px;",
                h4("Question 1"),
                p("Have you ever visited Berlin, Hamburg, Tel Aviv, or Jerusalem?"),
                radioButtons("q1", label = NULL, choices = c("Yes", "No"), inline = TRUE)
            ),
            
            # Question 2
            div(style = "margin-bottom: 20px;",
                h4("Question 2"),
                p("How would you rate this study if 1 is the worst and 5 is the best?"),
                radioButtons("q2", label = NULL, choices = c("1", "2", "3", "4", "5"), inline = TRUE)
            ),
            
            # Next button
            div(style = "text-align: center; margin-top: 20px;",
                actionButton("next_page", "Last Page", icon = icon("arrow-right"), class = "btn-primary btn-lg")
            )
        )
      )
    } else {  # Completion page after annotations
      tagList(
        div(style = "text-align: center; padding: 40px; max-width: 600px; margin: 0 auto;",
            
            h3("🎉 Thank you for completing the study! 🎉", 
               style = "font-weight: bold; color: #4CAF50; margin-bottom: 20px;"),
            
            p("We appreciate your time and effort in participating. All annotated images have been saved successfully.", 
              style = "font-size: 16px; color: #555; margin-bottom: 15px;"),
            
            p("Your responses will be reviewed shortly, and we’ll confirm your participation via email. Thank you for contributing to this research!", 
              style = "font-size: 16px; color: #555;"),
            
            div(style = "text-align: center; margin-top: 30px;",
                actionButton("close_app", "Close", 
                             icon = icon("check-circle"), 
                             class = "btn-primary btn-lg", 
                             style = "padding: 10px 20px; font-size: 18px;"))
        )
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
    
    
    # Funktion, um den gewählten Button blau zu markieren
    lapply(1:10, function(i) {
      observeEvent(input[[paste0("class_", i, "_tel_aviv")]], {
        shinyjs::removeClass(selector = paste0("#class_", i, "_jerusalem"), class = "selected")
        shinyjs::removeClass(selector = paste0("#class_", i, "_hamburg"), class = "selected")
        shinyjs::removeClass(selector = paste0("#class_", i, "_berlin"), class = "selected")
        shinyjs::addClass(selector = paste0("#class_", i, "_tel_aviv"), class = "selected")
      })
      
      observeEvent(input[[paste0("class_", i, "_jerusalem")]], {
        shinyjs::removeClass(selector = paste0("#class_", i, "_tel_aviv"), class = "selected")
        shinyjs::removeClass(selector = paste0("#class_", i, "_hamburg"), class = "selected")
        shinyjs::removeClass(selector = paste0("#class_", i, "_berlin"), class = "selected")
        shinyjs::addClass(selector = paste0("#class_", i, "_jerusalem"), class = "selected")
      })
      
      observeEvent(input[[paste0("class_", i, "_hamburg")]], {
        shinyjs::removeClass(selector = paste0("#class_", i, "_tel_aviv"), class = "selected")
        shinyjs::removeClass(selector = paste0("#class_", i, "_jerusalem"), class = "selected")
        shinyjs::removeClass(selector = paste0("#class_", i, "_berlin"), class = "selected")
        shinyjs::addClass(selector = paste0("#class_", i, "_hamburg"), class = "selected")
      })
      
      observeEvent(input[[paste0("class_", i, "_berlin")]], {
        shinyjs::removeClass(selector = paste0("#class_", i, "_tel_aviv"), class = "selected")
        shinyjs::removeClass(selector = paste0("#class_", i, "_jerusalem"), class = "selected")
        shinyjs::removeClass(selector = paste0("#class_", i, "_hamburg"), class = "selected")
        shinyjs::addClass(selector = paste0("#class_", i, "_berlin"), class = "selected")
      })
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
    
    
    observeEvent(input$user_id_input, {
      user_id(input$user_id_input)
    })
    
    
    
    # Render the original-size plot with annotations
    output[[paste0("imagePlot", i)]] <- renderPlot({
      img <- image_read(selected_images[i])
      img_raster <- as.raster(img)
      
      # Get image dimensions for each image dynamically
      img_info <- image_info(img)
      img_width <- img_info$width
      img_height <- img_info$height
      
      # Setze den Plot-Hintergrund auf transparent
      par(bg = NA, mar = c(0, 0, 0, 0))  # Hintergrund transparent und ohne Margen
      
      # Zeichne das Bild ohne Rand und Achsenbeschriftungen
      plot(img_raster, xlab = "", ylab = "", bty = "n", asp = img_height / img_width)
      
      # Zeige die Annotationen im Originalmaßstab an
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
    
    if (current_page >= 4 && current_page <= 13) {
      i <- current_page - 3
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
        save_to_nextcloud(csv_temp_path, csv_cloud_folder, paste0(user_id(), "_", input_filename, "_", selected_class, ".csv"), username, password)
        
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
        save_to_nextcloud(img_temp_path, img_cloud_folder, paste0(user_id(), "_", input_filename, "_", selected_class, ".png"), username, password)
        
        removeModal()
        
        page(current_page + 1)  # Move to the next page after processing
      }
    } else if  (page() == 1) {  # Check if on the first page
        if (input$user_id_input == "") {
          # Show a warning if User ID is empty
          showModal(modalDialog(
            title = "User ID Required",
            "Please enter your User ID to proceed.",
            easyClose = TRUE
          ))
        } else {
          # Store the User ID and go to the next page
          user_id(input$user_id_input)
          page(2)  # Move to the second page
        }
    }else {
      page(current_page + 1)  # Move to the next page for non-image pages
    }
    
  })
  

  
  # Add tab switching based on page
  observeEvent(input$next_page, {
    current_page <- page()
    new_page <- current_page + 0
    page(new_page)
    
    # Update the tab based on the new page
    updateTabsetPanel(session, "main_tab", selected = paste0("tab_", new_page))
  })
  
  
}
