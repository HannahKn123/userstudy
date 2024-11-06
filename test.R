# ui.R
library(shiny)

ui <- fluidPage(
  titlePanel("Likert-Skala Bewertung"),
  sidebarLayout(
    sidebarPanel(
      h3("Bewerte die folgende Aussage:"),
      p("„Ich bin mit der Benutzerfreundlichkeit dieser App zufrieden.“"),
      
      radioButtons("likert", "Bitte wähle eine Bewertung:",
                   choices = list(
                     "1 - Stimme überhaupt nicht zu" = 1,
                     "2 - Stimme nicht zu" = 2,
                     "3 - Neutral" = 3,
                     "4 - Stimme zu" = 4,
                     "5 - Stimme vollkommen zu" = 5
                   )),
      
      actionButton("submit", "Bewertung abschicken")
    ),
    mainPanel(
      h4("Ergebnis"),
      textOutput("response")
    )
  )
)

# server.R
server <- function(input, output, session) {
  observeEvent(input$submit, {
    output$response <- renderText({
      paste("Du hast die Bewertung:", input$likert, "gewählt.")
    })
  })
}

# App starten
shinyApp(ui = ui, server = server)
