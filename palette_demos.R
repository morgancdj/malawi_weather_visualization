library(colorspace)
library(patchwork)
library(leaflet)

data <- read.csv("https://www.dropbox.com/scl/fi/8rfx48d8kpuyk13pgo0k2/adm3_multivariable.csv?rlkey=83srmi5d905ulljewuawoq8el&st=f3uxreii&dl=1")
data$high_temperature <- as.numeric(data$high_temperature)
data$low_temperature <- as.numeric(data$low_temperature)
data$average_temperature <- as.numeric(data$average_temperature)
data$total_evaporation_transpiration <- data$total_evaporation_transpiration * 100
data$total_precipitation <- data$total_precipitation * 100

avg_temperature_palette <- colorNumeric(
  palette = "Spectral",
  domain = data$average_temperature,
  reverse = TRUE
)

avg_dewpoint_palette <- colorNumeric(
  palette = "PuOr",
  domain = data$average_dewpoint_temperature,
  reverse = TRUE
)

avg_windspeed_palette <- colorNumeric(
  palette = "mako",
  domain = data$average_windspeed,
  reverse = TRUE
)

avg_soil_water_palette <- colorNumeric(
  palette = "RdYlBu",
  domain = data$average_soil_water
)

tempseq <- seq(min(data$average_temperature), max(data$average_temperature), length.out = 30)
temp_hex_list <- avg_temperature_palette(tempseq)
specplot(temp_hex_list, type = "o", main = "Temperature Palette")
temp_pal <- recordPlot()

dewseq <- seq(min(data$average_dewpoint_temperature), max(data$average_dewpoint_temperature), length.out = 30)
dew_hex_list <- avg_dewpoint_palette(dewseq)
specplot(dew_hex_list, type = "o", main = "Dewpoint Palette")
dew_pal <- recordPlot()

windseq <- seq(min(data$average_windspeed), max(data$average_windspeed), length.out = 30)
wind_hex_list <- avg_windspeed_palette(windseq)
specplot(wind_hex_list, type = "o", main = "Windspeed, Evaportion & Precipitation Palette")
wind_pal <- recordPlot()

soilseq <- seq(min(data$average_soil_water), max(data$average_soil_water), length.out = 30)
soil_hex_list <- avg_soil_water_palette(soilseq)
specplot(soil_hex_list, type = "o", main = "Volumetric Soil Moisture Palette")
