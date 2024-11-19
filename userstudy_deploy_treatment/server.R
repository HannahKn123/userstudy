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

options(shiny.trace = FALSE)

# Lade helper.R für die save_to_nextcloud Funktion
source("helper.R")

# Load the image globally so it's accessible throughout the app
loaded_image <- image_read("www/berlin_attention_check_Berlin_Hamburg.png")
loaded_image_ueb <- image_read("www/ueben_img.png")

# Get image dimensions for display at original size
img_info <- image_info(loaded_image)
img_width <- img_info$width
img_height <- img_info$height

# Get image dimensions for display at original size
img_info_ueb <- image_info(loaded_image_ueb)
img_width_ueb  <- img_info_ueb$width
img_height_ueb  <- img_info_ueb$height






server <- function(input, output, session) {
  closeAllConnections()
  shinyjs::useShinyjs()
  
  # Nextcloud settings
  img_cloud_folder <- "treatment/treatment_image"
  csv_cloud_folder <- "treatment/treatment_csv"
  img_attention_cloud_folder <- "treatment/treatment_attention_image"
  csv_attention_cloud_folder <- "treatment/treatment_attention_csv"
  img_uebung_cloud_folder <- "treatment/treatment_uebung_image"
  csv_uebung_cloud_folder <- "treatment/treatment_uebung_csv"
  fail_folder <- "treatment/treatment_failures"
  question_folder <- "treatment/treatment_questions"
  
  
  username <- "zbc57"
  password <- "IBA2024Nein#"
  
  user_id <- reactiveVal("")
  q1_response <- reactiveVal(NULL)
  q2_response <- reactiveVal(NULL)
  
  selected_confidence <- reactiveVal(rep("", 6))  # Initialize for 10 images
  selected_city_6 <- reactiveVal(NULL)
  confidence_level_6 <- reactiveVal(NULL)
  
  # Load images from directory
  # img_dir <- "1_study_input"
  # all_images <- list.files(img_dir, pattern = "\\.png$", full.names = TRUE)
  
  
  img_dir_true <- "1_xai_study_input_true"
  img_dir_false <- "1_xai_study_input_false"
  
  all_images_true <- list.files(img_dir_true, pattern = "\\.png$", full.names = TRUE)
  all_images_false <- list.files(img_dir_false, pattern = "\\.png$", full.names = TRUE)
  
  
  #set.seed(as.numeric(user_id))  # Use user ID as seed for reproducibility
  # Randomly select 4 images from the first folder
  selected_images_from_folder_true <- sample(all_images_true, 4)
  # Randomly select 1 image from the second folder
  selected_image_from_folder_false <- sample(all_images_false, 1)
  
  # Combine the selected images into one vector
  selected_images <- c(selected_images_from_folder_true, selected_image_from_folder_false)
  # Shuffle the combined vector to remove any ordering
  selected_images <- sample(selected_images)
  
  print(selected_images)
  
  
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
  selected_city <- reactiveVal(rep("", 6))  # Initialize for 10 images
  
  
  
  # Track which div step is currently active
  step <- reactiveVal(1)
  
  
  # UI rendering for each page
  output$page_content <- renderUI({
    current_page <- page()
    if (current_page == 1) {  # Initial instructions page
      tagList(
        div(style = "text-align: center; margin: 0 auto; max-width: 800px; padding: 20px; background-color: #f4f6f9; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);",
            h2("Welcome! We're Glad to Have You Here!", style = "color: #003366; font-weight: bold; text-align: center;"),
            
            # Paragraph with increased margin-bottom to add space
            p("We aim to explore effective collaboration between ", strong("ARTIFICIAL INTELLIGENCE"), "and " , strong("HUMANS"),
              style = "text-align: center; margin-bottom: 40px; margin-top: 20px;"),
            
            # User ID input
            div(style = "display: flex; flex-direction: column; align-items: center; max-width: 400px; margin: 0 auto; padding: 15px; border-radius: 5px; border: 1px solid #ddd;",
                textInput("user_id_input", label = div(style = "font-size: 16px; font-weight: bold; color: #003366; text-align: center;", "Please enter your user ID:"),
                          placeholder = "User ID", width = '100%'),
                div(style = "font-size: 12px; color: #666; text-align: center;",
                    "The user ID is required to track your work.")
            ),
            
            # Continue button
            div(style = "display: flex; justify-content: center; margin-top: 20px;",
                actionButton("next_page", "Continue to Introduction", icon = icon("arrow-right"), class = "btn-primary btn-lg",
                             style = "background-color: #007bff; color: white; border: none; border-radius: 5px;")
            )
        )
      )
    } else if (current_page == 2) {  # Initial instructions page
      tagList(
        div(style = "text-align: center; margin: 0 auto; max-width: 800px; padding: 20px; background-color: #f4f6f9; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);",
            h2("Prolific Introduction", style = "color: #003366; font-weight: bold; text-align: center;"),
            
            # Paragraph with increased margin-bottom to add space
            p("Thank you for your interest in participating in our study on 'Human-AI Collaboration'. This research is conducted by the Institute for Business Analytics at the University of Ulm. The data collected will be used as part of our research project and will contribute to scientific presentations and publications. Before beginning the study, please carefully read the following consent form and general information.",
              style = "text-align: center; margin-top: 20px; margin-bottom: 40px;"),
            
            strong("What is the Study About?"), 
            p("The study explores how successful collaboration between humans and artificial intelligence (AI) can be achieved. During the study, you will be shown five different images from four distinct cities. Your task is to assign each image to the correct city. Additionally, you will use a marking tool to highlight any features on the image that were decisive in making your decision. Your markings will be used after the study to train the AI and improve its performance.  To assist you, you will also receive information on how the AI has classified the image.",
              style = "text-align: center; margin-bottom: 40px;"),
            
            strong("What Are the Study Conditions?", style = "text-align: center; margin-top: 20px;"), 
            p("The study will take approximately 8 minutes to complete. Please answer all questions as accurately and precisely as possible. You are free to withdraw from the study at any time by closing your browser window."),
            p("Please note that attention checks will be conducted throughout the study. Failure to pass these checks will result in early exclusion from the study, and in such cases, no compensation will be provided.",
              style = "text-align: center; margin-bottom: 40px;"),
            
            strong("How Is Data Collected?", style = "text-align: center; margin-bottom: 40px;"),
            p("Data collection and analysis are conducted exclusively in an anonymized and strictly confidential manner, ensuring that your data cannot be linked to your identity. The anonymized data will be used solely by the Institute for Business Analytics at the University of Ulm. You may withdraw your consent for data collection and analysis at any time after the study, without providing a reason.", 
              style = "text-align: center; margin-bottom: 40px;"),
            
            strong("Do You Have Any Questions?", style = "text-align: center; margin-bottom: 40px;"), 
            p("If you have any questions or comments, please feel free to contact us at hannah.knehr@uni-ulm.de."),
            p("Please note that your consent to the use of your data is required to participate in the study.",
              style = "text-align: center; margin-bottom: 40px;"),
            
            div(style = "width: 100%; display: flex; align-items: center;",
                checkboxInput("consent_checkbox", 
                              label = strong("I have read and understood the information above and consent to participate in the study."),
                              value = FALSE, 
                              width = '100%')
            ),
            
            
            
            # Continue button
            div(style = "display: flex; justify-content: center; margin-top: 20px;",
                actionButton("next_page", "Continue to Introduction", icon = icon("arrow-right"), class = "btn-primary btn-lg",
                             style = "background-color: #007bff; color: white; border: none; border-radius: 5px;")
            )
        )
      )
    } else if (current_page == 3) {  # Second introduction page
      tagList(
        div(id = "intro1", style = "text-align: center; margin: 0 auto; max-width: 800px; padding: 20px; background-color: #f4f6f9; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);",
            h2("Introduction to the Study", style = "color: #003366; font-weight: bold; text-align: center;"),
            
            p("You will be shown  ", strong("Google Maps images") , " - each depicting a random location from one of four cities: ", 
              style = "text-align: center; margin-top: 20px;"),
            p(HTML("<span style='color: #003366; font-weight: bold;'>Berlin, Hamburg, Jerusalem, or Tel Aviv</span>."),
              style = "text-align: center;"),
            
            p("For each image, the Artificial intelligence model has predicted ", strong("the location"), " and highlighted ", strong("important areas"), " that influenced its decision. We are providing you with this information.", 
              style = "text-align: center;"),
            
            
            div(
              strong("Keep in mind that Artificial Intelligence can make mistakes, so the Artificial Intelligence's choice may not always be correct."),
              style = "color: red;"
            ),
            
            actionButton("next_page_step_1", "Continue", icon = icon("arrow-down"), class = "btn-primary", style = "margin-top: 20px;")
            
        ), 
        
        div(id = "intro2", style = "text-align: center; margin: 0 auto; max-width: 800px; padding: 20px; background-color: #f4f6f9; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);",
            
            p(HTML("You will have <span style='font-weight: bold;'>three tasks</span> for each image:"), 
              style = "text-align: left;"),
            
            tags$ol(style = "list-style-type: decimal; padding-left: 2;",  # Adds numbers and removes indentation
                    div(style = "text-align: left;",
                        tags$li(p(strong("Choose a City: "), "Review the image and select the city where you believe it was captured."))
                    ),
                    div(style = "text-align: left;",
                        tags$li(p(strong("Annotate the Image: "), "Use the provided annotation tool to highlight areas in the image that influenced your choice."))
                    ),
                    div(style = "text-align: left;",
                        tags$li(p(strong("Choose a Confidence Level: "), "Select how confident you are in your choice, from 'Very Unsure' to 'Very Sure'."))
                    )
            ),
            
            actionButton("next_page_step_2", "Continue",  icon = icon("arrow-down"), class = "btn-primary", style = "margin-top: 20px;")
            
        ),
        
        div(id = "intro3", style = "text-align: center; margin: 0 auto; max-width: 800px; padding: 20px; background-color: #f4f6f9; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);",
            
            h4("Bonus Opportunity and Attention Checks", style = "text-align: center; color: #003366;"),
            
            p("Your feedback is essential to the success of our research project, and the accuracy of your responses plays a crucial role. You have the opportunity to increase your earnings through particularly precise answers: If you correctly identify all cities and accurately mark the relevant areas on the images, you will receive an additional bonus payment of 1 USD.",
              style = "text-align: center; margin-top: 10px;"),
            
            p("There will be attention checks for each of the three steps. Failure to pass these checks will result in no payment.",
              style = "font-weight: bold; color: red; text-align: center; margin-top: 10px;"),
            
            # Continue button
            div(style = "text-align: center; margin-top: 20px;",
                actionButton("next_page", "Continue to Annotation Instructions", icon = icon("arrow-right"), class = "btn-primary btn-lg",
                             style = "background-color: #007bff; color: white; border: none; border-radius: 5px;")
            )
        )
      )
    } else if (current_page == 4) {  # Third introduction page for polygon instructions
      tagList(
        div(id = "intro1_2", style = "text-align: center; margin: 0 auto; margin-top: 30px; max-width: 800px; padding: 20px; background-color: #f4f6f9; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);",
            
            # Page Title
            h2("Annotation Instructions", style = "margin-top: 20px; color: #003366; font-weight: bold; text-align: center;"),
            
            p("The following explains how to use the annotation tool."),
            
            div(style = "display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; margin-bottom: 10px;",
                # Load and display each specific image
                lapply(c("4_2.png"), function(img_name) {
                  img_path <- file.path("examples", img_name)  # Use only the relative path from www
                  tags$img(src = img_path, style = "max-width: 500px; height: auto; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);")
                })
            ),
            
            
            # Explanation for creating polygons
            tags$ol(
              div(style = "text-align: left; color: orange;",
                  strong("Forming a Shape:"),
                  tags$ul(style = "list-style-type: disc; color: black;",  # Set bullet points to black
                          tags$li("Click on the image to add the first point."),
                          tags$li("Continue adding points at each corner."),
                          tags$li("These points will connect to form a yellow-shaded shape around the selected area.")
                  )
              ),
              
              div(style = "text-align: left; color: green; margin-top: 10px",  # Adds space between sections
                  strong("Delete Annotations:"),
                  tags$ul(style = "list-style-type: disc; color: black;",  # Set bullet points to black
                          tags$li("Delete the last corner if necessary."),
                          tags$li("Delete the last shape if necessary."),
                          tags$li("Clear all shapes if necessary.")
                  )
              ),
              
              div(style = "text-align: left; color: #E83E8C; margin-top: 10px",  # Adds space between sections
                  strong("Completing the Annotation:"),
                  tags$ul(style = "list-style-type: disc; color: black;",  # Set bullet points to black
                          tags$li("You can add multiple shapes."),
                          tags$li("However, you need to complete the first shape before adding another")
                  )
              ), 
              
              actionButton("next_page_step_3", "Continue",  icon = icon("arrow-down"), class = "btn-primary", style = "margin-top: 20px;")
              
            )
        ), 
        
        div(id = "intro2_2", style = "text-align: center; margin: 0 auto; max-width: 800px; padding: 20px; background-color: #f4f6f9; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);",
            
            p("Please ensure to carefully place points around the boundary, capturing as many corners as necessary to create an as accurately as possible outline.",
              style = "text-align: center; font-weight: bold;"),
            
            
            p(
              strong(style = "text-align: center; font-weight: bold; color: green; margin-right: 250px;", "good example"), 
              strong(style = "text-align: center; font-weight: bold; color: red", "bad example")
            ),
            
            div(style = "display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; margin-top: 15px; margin-bottom: 15px;",
                # Load and display each specific image
                lapply(c("2_2.png", "5_2.png"), function(img_name) {
                  img_path <- file.path("examples", img_name)  # Use only the relative path from www
                  tags$img(src = img_path, style = "max-width: 370px; height: auto; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);")
                })
            ),
            
            
            strong(style = "margin-top: 40px; color: #FF0000;", "Follow the instructions carefully, as there will be attention checks."),
            
            # Continue button
            div(style = "text-align: center; margin-top: 20px;",
                actionButton("next_page", "Continue to Annotation Practice", icon = icon("arrow-right"), class = "btn-primary btn-lg",
                             style = "background-color: #007bff; color: white; border: none; border-radius: 5px;")
            )
        )
      )
    } else if (current_page == 5){
      tagList(
        div(style = "text-align: center; margin: 0 auto; margin-top: 30px; max-width: 800px; padding: 20px; background-color: #f4f6f9; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);",
            
            # Page Title
            h2("Annotation Practice", style = "margin-top: 20px; color: #003366; font-weight: bold; text-align: center;"),
            
            tags$ol(
              div(style = "text-align: center;",
                  p("In the next step, please practice using the annotation tool as demonstrated below."),
              ), 
              
              div(style = "text-align: center; margin-top: 20px; margin-bottom: 20px;",
                  tags$img(src = "examples/beispiel_2.gif", width = "400px", height = "auto", 
                           style = "border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);")
              ),
              
              div(style = "text-align: left; margin-bottom: 20px",
                  tags$ul(style = "list-style-type: decimal; color: black;",  # Set bullet points to black
                          tags$li(strong("Draw"), " a shape around the ", strong(style = "color: #32CD32", "green"), " shape."),
                          tags$li(strong("Draw"), " a shape around the ", strong(style = "color: #1E90FF ;", "blue"), " shape."),
                          tags$li(strong("Delete"), " the shape around the ", strong(style = "color: #1E90FF ;", "blue"), " shape."),
                  )
              ),
              
              div(style = "margin-top: 20px; color: #FF0000;", 
                  p("The result will be saved and used as an attention check.")
              ),
              
              
              # Display the image for annotation
              div(style = paste("margin-top: 40px; display: flex; justify-content: center; align-items: center; width:", img_width_ueb, "px; height:", img_height_ueb, "px; padding: 0; margin: 0;"),
                  plotOutput("imagePlot_uebung", click = "image_click_uebung", 
                             width = paste0(img_width_ueb, "px"), height = paste0(img_height_ueb, "px"))
              ),
              
              div(style = "display: flex; gap: 10px; margin-top: 15px; justify-content: center;",  
                  actionButton("clear_uebung", "Clear All Shapes", icon = icon("trash"), 
                               class = "btn-secondary", style = "padding: 5px 7px; font-size: 12px;"),  
                  actionButton("delete_last_polygon_uebung", "Delete Last Shape", icon = icon("trash"), 
                               class = "btn-secondary", style = "padding: 5px 7px; font-size: 12px;"),  
                  # Add in the UI section where other action buttons are defined
                  actionButton("delete_last_corner", "Delete Last Corner", icon = icon("trash"), 
                               class = "btn-secondary", style = "padding: 5px 7px; font-size: 12px;"),
                  actionButton("end_polygon_uebung", "Complete Shape", icon = icon("check"), 
                               class = "btn-secondary", style = "padding: 5px 7px; font-size: 12px;"),  
                  actionButton("next_page", "Start Study", icon = icon("arrow-right"), 
                               class = "btn-primary", style = "padding: 5px 7px; font-size: 12px;")  
              ),
            ),
            
        ), 
      )
      
    } else if (current_page == 10) {  # Page 6 content with updated text for annotation
      # Reset polygon ID
      coords(tibble(x = numeric(), y = numeric(), polygon_id = integer(), name = character()))
      polygon_id(1)  # Reset polygon ID
      
      # Load Image
      image_path <- "www/berlin_attention_check_Berlin_Hamburg.png"
      loaded_image <- image_read(image_path)
      
      # Get image dimensions for original size display
      img_info <- image_info(loaded_image)
      img_width <- img_info$width
      img_height <- img_info$height
      
      tagList(
        div(style = "display: flex; flex-direction: column; gap: 10px; width: 100%; margin: 0 auto;",  
            div(class = "highlight-container",
                style = "background-color: #e0e0e0; border-radius: 8px; display: flex; padding: 10px; width: 100%; max-width: 1500px; margin-bottom: 2px;",  
                h4("AI Decision"),
                div(class = "flex-container", 
                    style = "display: flex; gap: 20px; width: 100%; align-items: stretch;",
                    div(style = "background-color: #ffffff; border-radius: 8px; display: flex; flex: 1; flex-basis: 28%; padding: 15px; min-height: 10px;",  
                        div(style = "display: flex; text-align: left; width: 100%;",  
                            p("The AI recognized this image as taken in ", 
                              span(style = "color: #800080; font-weight: bold;", "Berlin"), ".")
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
                style = "background-color: #e0e0e0; border-radius: 8px; display: flex; padding: 10px; width: 100%; max-width: 1500px; margin-top: 2px;",  
                h4("Human Decision"),
                div(class = "flex-container", 
                    style = "display: flex; gap: 20px; width: 100%; align-items: stretch;",  
                    div(style = "background-color: #ffffff; border-radius: 8px; display: flex; flex: 1; flex-basis: 28%; padding: 15px; flex-direction: column;",  
                        div(style = "display: flex; flex-direction: column; width: 100%; height: 100%; gap: 30px;",  
                            p("Take a close look at the image. This is an Attention Check. Please ", strong(style = "color: #FFA500;", "select Berlin"), " below. If you select another city you will fail the attention check."),
                            div(class = "btn-group-container", style = "display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; margin-top: 20px;",
                                actionButton("class_6_tel_aviv", label = "Tel Aviv", class = "btn", style = "width: 150px; text-align: center;"),
                                actionButton("class_6_jerusalem", label = "Jerusalem", class = "btn", style = "width: 150px; text-align: center;"),
                                actionButton("class_6_hamburg", label = "Hamburg", class = "btn", style = "width: 150px; text-align: center;"),
                                actionButton("class_6_berlin", label = "Berlin", class = "btn", style = "width: 150px; text-align: center;")
                            )
                        ),
                        div(
                          style = "display: flex; flex-direction: column; width: 100%; height: 100%; gap: 2px; margin-top: 2px; text-align: center; align-items: center;",
                          selectInput(
                            "confidence_6", 
                            label = "How confident are you in your decision?",
                            choices = c("", "Very unsure", "Unsure", "Neutral", "Sure", "Very sure"),
                            selected = ""
                          )
                        )
                    ),
                    div(style = "background-color: #ffffff; border-radius: 8px; display: flex; flex: 1; flex-basis: 72%; padding: 15px; flex-direction: column; align-items: center;",  
                        div(style = "width: 100%; text-align: left; margin-bottom: 10px;",
                            p("Review these highlighted areas carefully. This is an attention check. Please ", span(style = "color: #FFA500; font-weight: bold;", "highlight the yellow sign that says 'Berlin'"), " using the annotation tool. Before proceeding, ensure that you’ve marked the sign which says 'Berlin'.")
                        ),
                        # Display the image for annotation
                        div(style = paste("display: flex; justify-content: center; align-items: center; width:", img_width, "px; height:", img_height, "px; padding: 0; margin: 0;"),
                            plotOutput("imagePlot_6", click = "image_click_6", 
                                       width = paste0(img_width, "px"), height = paste0(img_height, "px"))
                        ),
                        div(style = "display: flex; gap: 10px; margin-top: 5px; justify-content: center;",  
                            actionButton("clear_6", "Clear All Shapes", icon = icon("trash"), 
                                         class = "btn-secondary", style = "padding: 5px 7px; font-size: 12px;"),  
                            actionButton("delete_last_polygon_6", "Delete Last Shape", icon = icon("trash"), 
                                         class = "btn-secondary", style = "padding: 5px 7px; font-size: 12px;"),  
                            # Add in the UI section where other action buttons are defined
                            actionButton("delete_last_corner", "Delete Last Corner", icon = icon("trash"), 
                                         class = "btn-secondary", style = "padding: 5px 7px; font-size: 12px;"),
                            actionButton("end_polygon_6", "Complete Shape", icon = icon("check"), 
                                         class = "btn-secondary", style = "padding: 5px 7px; font-size: 12px;"),  
                            actionButton("next_page", "Next", icon = icon("arrow-right"), 
                                         class = "btn-primary", style = "padding: 5px 7px; font-size: 12px;")  
                        )
                    )
                )
            )
        )
      )
    } else if (current_page >= 6 && current_page <= 11 && current_page != 10) {  # Annotation pages
      # Reset polygon ID
      coords(tibble(x = numeric(), y = numeric(), polygon_id = integer(), name = character()))
      polygon_id(1)  
      
      # Load Image
      if (current_page == 11){
        i <- current_page - 6
      } else {
        i <- current_page - 5
      }
      
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
                            p("Take a close look at the image. Do you agree with the AI’s classification of this image as ",   span(class_number)," or would you assign it to a different city? Please ", strong(style = "color: #FFA500;", "select your choice"), " below."),
                            div(class = "btn-group-container", style = "display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; margin-top: 20px;",
                                actionButton(inputId = paste0("class_", i, "_tel_aviv"), label = "Tel Aviv", class = "btn", style = "width: 150px; text-align: center;"),
                                actionButton(inputId = paste0("class_", i, "_jerusalem"), label = "Jerusalem", class = "btn", style = "width: 150px; text-align: center;"),
                                actionButton(inputId = paste0("class_", i, "_hamburg"), label = "Hamburg", class = "btn", style = "width: 150px; text-align: center;"),
                                actionButton(inputId = paste0("class_", i, "_berlin"), label = "Berlin", class = "btn", style = "width: 150px; text-align: center;")
                            )
                        ),
                        div(
                          style = "display: flex; flex-direction: column; width: 100%; height: 100%; gap: 2px; margin-top: 2px; text-align: center; align-items: center;",
                          selectInput(
                            inputId = paste0("confidence_", i), 
                            label = "How confident are you in your decision?",
                            choices = c("", "Very unsure", "Unsure", "Neutral", "Sure", "Very sure"),
                            selected = ""
                          )
                        )
                        
                    ),
                    div(style = "background-color: #ffffff; border-radius: 8px; display: flex; flex: 1; flex-basis: 72%; padding: 15px; flex-direction: column; align-items: center;",  
                        div(style = "width: 100%; text-align: left; margin-bottom: 10px;",
                            p("Review these highlighted areas carefully. Which parts of the image led you to your decision? Please ", span(style = "color: #FFA500; font-weight: bold;", "mark these key areas as precisely as possible"), " using the annotation tool. Before proceeding, ensure that you’ve marked all features you consider important.")
                        ),
                        # Outer div to center the image
                        div(style = paste("display: flex; justify-content: center; align-items: center; width:", img_width, "px; height:", img_height, "px; padding: 0; margin: 0;"),
                            plotOutput(paste0("imagePlot", i), click = paste0("image_click_", i),
                                       width = paste0(img_width, "px"), height = paste0(img_height, "px"))
                        ),
                        div(style = "display: flex; gap: 10px; margin-top: 5px; justify-content: center;",  
                            actionButton(paste0("clear_", i), "Clear All Shape", icon = icon("trash"), 
                                         class = "btn-secondary", style = "padding: 5px 7px; font-size: 12px;"),  
                            actionButton(paste0("delete_last_polygon", i), "Delete Last Shape", icon = icon("trash"), 
                                         class = "btn-secondary", style = "padding: 5px 7px; font-size: 12px;"),  
                            # Add in the UI section where other action buttons are defined
                            actionButton("delete_last_corner", "Delete Last Corner", icon = icon("trash"), 
                                         class = "btn-secondary", style = "padding: 5px 7px; font-size: 12px;"),
                            actionButton(paste0("end_polygon_", i), "Complete Shape", icon = icon("check"), 
                                         class = "btn-secondary", style = "padding: 5px 7px; font-size: 12px;"),  
                            actionButton("next_page", "Next", icon = icon("arrow-right"), 
                                         class = "btn-primary", style = "padding: 5px 7px; font-size: 12px;")  
                        )
                    )
                )
            )
        )
      )
    } else if (current_page == 12) {
      tagList(
        div(style = "text-align: center; margin-bottom: 20px;",
            h3("Almost There! Answer the Final Two Questions to Finish!")
        ),
        
        div(style = "background-color: #f9f9f9; padding: 20px; border-radius: 8px; max-width: 600px; margin: 0 auto; box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);",
            
            # Question 1
            div(style = "margin-bottom: 20px;",
                p("In which of the following Cities have you ever ", strong("lived"), " ?"),
                checkboxGroupInput("q1", label = NULL, choices = c("Berlin", "Hamburg", "Tel Aviv", "Jerusalem", "None"), selected = character(0), inline = TRUE)
            ),
            
            # Question 2
            div(style = "margin-bottom: 20px;",
                p("Which of the following Cities have you ever ", strong("visited"), " ?"),
                checkboxGroupInput("q2", label = NULL, choices = c("Berlin", "Hamburg", "Tel Aviv", "Jerusalem", "None"), selected = character(0), inline = TRUE)
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
            
            h3("🎉 Study Complete! Thank You for Your Contribution! 🎉", 
               style = "font-weight: bold; color: #4CAF50; margin-bottom: 20px;"),
            
            p("We appreciate your time and effort in participating. All annotated images have been saved successfully.", 
              style = "font-size: 16px; color: #555; margin-bottom: 15px;"),
            
            p("Your responses will be reviewed shortly, and we’ll confirm your participation. Thank you for contributing to this research!", 
              style = "font-size: 16px; color: #555;"),
            
            p("Your Prolific Completion Code is XYZ. You may now close this window and continue in Prolific!", 
              style = "font-size: 16px; color: #0000FF;"),
            
            
        )
      )
    }
  })
  
  
  
  ############################################################################## 
  
  # Render the plot with the loaded image and handle annotations
  output$imagePlot_6 <- renderPlot({
    # Render the image and display any drawn polygons
    img_raster <- as.raster(loaded_image)
    par(bg = NA, mar = c(0, 0, 0, 0))  # Transparent background with no margins
    
    # Plot the image without borders or axis labels
    plot(img_raster, xlab = "", ylab = "", bty = "n", asp = img_height / img_width)
    
    # Draw existing annotations (polygons) on the image
    all_polygons <- coords() %>% filter(name == "polygon_6")
    for (poly_id in unique(all_polygons$polygon_id)) {
      polygon_coords <- all_polygons %>% filter(polygon_id == poly_id)
      
      # Display points if at least one point exists
      if (nrow(polygon_coords) >= 1) {
        points(polygon_coords$x, polygon_coords$y, col = "orange", pch = 15, cex = 1.5)  # Draw points
      }
      
      if (nrow(polygon_coords) >= 2) {
        # Draw lines between consecutive points
        lines(polygon_coords$x, polygon_coords$y, col = "orange", lwd = 2)
      }
      if (nrow(polygon_coords) > 2) {
        # Complete the polygon if more than 2 points exist
        polygon(polygon_coords$x, polygon_coords$y, border = "orange", col = rgb(1, 0.65, 0, alpha = 0.5))
      }
    }
  })
  
  # Render the plot with the loaded image and handle annotations
  output$imagePlot_uebung <- renderPlot({
    # Render the image and display any drawn polygons
    img_raster <- as.raster(loaded_image_ueb)
    par(bg = NA, mar = c(0, 0, 0, 0))  # Transparent background with no margins
    
    # Plot the image without borders or axis labels
    plot(img_raster, xlab = "", ylab = "", bty = "n", asp = img_height / img_width)
    
    
    # Draw existing annotations (polygons) on the image
    all_polygons <- coords() %>% filter(name == "polygon_uebung")
    for (poly_id in unique(all_polygons$polygon_id)) {
      polygon_coords <- all_polygons %>% filter(polygon_id == poly_id)
      # Display points if at least one point exists
      if (nrow(polygon_coords) >= 1) {
        points(polygon_coords$x, polygon_coords$y, col = "orange", pch = 15, cex = 1.5)  # Draw points
      }
      if (nrow(polygon_coords) >= 2) {
        # Draw lines between consecutive points
        lines(polygon_coords$x, polygon_coords$y, col = "orange", lwd = 2)
      }
      if (nrow(polygon_coords) > 2) {
        # Complete the polygon if more than 2 points exist
        polygon(polygon_coords$x, polygon_coords$y, border = "orange", col = rgb(1, 0.65, 0, alpha = 0.5))
      }
    }
    
  })
  
  
  
  
  
  # Capture and store clicks for annotation
  observeEvent(input$image_click_6, {
    current_coords <- coords()
    polygon_id_val <- polygon_id()
    adjusted_x <- input$image_click_6$x
    adjusted_y <- input$image_click_6$y
    
    # Add the clicked point to the polygon being drawn
    current_coords <- add_row(
      current_coords,
      x = adjusted_x,
      y = adjusted_y,
      polygon_id = polygon_id_val,
      name = "polygon_6"
    )
    coords(current_coords)
  })
  
  # Capture and store clicks for annotation
  observeEvent(input$image_click_uebung, {
    current_coords <- coords()
    polygon_id_val <- polygon_id()
    
    adjusted_x <- input$image_click_uebung$x
    adjusted_y <- input$image_click_uebung$y
    
    # Add the clicked point to the polygon being drawn
    current_coords <- add_row(
      current_coords,
      x = adjusted_x,
      y = adjusted_y,
      polygon_id = polygon_id_val,
      name = "polygon_uebung"
    )
    coords(current_coords)
  })
  
  
  # Clear all annotations for this image
  observeEvent(input$clear_6, {
    coords(coords() %>% filter(name != "polygon_6"))
  })
  
  # Clear all annotations for this image
  observeEvent(input$clear_uebung, {
    coords(coords() %>% filter(name != "polygon_uebung"))
  })
  
  
  
  
  # Delete the last drawn polygon for this image
  observeEvent(input$delete_last_polygon_6, {
    current_coords <- coords()
    max_polygon_id <- max(current_coords %>% filter(name == "polygon_6") %>% pull(polygon_id), na.rm = TRUE)
    
    updated_coords <- current_coords %>% filter(!(name == "polygon_6" & polygon_id == max_polygon_id))
    coords(updated_coords)
  })
  
  # Delete the last drawn polygon for this image
  observeEvent(input$delete_last_polygon_uebung, {
    current_coords <- coords()
    max_polygon_id <- max(current_coords %>% filter(name == "polygon_uebung") %>% pull(polygon_id), na.rm = TRUE)
    
    updated_coords <- current_coords %>% filter(!(name == "polygon_uebung" & polygon_id == max_polygon_id))
    coords(updated_coords)
  })
  
  
  
  # Finalize the current polygon and start a new one
  observeEvent(input$end_polygon_6, {
    polygon_id(polygon_id() + 1)
  })
  
  # Finalize the current polygon and start a new one
  observeEvent(input$end_polygon_uebung, {
    polygon_id(polygon_id() + 1)
  })
  
  
  # Observers for the city selection buttons on page 6
  observeEvent(input$class_6_tel_aviv, { selected_city_6("Tel Aviv") })
  observeEvent(input$class_6_jerusalem, { selected_city_6("Jerusalem") })
  observeEvent(input$class_6_hamburg, { selected_city_6("Hamburg") })
  observeEvent(input$class_6_berlin, { selected_city_6("Berlin") })
  
  # Observer for the confidence level dropdown on page 6
  observeEvent(input$confidence_6, { confidence_level_6(input$confidence_6) })
  
  
  
  
  
  ##############################################################################  
  
  
  
  # Observers for annotation functionality and handling clicks
  lapply(1:6, function(i) {
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
    lapply(1:6, function(i) {
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
    
    # Observers to handle dropdown selection and save the value
    lapply(1:6, function(i) {
      observeEvent(input[[paste0("confidence_", i)]], {
        confidence_list <- selected_confidence()
        confidence_list[i] <- input[[paste0("confidence_", i)]]
        selected_confidence(confidence_list)
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
      
      # Draw existing annotations (polygons) on the image
      all_polygons <- coords() %>% filter(name == paste("polygon", i))
      for (poly_id in unique(all_polygons$polygon_id)) {
        polygon_coords <- all_polygons %>% filter(polygon_id == poly_id)
        # Display points if at least one point exists
        if (nrow(polygon_coords) >= 1) {
          points(polygon_coords$x, polygon_coords$y, col = "orange", pch = 15, cex = 1.5)  # Draw points
        }
        if (nrow(polygon_coords) >= 2) {
          # Draw lines between consecutive points
          lines(polygon_coords$x, polygon_coords$y, col = "orange", lwd = 2)
        }
        if (nrow(polygon_coords) > 2) {
          # Complete the polygon if more than 2 points exist
          polygon(polygon_coords$x, polygon_coords$y, border = "orange", col = rgb(1, 0.65, 0, alpha = 0.5))
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
  
  # Observer to delete only the last point added to the current (latest) polygon
  observeEvent(input$delete_last_corner, {
    current_page <- page()
    current_coords <- coords()
    current_polygon_id <- polygon_id()  # ID of the current polygon
    
    # Apply logic specifically for page 9
    if (current_page == 9) {
      # Filter points specifically for the polygon on page 9
      latest_polygon_points <- current_coords %>% filter(name == "polygon_6", polygon_id == current_polygon_id)
    } else {
      # Use the standard approach for other pages
      latest_polygon_points <- current_coords %>% filter(polygon_id == current_polygon_id)
    }
    
    # Proceed with deletion if there are points to delete
    if (nrow(latest_polygon_points) > 0) {
      # Find the index of the last point in the current polygon
      last_point_index <- tail(which(current_coords$polygon_id == current_polygon_id), 1)
      
      # Delete the last point and explicitly update `coords`
      updated_coords <- current_coords[-last_point_index, ]
      
      # Clear `coords()` to enforce the reactive update
      coords(NULL)  
      Sys.sleep(0.1)  # Add a short delay to allow complete update
      
      # Assign the updated coordinates back to `coords`
      coords(updated_coords)
    }
  })
  
  
  
  
  
  
  
  
  
  
  
  ############################################################################## 
  
  
  observeEvent(input$user_id_input, {
    user_id(input$user_id_input)
  })
  
  # Store responses to the questions
  observeEvent(input$q1, {
    q1_response(input$q1)
  })
  observeEvent(input$q2, {
    q2_response(input$q2)
  })
  
  
  
  ############################################################################## 
  
  
  observeEvent(input$next_page_step_1, {
    current_step <- step()
    step(current_step + 1) # Increase the step by 1 each time
    session$sendCustomMessage("showNextDiv", step())
  })
  
  observeEvent(input$next_page_step_2, {
    current_step <- step()
    step(current_step + 1) # Increase the step by 1 each time
    session$sendCustomMessage("showNextDiv", step())
  })
  
  observeEvent(input$next_page_step_3, {
    current_step <- step()
    step(current_step + 1) # Increase the step by 1 each time
    session$sendCustomMessage("showNextDiv", step())
  })
  
  
  observeEvent(input$next_page_step_1, {
    shinyjs::hide("next_page_step_1")  # Hide the button after clicking
    # Rest of the code for this step
  })
  
  observeEvent(input$next_page_step_2, {
    shinyjs::hide("next_page_step_2")  # Hide the button after clicking
    # Rest of the code for this step
  })
  
  observeEvent(input$next_page_step_3, {
    shinyjs::hide("next_page_step_3")  # Hide the button after clicking
    # Rest of the code for this step
  })
  
  
  
  # Page navigation handling
  observeEvent(input$next_page, {
    current_page <- page()
    
    if (current_page == 10) {
      # Save only if both a city is selected and there is an annotation
      polygon_coords <- coords() %>% filter(name == paste("polygon_6"))
      annotation_missing <- nrow(polygon_coords) < 3  
      city_not_selected <- selected_city_6() == ""
      confidence_level_missing <- confidence_level_6() == ""
      
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
      } else if (confidence_level_missing) {
        showModal(modalDialog(
          title = "Please choose a confidence level!",
          "Make sure to select a confidence level before proceeding.",
          easyClose = TRUE
        ))
      } else if (city_not_selected) {
        showModal(modalDialog(
          title = "Please choose a city!",
          "Make sure to select a city before proceeding.",
          easyClose = TRUE
        ))
      } else {
        if (selected_city_6() != "Berlin") {
          # User failed the attention check
          fail_text_path <- tempfile(fileext = ".txt")
          writeLines(paste("User ID:", user_id(), "\nStatus: Failed Attention Check"), fail_text_path)
          
          # Specify the new Nextcloud folder
          save_to_nextcloud(fail_text_path, fail_folder, paste0("treatment_", user_id(), ".txt"), username, password)
          # Move to the next page after processing
        } 
        
        # Proceed with saving if both values are present
        selected_class <- selected_city_6()
        confidence_level <- confidence_level_6()
        input_filename <- "test"
        
        # Progressively update the progress bar and save
        showModal(modalDialog(
          title = "Saving, this might take a moment...",
          progressBar(id = "save_progress", value = 0, display_pct = TRUE),
          footer = NULL,
          easyClose = FALSE
        ))
        
        # Save the annotations and data
        polygon_coords <- coords() %>% filter(name == "polygon_6")
        
        for (progress in seq(0, 100, by = 20)) {
          Sys.sleep(0.2)
          updateProgressBar(session, id = "save_progress", value = progress)
        }
        
        # Load the image and adjust coordinates
        img <- image_read("www/berlin_attention_check_Berlin_Hamburg.png")
        img_height <- image_info(img)$height
        save_coords <- polygon_coords %>% mutate(y = img_height - y)
        
        # Save adjusted coordinates to CSV and upload to Nextcloud
        csv_temp_path <- tempfile(fileext = ".csv")
        write.csv(save_coords, csv_temp_path, row.names = FALSE)
        save_to_nextcloud(csv_temp_path, csv_attention_cloud_folder, paste0("treatment_", user_id(), "_", input_filename, "_", selected_class, "_", confidence_level, ".csv"), username, password)
        
        # Draw polygons on the image for saving
        img <- image_draw(img)
        for (poly_id in unique(save_coords$polygon_id)) {
          poly_coords <- save_coords %>% filter(polygon_id == poly_id)
          polygon(poly_coords$x, poly_coords$y, border = "orange", col = rgb(1, 0.65, 0, alpha = 0.5))
        }
        dev.off()  # Close the drawing device
        
        # Save the annotated image temporarily and upload to Nextcloud
        img_temp_path <- tempfile(fileext = ".png")
        image_write(img, path = img_temp_path, format = "png")
        save_to_nextcloud(img_temp_path, img_attention_cloud_folder, paste0("treatment_", user_id(), "_", input_filename, "_", selected_class, "_", confidence_level, ".png"), username, password)
        
        removeModal()
        page(current_page + 1)   # Move to the next page after processing
      }
    }
    else if (current_page == 5) {
      # Proceed with saving if both values are present
      input_filename <- "uebung"
      
      # Adjust the coordinates for saving as before
      polygon_coords <- coords() %>% filter(name == "polygon_uebung")
      
      # Load the image and adjust coordinates
      img <- image_read("www/ueben_img.png")
      img_height <- image_info(img)$height
      save_coords <- polygon_coords %>% mutate(y = img_height - y)  # Flip y-coordinates
      
      annotation_missing <- nrow(polygon_coords) < 3  
      
      if (annotation_missing) {
        showModal(modalDialog(
          title = "Please annotate the picture!",
          "Make sure to annotate the picture before proceeding.",
          easyClose = TRUE
        ))
        return()  # Exit if annotations are missing
      }
      
      # Draw polygons on the image for saving
      img <- image_draw(img)
      for (poly_id in unique(save_coords$polygon_id)) {
        poly_coords <- save_coords %>% filter(polygon_id == poly_id)
        polygon(poly_coords$x, poly_coords$y, border = "orange", col = rgb(1, 0.65, 0, alpha = 0.5))
      }
      dev.off()  # Close the drawing device
      
      # Save the annotations and data
      # Progressively update the progress bar and save
      showModal(modalDialog(
        title = "Saving, this might take a moment...",
        progressBar(id = "save_progress", value = 0, display_pct = TRUE),
        footer = NULL,
        easyClose = FALSE
      ))
      
      # Progressively update the progress bar during saving
      for (progress in seq(0, 100, by = 20)) {
        Sys.sleep(0.2)
        updateProgressBar(session, id = "save_progress", value = progress)
      }
      
      # Save adjusted coordinates to CSV and upload to Nextcloud
      csv_temp_path <- tempfile(fileext = ".csv")
      write.csv(save_coords, csv_temp_path, row.names = FALSE)
      save_to_nextcloud(csv_temp_path, csv_uebung_cloud_folder, paste0("treatment_", user_id(), "_", input_filename, ".csv"), username, password)
      
      
      # Save the annotated image temporarily and upload to Nextcloud
      img_temp_path <- tempfile(fileext = ".png")
      image_write(img, path = img_temp_path, format = "png")
      save_to_nextcloud(img_temp_path, img_uebung_cloud_folder, paste0("treatment_", user_id(), "_", input_filename, ".png"), username, password)
      
      removeModal()
      page(current_page + 1)   # Move to the next page after processing
      
      
    } else if (current_page >= 6 && current_page <= 11 && current_page != 10) {
      
      if (current_page == 11){
        i <- current_page - 6
      } else {
        i <- current_page - 5
      }
      
      selected_class <- selected_city()[i]  # Get selected city for current image
      confidence_level <- selected_confidence()[i]  # Get selected confidence for current image
      
      input_filename <- tools::file_path_sans_ext(basename(selected_images[i]))
      class_AI <- extract_class_from_filename(selected_images[i])
      
      # Save only if both a city is selected and there is an annotation
      polygon_coords <- coords() %>% filter(name == paste("polygon", i))
      annotation_missing <- nrow(polygon_coords) < 3  
      city_not_selected <- selected_class == ""
      confidence_level_missing <- confidence_level == ""
      
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
      } else if (confidence_level_missing) {
        showModal(modalDialog(
          title = "Please choose a confidence level!",
          "Make sure to select a confidence level before proceeding.",
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
          title = "Saving, this might take a moment...",
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
        save_to_nextcloud(csv_temp_path, csv_cloud_folder, paste0("treatment_", user_id(), "_", input_filename, "_", selected_class,  "_",  confidence_level, ".csv"), username, password)
        
        # Draw polygons on the image for saving
        img <- image_draw(img)
        for (poly_id in unique(save_coords$polygon_id)) {
          poly_coords <- save_coords %>% filter(polygon_id == poly_id)
          polygon(poly_coords$x, poly_coords$y, border = "orange", col = rgb(1, 0.65, 0, alpha = 0.5))
        }
        dev.off()
        
        # Save the annotated image temporarily and upload to Nextcloud
        img_temp_path <- tempfile(fileext = ".png")
        image_write(img, path = img_temp_path, format = "png")
        save_to_nextcloud(img_temp_path, img_cloud_folder, paste0("treatment_", user_id(), "_", input_filename, "_", selected_class, "_",  confidence_level, ".png"), username, password)
        
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
    } else if (current_page == 2) {  # Check consent on page 2
      if (is.null(input$consent_checkbox) || !input$consent_checkbox) {
        showModal(modalDialog(
          title = "Consent Required",
          "You must check the consent box to proceed.",
          easyClose = TRUE
        ))
        return()  # Stop further execution if consent is not given
      } else {
        page(current_page + 1)  # Move to the next page
      }
    } else if (current_page == 12) {  # Last page to save the questionnaire responses
      # Check if both questions have at least one selected value
      if (is.null(input$q1) || length(input$q1) == 0 || 
          is.null(input$q2) || length(input$q2) == 0) {
        # Show a warning if any question is unanswered
        print("Both questions not answered")  # Debugging message
        showModal(modalDialog(
          title = "Please answer both questions",
          "Make sure to select at least one option for both questions before proceeding.",
          easyClose = TRUE
        ))
      } else {
        # Prepare responses for saving
        q1_responses <- paste(input$q1, collapse = ", ")
        q2_responses <- paste(input$q2, collapse = ", ")
        
        # Create a tibble to store responses
        response_data <- tibble(
          user_id = user_id(),
          q1_responses = q1_responses,
          q2_responses = q2_responses
        )
        
        # Save responses locally or to Nextcloud
        csv_temp_path <- tempfile(fileext = ".csv")
        write_csv(response_data, csv_temp_path)
        
        # Save to Nextcloud
        save_to_nextcloud(
          csv_temp_path, 
          question_folder, 
          paste0("treatment_", user_id(), "_questions.csv"), 
          username, 
          password
        )
        
        page(13)  # Set to the last page number directly
      }
    } else {
      page(current_page + 1)  # Move to the next page for non-image pages
    }
  })
  
  
  observeEvent(input$close_app, {
    session$sendCustomMessage(type = "jsCode", list(code = "closeWindow()"))
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
