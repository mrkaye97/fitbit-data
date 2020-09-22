library(tidyverse)
library(dbplyr)
library(lubridate)
library(scales)
library(ggthemes)
library(RPostgres)
library(forecast)
library(viridis)
library(patchwork)

rm(list = ls())

con <- DBI::dbConnect(RPostgres::Postgres(),    
                      host = "localhost",   
                      dbname = "fitbit",   
                      user = "matt")

df <- tbl(con, 'basicactivity') %>%
  arrange(date) %>%
  collect() %>%
  mutate(across(c(sedentaryMinutes, fairlyActiveMinutes, veryActiveMinutes), as.numeric)) %>%
  select(date, sedentaryMinutes, fairlyActiveMinutes, veryActiveMinutes) %>%
  pivot_longer(cols = -c(date)) %>%
  group_by(date) %>%
  mutate(prop = value / sum(value)) %>%
  ungroup()


p1 <- df %>%
  mutate(name = case_when(name == 'sedentaryMinutes' ~ 'Sedentary',
                              name == 'veryActiveMinutes' ~ 'Very Active',
                              name == 'fairlyActiveMinutes' ~ 'Fairly Active'),
         Activity = fct_reorder(name, desc(value))) %>%
  filter(Activity != 'Sedentary') %>%
  ggplot(aes(x = date, y = prop, fill = Activity, color = Activity))+
  geom_bar(stat = 'identity')+
  theme_fivethirtyeight()+
  scale_color_manual(values = c('coral', 'dodgerblue'))+
  scale_fill_manual(values = c('coral', 'dodgerblue'))+
  theme(legend.position = 'none')

p2 <- df %>%
  group_by(name) %>%
  mutate(name = case_when(name == 'sedentaryMinutes' ~ 'Sedentary',
                          name == 'veryActiveMinutes' ~ 'Very Active',
                          name == 'fairlyActiveMinutes' ~ 'Fairly Active'),
         Activity = fct_reorder(name, desc(value)),
         valuema = ma(value, 7), #create moving averages
  ) %>%
  ungroup() %>%
  filter(Activity != 'Sedentary') %>%
  ggplot(aes(x = date, color = Activity))+
  geom_line(aes(y = valuema))+
  theme_fivethirtyeight()+
  scale_color_manual(values = c('dodgerblue', 'coral'))


plt <- p1 / p2


ggsave('activityplot.svg', plt, 'svg', dpi = 'retina', path = '~/Google Drive/GitHub/fitbit-data/viz', width = 6, height = 4.8)
