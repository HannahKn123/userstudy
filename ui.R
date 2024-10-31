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
        padding: 20px; /* Reduced padding */
        background-color: #ffffff;
        border: 2px solid #d3d3d3;
        border-radius: 10px;
        margin-bottom: 15px; /* Reduced margin */
        position: relative;
        width: 80%; /* Adjusts width for a more compact look */
        margin-left: auto;
        margin-right: auto;
      }
      .highlight-container h4, .decision-container h4 {
        margin-top: 0;
        font-weight: bold;
        font-size: 14px; /* Smaller font size */
        color: #ffffff; /* White text for better contrast */
        padding: 8px 12px; /* Reduced padding */
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
        padding-bottom: 15px;
        margin-bottom: 15px;
        border-bottom: 2px solid #d3d3d3; /* Divider line for separation */
      }
      .highlight-instructions {
        margin-top: 25px; /* Additional spacing before highlight instructions */
        font-weight: bold;
      }
      .image-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 20px; /* Adjusted padding */
        background-color: #f0f9ff;
        border-radius: 10px;
        box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.05);
      }
      .highlight-text {
        margin-top: 30px;
      }
      /* Style for the dropdown menu */
      .custom-dropdown select {
        color: #4169E1; /* Set dropdown text color to blue */
      }
    "))
  ),
  
  div(class = "image-container",
      uiOutput("page_content"),
      shinyjs::hidden(div(id = "loading_msg", "Saving, please wait..."))
  )
)
