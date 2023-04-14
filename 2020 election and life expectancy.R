library(dplyr)
library(tidyr)

election_data <- read.csv("https://raw.githubusercontent.com/nickmmark/life-expectancy/main/election%20results/president_county_candidate.csv")

vote_counts <- election_data %>%
  filter(candidate %in% c("Joe Biden", "Donald Trump")) %>%
  select(county, state, candidate, total_votes) %>%
  pivot_wider(names_from = candidate, values_from = total_votes) %>%
  mutate(county = str_to_title(county),
         state = str_to_title(state))

vote_counts$winner <- ifelse(vote_counts$`Joe Biden` > vote_counts$`Donald Trump`, "Joe Biden", "Donald Trump")

head(vote_counts)

cdc_data <- read.csv("https://data.cdc.gov/api/views/5h56-n989/rows.csv?accessType=DOWNLOAD&bom=true&format=true")

head(cdc_data)

# Select the necessary columns and rename them
cdc_data <- cdc_data %>%
  select(County, State) %>%
  rename(county = County, state = State`)

# Capitalize the first letter of each word in the county and state names
cdc_data$county <- str_to_title(cdc_data$county)
cdc_data$state <- str_to_title(cdc_data$state)

merged_data <- merge(vote_counts, cdc_data, by = "County")

head(merged_data)
