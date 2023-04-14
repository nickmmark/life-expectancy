# Load necessary packages
library(tidyverse)
library(sf)
library(tmap)

# Import county data
counties <- st_read("https://opendata.arcgis.com/datasets/21843acfc7214984b9b4d4b42d4414b9_0.geojson")

# Import life expectancy data
life_expectancy <- read.csv("https://data.cdc.gov/api/views/5h56-n989/rows.csv?accessType=DOWNLOAD&bom=true&format=true")

# Filter data to only include the last 5 years
life_expectancy <- life_expectancy %>%
  filter(Year >= 2016)

# Compute the average life expectancy for each county over the last 5 years
life_expectancy_county <- life_expectancy %>%
  group_by(County, State) %>%
  summarize(avg_life_expectancy = mean(Life.Expectancy, na.rm = TRUE)) %>%
  ungroup()

# Join life expectancy data to county data
counties <- counties %>%
  left_join(life_expectancy_county, by = c("NAME" = "County", "STATE_NAME" = "State"))

# Create a color palette
palette <- colorNumeric(palette = "Reds", domain = counties$avg_life_expectancy)

# Plot the map
tm_shape(counties) +
  tm_fill(col = "avg_life_expectancy", palette = palette, title = "Average Life Expectancy") +
  tm_borders() +
  tm_layout(main.title = "Change in Life Expectancy over the last 5 years")

