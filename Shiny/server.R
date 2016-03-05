ds <- read.table('http://hsequantling.wikispaces.com/file/view/all_words.csv',sep=',',encoding = 'UTF-8',header = T) 

library(shiny) 

# Load the ggplot2 package which provides 
# the 'mpg' dataset. 
library(ggplot2) 

# Define a server for the Shiny app 
shinyServer(function(input, output) { 
  
  # Filter data based on selections 
  output$table <- DT::renderDataTable(DT::datatable({ 
    data <- ds 
    if (input$lang != "All languages") { 
      data <- data[ds$lang == input$lang,] 
    } 
    data 
  })) 
  
}) 