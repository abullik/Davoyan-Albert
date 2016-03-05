ds <- read.table('http://hsequantling.wikispaces.com/file/view/all_words.csv',sep=',',encoding = 'UTF-8',header = T) 

library(shiny) 
library(ggplot2) 

shinyUI( 
  fluidPage( 
    titlePanel("One thousand Most Frequently Used Words"), 
    
    fluidRow( 
      column(4, 
             selectInput("lang", 
                         "Choose language:", 
                         c("All languages", 
                           unique(as.character(ds$language)))) 
      ), 
      column(8, 
             helpText("Это приложение показывает 1000 самых частотных слов некоторых языков. Данные основаны на материалах сайта http://www.101languages.net/common-words/. Нельзя гарантировать, что данные собраны хорошо (процесс сбора данных на сайте не описан), ровно как и не стоит верить переводам.") 
      ) 
    ), 
    
    fluidRow( 
      DT::dataTableOutput("table") 
    ) 
  ) 
)