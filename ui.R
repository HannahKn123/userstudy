library(shiny)
library(shinyjs)

ui <- fluidPage(
  useShinyjs(),
  # Link to Google Fonts
  tags$head(
    tags$link(rel = "stylesheet", href = "https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap"),
    # Custom CSS for button styles and layout
    tags$style(HTML("
      .shiny-plot-output {
        padding: 0 !important;
        margin: 0 !important;
        border: none !important;
        background-color: transparent !important;
      }
      .image-container {
        background-color: transparent !important;
      }
      .btn-group-container .btn {
        display: inline-block;
        padding: 8px 12px;
        margin: 5px;
        background-color: #d3d3d3;
        color: white;
        border: none;
        border-radius: 4px;
        font-weight: bold;
        cursor: pointer;
        text-align: center;
      }
      .btn-group-container .btn:hover {
        background-color: #b0b0b0;
      }
      .btn-group-container .btn.selected {
        background-color: #4169E1;
        border-color: #4169E1;
      }
    
      body {
        font-family: 'Roboto', sans-serif;
        background-color: #f8f9fa;
        color: #333;
        padding-top: 20px;
      }
      h3, h4 {
        font-weight: 700;
        color: #4a4a4a;
      }
      .highlight-container, .decision-container {
        padding: 25px;
        background-color: #ffffff;
        border: 2px solid #d3d3d3;
        border-radius: 10px;
        margin: 50px auto 20px auto;
        width: 100%;
        max-width: 1500px;
        text-align: left;
        display: flex;
        align-items: center;
        position: relative;
      }
      .highlight-container h4, .decision-container h4 {
        margin-top: 0;
        font-weight: bold;
        font-size: 14px;
        color: #ffffff;
        padding: 8px 12px;
        border-radius: 5px;
        position: absolute;
        top: -12px;
        left: 20px;
        text-align: center;
        width: 200px;
      }
      .highlight-container h4 {
        background-color: #d3d3d3;
      }
      .decision-container h4 {
        background-color: #d3d3d3;
      }
      .flex-container {
        display: flex;
        gap: 40px;
        align-items: center;
        justify-content: center;
      }
      .flex-box {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
      }
      .custom-dropdown select {
        color: #4169E1;
      }
      .left-align-text { 
        text-align: left;
      }
      
      /* Disable hover and active styling for tabs */
      .nav-tabs .nav-link {
        color: gray;
        pointer-events: none; /* Disable clicking */
        cursor: default; /* No pointer cursor */
      }
      .nav-tabs .nav-link:hover,
      .nav-tabs .nav-link:active {
        background-color: transparent;
        color: gray;
      }
    "))
  ),
  
  tags$style(HTML("
    .nav-tabs {
      font-size: 12px; /* Smaller font size */
      font-weight: normal; /* Remove bold styling */
      padding: 0px; /* Remove padding for compact appearance */
    }
    
    .nav-tabs > li > a {
      color: #888; /* Set a light color to make tabs less prominent */
      background-color: #f5f5f5; /* Subtle background color */
      padding: 5px 10px; /* Smaller padding for compact tabs */
      border: 1px solid #ddd; /* Light border to blend with background */
      border-radius: 4px;
    }
  
    .nav-tabs > li > a:hover {
      color: #555; /* Slightly darker color on hover */
      background-color: #e9e9e9; /* Subtle color change on hover */
    }
  
    .nav-tabs > li.active > a {
      color: #333; /* Slightly darker color for active tab */
      background-color: #e0e0e0; /* Light background for active tab */
    }
    .nav-tabs > li > a { pointer-events: none; 
    }
  ")),
  
  
  tabsetPanel(
    id = "main_tab",
    tabPanel("Welcome", uiOutput("page_content"), value = "tab_1"),
    tabPanel("Introduction", uiOutput("page_content"), value = "tab_2"),
    tabPanel("Annotation Instructions", uiOutput("page_content"), value = "tab_3"),
    tabPanel("1", uiOutput("page_content"), value = "tab_4"),
    tabPanel("2", uiOutput("page_content"), value = "tab_5"),
    tabPanel("3", uiOutput("page_content"), value = "tab_6"),
    tabPanel("4", uiOutput("page_content"), value = "tab_7"),
    tabPanel("5", uiOutput("page_content"), value = "tab_8"),
    tabPanel("6", uiOutput("page_content"), value = "tab_9"),
    tabPanel("7", uiOutput("page_content"), value = "tab_10"),
    tabPanel("8", uiOutput("page_content"), value = "tab_11"),
    tabPanel("9", uiOutput("page_content"), value = "tab_12"),
    tabPanel("10", uiOutput("page_content"), value = "tab_13"),
    tabPanel("Survey", uiOutput("page_content"), value = "tab_14"),
    tabPanel("Done!", uiOutput("page_content"), value = "tab_15")
  ),
  
  div(class = "image-container",
      uiOutput("page_content"),
      shinyjs::hidden(div(id = "loading_msg", "Saving, please wait..."))
  )
)
