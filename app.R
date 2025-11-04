library(shiny)
library(bslib)
library(shinydashboard)
library(shinybusy)
library(leaflet)
library(sf)
library(dplyr)
library(RColorBrewer)
library(viridis)
library(DT)
library(tidyr) # Needed for unnest()

# ========================================
# LOAD PRE-PROCESSED DATA (ONCE AT STARTUP)
# ========================================

data <- read.csv("https://www.dropbox.com/scl/fi/8rfx48d8kpuyk13pgo0k2/adm3_multivariable.csv?rlkey=83srmi5d905ulljewuawoq8el&st=f3uxreii&dl=1")
data$high_temperature <- as.numeric(data$high_temperature)
data$low_temperature <- as.numeric(data$low_temperature)
data$average_temperature <- as.numeric(data$average_temperature)
data$total_evaporation_transpiration <- data$total_evaporation_transpiration * 100
data$total_precipitation <- data$total_precipitation * 100
shapes <- st_read("data/shapefiles/mwi_adm3_shp")

# ========================================
# PRE-CALCULATE PALETTES
# ========================================

high_temperature_palette <- colorNumeric(
  palette = "Spectral",
  domain = data$high_temperature,
  reverse = TRUE
)

avg_temperature_palette <- colorNumeric(
  palette = "Spectral",
  domain = data$average_temperature,
  reverse = TRUE
)

low_temperature_palette <- colorNumeric(
  palette = "Spectral",
  domain = data$low_temperature,
  reverse = TRUE
)

high_dewpoint_palette <- colorNumeric(
  palette = "PuOr",
  domain = data$high_dewpoint_temperature
)

avg_dewpoint_palette <- colorNumeric(
  palette = "PuOr",
  domain = data$average_dewpoint_temperature,
  reverse = TRUE
)

low_dewpoint_palette <- colorNumeric(
  palette = "PuOr",
  domain = data$low_dewpoint_temperature,
  reverse = TRUE
)

max_windspeed_palette <- colorNumeric(
  palette = "mako",
  domain = data$max_windspeed,
  reverse = TRUE
)

avg_windspeed_palette <- colorNumeric(
  palette = "mako",
  domain = data$average_windspeed,
  reverse = TRUE
)

min_windspeed_palette <- colorNumeric(
  palette = "mako",
  domain = data$min_windspeed,
  reverse = TRUE
)

max_soil_water_palette <- colorNumeric(
  palette = "RdYlBu",
  domain = data$max_soil_water
)

avg_soil_water_palette <- colorNumeric(
  palette = "RdYlBu",
  domain = data$average_soil_water
)

min_soil_water_palette <- colorNumeric(
  palette = "RdYlBu",
  domain = data$min_soil_water
)

# ========================================
# UI
# ========================================

ui <- page_sidebar(
  # App title 
  title = "Malawi Weather Visualization",
  sidebar = sidebar(
    dateInput(
      'date', 
      'Select a Date:', 
      min = '2020-01-01', 
      max = '2025-08-31'),
    selectInput(
      "var",
      label = "Choose a variable to display",
      choices = 
        list(
          "High Temperature",
          "Average Temperature",
          "Low Temperature",
          "High Dewpoint",
          "Average Dewpoint",
          "Low Dewpoint",
          "Maximum Windspeed",
          "Average Windspeed",
          "Minimum Windspeed",
          "Maximum Soil Moisture",
          "Average Soil Moisture",
          "Minimum Soil Moisture",
          "Total Precipitation",
          "Total Evaporation via Transpiration"
        ),
      selected = "High Temperature"
    )
  ),
  # Output: Map
  leafletOutput("leafletMap")
)

# ========================================
# SERVER
# ========================================

server <- function(input, output){
  
  output$leafletMap <- renderLeaflet({
    joined <- st_sf(inner_join(data[data$date == input$date,], shapes, by=c("adm3.id" = "ADM3_PCODE")))
    
    value <- switch(input$var,
                   "High Temperature" = joined$high_temperature,
                   "Low Temperature" = joined$low_temperature,
                   "Average Temperature" = joined$average_temperature,
                   "High Dewpoint" = joined$high_dewpoint_temperature,
                   "Average Dewpoint" = joined$average_dewpoint_temperature,
                   "Low Dewpoint" = joined$low_dewpoint_temperature,
                   "Maximum Windspeed" = joined$max_windspeed,
                   "Average Windspeed" = joined$average_windspeed,
                   "Minimum Windspeed" = joined$min_windspeed,
                   "Maximum Soil Moisture" = joined$max_soil_water,
                   "Average Soil Moisture" = joined$average_soil_water,
                   "Minimum Soil Moisture" = joined$min_soil_water,
                   "Total Precipitation" = joined$total_precipitation,
                   "Total Evaporation via Transpiration" = joined$total_evaporation_transpiration)
    
    if (input$var == "Total Precipitation"){
      precipitation_palette <- colorNumeric(
        palette = "mako",
        domain = value,
        reverse = TRUE)
    }
    if(input$var == "Total Evaporation via Transpiration"){
      evaporation_palette <- colorNumeric(
        palette = "mako",
        domain = value,
        reverse = TRUE)
    }
    
    pal <- switch(input$var,
                  "High Temperature" = high_temperature_palette,
                  "Average Temperature" = avg_temperature_palette,
                  "Low Temperature" = low_temperature_palette,
                  "High Dewpoint" = high_dewpoint_palette,
                  "Average Dewpoint" = avg_dewpoint_palette,
                  "Low Dewpoint" = low_dewpoint_palette,
                  "Maximum Windspeed" = max_windspeed_palette,
                  "Average Windspeed" = avg_windspeed_palette,
                  "Minimum Windspeed" = min_windspeed_palette,
                  "Maximum Soil Moisture" = max_soil_water_palette,
                  "Average Soil Moisture" = avg_soil_water_palette,
                  "Minimum Soil Moisture" = min_soil_water_palette,
                  "Total Precipitation" = precipitation_palette,
                  "Total Evaporation via Transpiration" = evaporation_palette)
    
    unit <- switch(input$var,
                   "High Temperature" = " (°C)",
                   "Average Temperature" = " (°C)",
                   "Low Temperature" = " (°C)",
                   "High Dewpoint" = " (°C)",
                   "Average Dewpoint" = " (°C)",
                   "Low Dewpoint" = " (°C)",
                   "Maximum Windspeed" = " (m/s)",
                   "Average Windspeed" = " (m/s)",
                   "Minimum Windspeed" = " (m/s)",
                   "Maximum Soil Moisture" = " (m³/m³)",
                   "Average Soil Moisture" = " (m³/m³)",
                   "Minimum Soil Moisture" = " (m³/m³)",
                   "Total Precipitation" = " (cm equivalent)",
                   "Total Evaporation via Transpiration" = " (cm equivalent)")
    leaflet(joined) %>%
      addTiles() %>%
      addPolygons(
        fillColor = ~pal(value),
        weight = 1,
        opacity = 1,
        color = "white",
        dashArray = "3",
        fillOpacity = 0.7,
        highlightOptions = highlightOptions(
          weight = 2,
          color = "#666",
          dashArray = "",
          fillOpacity = 0.7,
          bringToFront = TRUE
        ),
        popup = ~paste0(ADM3_EN, paste("<br/>", input$var, ": "), value)
      ) %>%
      addLegend(pal = pal, 
                values = ~value, 
                opacity = 0.7, 
                title = paste(input$var, 
                              "<br/>", 
                              unit, 
                              "<br/>", 
                              input$date), 
                position = "bottomright")
  })
}

shinyApp(ui = ui, server = server)
