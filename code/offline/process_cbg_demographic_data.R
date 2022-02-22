## This script is for exploring and processing the CBG ACS demographic data.

library(tidyverse)

## Exploratory 
df <- read.csv("/Users/jfossett/Documents/Research/nycoral/drafting/data_analysis_cbg/safegraph_open_census_data_2019/metadata/cbg_field_descriptions.csv")
df %>% select(table_title)
View(df %>% group_by(table_title) %>% summarise(n=n()) %>% arrange(desc(n)))

View(df %>% filter(table_title == 'Hispanic Or Latino Origin By Race'))
(df %>% filter(table_title == 'Ratio Of Income To Poverty Level In The Past 12 Months', field_level_1=='Estimate') %>% select(table_id, field_level_5))$field_level_5

## Final

# Poverty data 
colclasses <- c("character","integer","integer","integer","integer","integer","integer","integer","integer","integer","integer","integer","integer","integer","integer","integer","integer")
poverty_data <- read.csv("/Users/jfossett/Documents/Research/nycoral/drafting/data_analysis_cbg/safegraph_open_census_data_2019/data/cbg_c17.csv", colClasses = colclasses)
poverty_fields <- c("census_block_group", "C17002e1","C17002e2","C17002e3","C17002e4","C17002e5","C17002e6","C17002e7","C17002e8")
clean_names <- c("census_block_group","Poverty_total","Under .50",".50 to .99",  "1.00 to 1.24",  "1.25 to 1.49", "1.50 to 1.84", "1.85 to 1.99", "2.00 and over")
poverty_data <- poverty_data[,poverty_fields]
colnames(poverty_data) <- clean_names
poverty_data %>% write_csv(file="/Users/jfossett/Documents/Research/nycoral/clean/data/raw/acs_data/df_poverty_cbg.csv")


# Race data 
colclasses <- c("character", rep("integer", 32))
race_data <- read.csv("/Users/jfossett/Documents/Research/nycoral/drafting/data_analysis_cbg/safegraph_open_census_data_2019/data/cbg_b02.csv", colClasses = colclasses)
race_fields <- c("census_block_group", "B02001e1","B02001e2","B02001e3","B02001e4","B02001e5","B02001e6","B02001e7", "B02001e8")
clean_race_names <- c("census_block_group","Race_total","White alone","Black or African American alone",  "American Indian and Alaska Native alone",  "Asian alone", "Native Hawaiian and Other Pacific Islander alone", "Some other race alone", "Two or more races")
race_data <- race_data[,race_fields]
colnames(race_data) <- clean_race_names
race_data %>% write_csv(file="/Users/jfossett/Documents/Research/nycoral/clean/data/raw/acs_data/df_race_cbg.csv")


# Race data with ethnicity (Hispanic / non-Hispanic)
colclasses <- c("character", rep("integer", 48))
race_ethnicity_data <- read.csv("/Users/jfossett/Documents/Research/nycoral/drafting/data_analysis_cbg/safegraph_open_census_data_2019/data/cbg_b03.csv", colClasses = colclasses)
race_ethnicity_fields <- c("census_block_group", "B03002e1","B03002e3","B03002e4","B03002e5","B03002e6","B03002e7","B03002e8","B03002e9","B03002e12")
race_ethnicity_data <- race_ethnicity_data[,race_ethnicity_fields]
clean_race_ethnicity_names <- c("census_block_group", "Race Total", "White alone","Black or African American alone",  "American Indian and Alaska Native alone",  "Asian alone", "Native Hawaiian and Other Pacific Islander alone", "Some other race alone", "Two or more races", "Hispanic or Latino (Any Race)")
colnames(race_ethnicity_data) <- clean_race_ethnicity_names
race_ethnicity_data %>% write_csv(file="/Users/jfossett/Documents/Research/nycoral/clean/data/raw/acs_data/df_race_ethnicity_cbg.csv")






