library(shiny)
library(shinyjs)

ui <- fluidPage(
  useShinyjs(),
  
  # Link to Google Fonts
  tags$head(
    tags$link(rel = "stylesheet", href = "https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap"),
    
    # Custom CSS for button styles and layout
    tags$style(HTML("
      .btn-group-container .btn {
        display: inline-block;
        padding: 8px 12px;
        margin: 5px;
        background-color: #d3d3d3; /* Gray background for unselected buttons */
        color: white;
        border: none;
        border-radius: 4px;
        font-weight: bold;
        cursor: pointer;
        text-align: center;
      }
      .btn-group-container .btn:hover {
        background-color: #b0b0b0; /* Slightly darker gray on hover */
      }
      .btn-group-container .btn.selected {
        background-color: #4169E1; /* Distinct color for selected button */
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
        max-width: 1200px;
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
        width: 140px;
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
    "))
  ),
  
  # JavaScript to toggle "selected" class on clicked buttons
  tags$script(HTML("
    $(document).on('click', '.btn-group-container .btn', function() {
      $(this).addClass('selected').siblings().removeClass('selected');
    });
  ")),
  
  # Main UI container
  div(class = "image-container",
      uiOutput("page_content"),
      shinyjs::hidden(div(id = "loading_msg", "Saving, please wait..."))
  )
)
