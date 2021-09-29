library(caTools)
library(gets) ### main package for break detection - see Pretis, Reade, and Sucarrat, Journal of Stat. Software, in press.
library(dplyr)
library(magrittr)
library(glue)
library(tidyr)
library(ggplot2)
library(lubridate)
library(readr)
library(stringr)
library(RColorBrewer)
# library(ggstream)

##### Retrive arguments from Python command
arguments <- commandArgs(trailingOnly = TRUE)

### For testing
# arguments[1] = "output/indicator_saturation"
# arguments[2] = "output/indicator_saturation/combined"

colour_scheme = vector()
colour_scheme["pos"] = brewer.pal(3,"Set1")[1]
colour_scheme["neg"] = brewer.pal(3,"Set1")[2]

###################################################################
#######################################
########### B: Extract Trend-Break Results
#######################################
####################################################################

in_dir = arguments[1]
out_dir = arguments[2]

if ( !dir.exists(out_dir ) ) {
  cat(sprintf("Making this directory: %s", out_dir))
  dir.create(out_dir, showWarnings = FALSE)
}

# in_dir = "/Users/lisahopcroft/Work/Projects/PINCER/pincer-measures/output/indicator_saturation"
# intervention_moment
#intervention_moment = "2019-10-15"
#known.t = time_since_epoch( intervention_moment )
#annotation.t = 10


#####################################################################
### READING IN THE PER MONTH OUTPUT AND GENERATING PLOTS
#####################################################################

###
### Negative breaks
###

pos_break_permonth.in = read.csv( glue("{out_dir}/num-pos-break_permonth.csv") )

pos_break_permonth.d = pos_break_permonth.in %>%
  select( -X ) %>% 
  mutate( month = ymd( month ) )

xbreaks = seq( pos_break_permonth.d %>% pull(month) %>% min(na.rm=TRUE),
               pos_break_permonth.d %>% pull(month) %>% max(na.rm=TRUE),
               by='1 month' )

ggplot( data = pos_break_permonth.d,
        aes( x = month,
             y = n,
             group = indicator ) ) +
  geom_vline( xintercept = ymd("2020-03-01"),
              colour="orange",
              linetype="dashed") +
  geom_point( colour = colour_scheme["pos"] ) + 
  geom_line( colour = colour_scheme["pos"] ) +
  scale_x_date( date_labels = "%b %y", breaks = xbreaks ) +
  labs( title= "Count of positive breaks per month (from the index date)",
        x = "Months relative to index date",
        y = "Number of practices with positive break identified in this month" ) +
  theme_bw() +
  theme( axis.text.x = element_text(angle=90, hjust = 1, vjust=0.5)) +
  facet_wrap( ~indicator )

ggsave(glue("{out_dir}/BREAK-COUNT_POS_line-permonth.png"), width = 12, height = 6)

###
### Negative breaks
###

neg_break_permonth.in = read.csv( glue("{out_dir}/num-neg-break_permonth.csv") )

neg_break_permonth.d = neg_break_permonth.in %>% 
  select( -X ) %>% 
  mutate( month = ymd( month ) ) 

xbreaks = seq( neg_break_permonth.d %>% pull(month) %>% min(na.rm=TRUE),
               neg_break_permonth.d %>% pull(month) %>% max(na.rm=TRUE),
               by='1 month' )

### As line plot
ggplot( data = neg_break_permonth.d,
        aes( x = month,
             y = n,
             group = indicator ) ) +
  geom_vline( xintercept = ymd("2020-03-01"),
              colour="orange",
              linetype="dashed") +
  geom_point( colour = colour_scheme["neg"] ) + 
  geom_line( colour = colour_scheme["neg"] ) +
  scale_x_date( date_labels = "%b %y", breaks = xbreaks ) +
  labs( title= "Count of negitive breaks per month (from the index date)",
        x = "Months relative to index date",
        y = "Number of practices with negative break identified in this month" ) +
  theme_bw() +
  theme( axis.text.x = element_text(angle=90, hjust = 1, vjust=0.5)) +
  facet_wrap( ~indicator )

ggsave(glue("{out_dir}/BREAK-COUNT_NEG_line-permonth.png"), width = 12, height = 6)

###
### Combined plot
### 

both_break_permonth.d = pos_break_permonth.d %>%
  select( indicator, n, month ) %>% 
  rename( pos = n ) %>% 
  inner_join( neg_break_permonth.d %>% select( indicator, n, month ),
              by=c("indicator","month")) %>% 
  rename( neg = n ) %>% 
  pivot_longer( c(pos, neg),
                names_to = "direction",
                values_to = "n" )

ggplot( data = both_break_permonth.d,
        aes( x = month,
             y = n,
             group = direction,
             col = direction ) ) +
  geom_vline( xintercept = ymd("2020-03-01"),
              colour="orange",
              linetype="dashed") +
  geom_point() + 
  geom_line() +
  scale_x_date( date_labels = "%b %y", breaks = xbreaks ) +
  scale_colour_manual( values=colour_scheme ) +
  labs( title= "Count of negitive breaks per month (from the index date)",
        x = "Months relative to index date",
        y = "Number of practices with breaks identified in this month" ) +
  theme_bw( ) +
  theme( axis.text.x = element_text(angle=90, hjust = 1, vjust=0.5)) +
  facet_wrap( ~indicator )

ggsave(glue("{out_dir}/BREAK-COUNT_BOTH_line-permonth.png"), width = 12, height = 6)



