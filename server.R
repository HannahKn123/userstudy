server <- function(input, output, session) {
  
  shinyjs::useShinyjs()
  
  # Nextcloud settings
  img_cloud_folder <- "annotation_result"
  csv_cloud_folder <- "annotation_result"
  username <- "zbc57"
  password <- "IBA2024Nein#"
  
  img_dir <- "xai_image/"
  all_images <- list.files(img_dir, pattern = "\\.png$", full.names = TRUE)
  selected_images <- sample(all_images, 10)
  
  extract_class_from_filename <- function(filename) {
    parts <- strsplit(basename(filename), "_")[[1]]
    class_name <- parts[length(parts)]
    class_name <- gsub("\\.png", "", class_name)
    return(class_name)
  }
  
  page <- reactiveVal(1)
  coords <- reactiveVal(value = tibble(x = numeric(), y = numeric(), polygon_id = integer(), name = character()))
  polygon_id <- reactiveVal(1)
  
  output$page_content <- renderUI({
    current_page <- page()
    if (current_page == 1) {
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
    } else if (current_page >= 2 && current_page <= 11) {
      i <- current_page - 1
      class_number <- extract_class_from_filename(selected_images[i])
      image <- image_read(selected_images[i])
      
      tagList(
        # AI Decision Box - Einheitliche Struktur und größerer Abstand zwischen den Seiten
        div(class = "highlight-container",
            style = "width: 100%; max-width: 1200px; margin: 0 auto; margin-bottom: 30px; display: flex; justify-content: center;",  # Box mittig im Fenster zentriert
            h4("AI Decision"),
            div(class = "flex-container", 
                style = "gap: 40px; width: 100%; align-items: center;",  # Größerer Abstand zwischen den Seiten
                div(style = "flex: 1;",  # Text links
                    p("The AI recognized this image as taken in ", 
                      span(style = "color: #4169E1;", class_number), ".")
                ),
                div(style = "flex: 1;",  # Text rechts
                    p("The ", strong("highlighted areas"), " shown below were ", strong("key factors"), " in its decision.")
                )
            )
        ),
        
        # Human Decision Box - Einheitliche Struktur und größerer Abstand zwischen den Seiten
        div(class = "decision-container",
            style = "width: 100%; max-width: 1200px; margin: 0 auto; display: flex; justify-content: center;",  # Box mittig im Fenster zentriert
            h4("Human Decision"),
            div(class = "flex-container", 
                style = "gap: 40px; width: 100%; align-items: center;",  # Größerer Abstand zwischen den Seiten
                div(
                  style = "flex: 1;",  # Textbereich links
                  p("Please ", strong("select the city"), " you believe this image represents from the dropdown menu:"),
                  div(class = "custom-dropdown",  
                      selectInput(paste0("class_", i), NULL, choices = c("", "Tel Aviv", "Jerusalem", "Hamburg", "Berlin"), 
                                  width = "150px",  
                                  selectize = FALSE)
                  )
                ),
                div(
                  style = "flex: 1; display: flex; flex-direction: column; align-items: center;",  # Text und Bildbereich rechts
                  p("Please ", strong("highlight the key areas"), " which were key factors in your decision."),  # Text über dem Bild
                  plotOutput(paste0("imagePlot", i), click = paste0("image_click_", i), height = "auto", width = "auto"),  # Ursprüngliche Größe des Bildes
                  div(style = "display: flex; gap: 10px; justify-content: center; margin-top: 10px;",  # Buttons unter dem Bild
                      actionButton(paste0("clear_", i), "Clear All Annotations", icon = icon("trash"), class = "btn-secondary"),
                      actionButton(paste0("delete_last_polygon", i), "Delete Last Polygon", icon = icon("trash"), class = "btn-secondary"),
                      actionButton(paste0("end_polygon_", i), "Complete Polygon", icon = icon("check"), class = "btn-secondary"),
                      actionButton("next_page", "Next Image", icon = icon("arrow-right"), class = "btn-primary")
                  )
                )
            )
        )
      )
    }else {
      tagList(
        h3("Thank you for completing the annotations!"),
        p("All annotated images and coordinates have been saved to Nextcloud."),
        actionButton("close_app", "Close", class = "btn-primary", style = "margin-top: 20px;")
      )
    }
  })
  
  # Observers for annotation functionality
  observeEvent(page(), {
    lapply(1:10, function(i) {
      observeEvent(input[[paste0("image_click_", i)]], {
        current_coords <- coords()
        polygon_id_val <- polygon_id()
        current_coords <- add_row(
          current_coords,
          x = input[[paste0("image_click_", i)]]$x,
          y = input[[paste0("image_click_", i)]]$y,
          polygon_id = polygon_id_val,
          name = paste("polygon", i)
        )
        coords(current_coords)
      })
      
      output[[paste0("imagePlot", i)]] <- renderPlot({
        img <- image_read(selected_images[i])
        img_raster <- as.raster(img)
        plot(img_raster)
        
        all_polygons <- coords() %>% filter(name == paste("polygon", i))
        unique_polygons <- unique(all_polygons$polygon_id)
        
        for (poly_id in unique_polygons) {
          polygon_coords <- all_polygons %>% filter(polygon_id == poly_id)
          if (nrow(polygon_coords) > 2) {
            polygon(polygon_coords$x, polygon_coords$y, border = "blue", col = rgb(0, 0, 1, alpha = 0.2))
          }
        }
      })
      
      observeEvent(input[[paste0("clear_", i)]], {
        coords(coords() %>% filter(name != paste("polygon", i)))
      })
      
      observeEvent(input[[paste0("end_polygon_", i)]], {
        polygon_id(polygon_id() + 1)
      })
    })
  })
  
  observeEvent(input$next_page, {
    current_page <- page()
    if (current_page >= 2 && current_page <= 11) {
      i <- current_page - 1
      selected_class <- input[[paste0("class_", i)]]
      input_filename <- tools::file_path_sans_ext(basename(selected_images[i]))
      class_AI <- extract_class_from_filename(selected_images[i])
      
      polygon_missing <- selected_class == ""
      polygon_coords <- coords() %>% filter(name == paste("polygon", i))
      annotation_missing <- nrow(polygon_coords) < 3  
      
      if (annotation_missing && polygon_missing) {
        showModal(modalDialog(
          title = "Please choose a city and annotate the picture!",
          "Please make sure to select a city from the dropdown menu and annotate the picture before moving to the next page.",
          easyClose = TRUE
        ))
      } else if (annotation_missing) {
        showModal(modalDialog(
          title = "Please annotate the picture!",
          "Please make sure to annotate the picture before moving to the next page.",
          easyClose = TRUE
        ))
      } else if (polygon_missing) {
        showModal(modalDialog(
          title = "Please choose a city!",
          "Please make sure to select a city from the dropdown menu before moving to the next page.",
          easyClose = TRUE
        ))
      } else {
        # Save functionality with progress bar
        showModal(modalDialog(
          title = "Saving, please wait...",
          progressBar(id = "save_progress", value = 0, display_pct = TRUE),
          footer = NULL,
          easyClose = FALSE
        ))
        
        for (progress in seq(0, 100, by = 20)) {
          Sys.sleep(0.2)
          updateProgressBar(session, id = "save_progress", value = progress)
        }
        
        # Save annotation details here (image and CSV saving)
        
        removeModal()
        page(current_page + 1)
      }
    } else {
      page(current_page + 1)
    }
  })
}