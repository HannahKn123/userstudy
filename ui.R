ui <- fluidPage(
  useShinyjs(),
  tags$head(
    tags$link(rel = "stylesheet", href = "https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap"),
    tags$style(HTML("
      body {
        font-family: 'Roboto', sans-serif;
        background-color: #f8f9fa;
        color: #333;
      }
      h3, h4 {
        font-weight: 700;
        color: #4a4a4a;
      }
      .highlight-container, .decision-container {
        padding: 15px;
        background-color: #ffffff;
        border: 2px solid #d3d3d3;
        border-radius: 10px;
        margin-bottom: 15px;
        position: relative;
        width: 100%;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
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
      }
      .highlight-container h4 {
        background-color: #d3d3d3;
      }
      .decision-container h4 {
        background-color: #d3d3d3;
      }
      .classification-section {
        padding-bottom: 10px;
        margin-bottom: 10px;
        border-bottom: 2px solid #d3d3d3;
      }
      .custom-dropdown select {
        color: #4169E1;
      }
      /* Style to display two lines side by side */
      .flex-container {
        display: flex;
        gap: 10px; /* Add space between the two lines */
        align-items: center; /* Vertically aligns text in the middle */
      }
    "))
  ),
  
  div(class = "image-container",
      uiOutput("page_content"),
      shinyjs::hidden(div(id = "loading_msg", "Saving, please wait..."))
  )
)