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



source("ui.R")
source("server.R")

shinyApp(ui = ui, server = server)