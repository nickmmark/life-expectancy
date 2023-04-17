## 2020 presidential election results by county

# Load required packages
library(dplyr)

# Load election data
election_data <- read.csv("https://raw.githubusercontent.com/nickmmark/life-expectancy/main/election%20results/president_county_candidate.csv")

# Summarize the data by county and candidate, getting the total votes
county_results <- election_data %>% 
  group_by(county, candidate) %>% 
  summarize(total_votes = sum(total_votes)) %>% 
  ungroup()

# Get the winner by county
county_winners <- county_results %>% 
  group_by(county) %>% 
  slice_max(total_votes) %>% 
  ungroup()

# Print the results
head(county_winners)


## life expectancy by county

# Load required packages
library(dplyr)

# Load life expectancy data
life_expectancy_data <- read.csv("https://data.cdc.gov/api/views/5h56-n989/rows.csv?accessType=DOWNLOAD&bom=true&format=true")

# Clean the data and extract life expectancy by county
life_expectancy <- life_expectancy_data %>% 
  select(State, County, `Life.Expectancy`) %>% 
  rename(county = County, state = State, life_expectancy = `Life.Expectancy`) %>% 
  mutate(county = tolower(county)) %>% 
  mutate(state = gsub(",", "", state)) %>% 
  mutate(state = gsub(" ", "", state)) %>% 
  mutate(state = gsub("'", "", state)) %>% 
  mutate(fips = ifelse(nchar(state) == 1, paste0("0", state), state)) %>% 
  mutate(county = gsub(", [A-Z]{2}$", "", county)) %>% 
  mutate(fips = paste0(fips, county)) %>% 
  select(county, fips, life_expectancy)

# Get the average life expectancy by county
county_life_expectancy <- life_expectancy %>% 
  group_by(county, fips) %>% 
  summarize(avg_life_expectancy = mean(life_expectancy)) %>% 
  mutate(county = gsub(",.*", "", county))
  ungroup()

# Remove rows with NA in avg_life_expectancy
county_life_expectancy <- county_life_expectancy[!is.na(county_life_expectancy$avg_life_expectancy),]

# Merge county life expectancy with election data
election_life_expectancy <- left_join(county_winners, county_life_expectancy, by = c("county" = "county"))

# Print the results
head(election_life_expectancy)

