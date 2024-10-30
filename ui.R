library(shiny)
library(magick)
library(shinyjs)
library(readr)
library(tidyverse)

ui <- fluidPage(
  useShinyjs(),
  tags$head(
    tags$style(HTML("
      body {
        font-family: Arial, sans-serif;
        background-color: #f5f7fa;
        color: #333;
      }
      h3 {
        font-weight: bold;
        color: #2c3e50;
      }
      .main-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
      }
      .image-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        background-color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0px 0px 12px rgba(0, 0, 0, 0.1);
      }
      .btn-primary, .btn-secondary {
        color: #ffffff !important;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        border-radius: 4px;
      }
      .btn-primary {
        background-color: #3498db;
      }
      .btn-secondary {
        background-color: #95a5a6;
      }
      .select-input {
        margin-top: 15px;
        font-size: 16px;
      }
    "))
  ),
  
  div(class = "main-container",
      uiOutput("page_content")
  )
)