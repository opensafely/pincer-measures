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
### STEP 1: READING IN THE CUMULATIVE ANALYSIS OUTPUT AND GENERATING PLOTS
#####################################################################

pos_break_cumulative.in = read.csv( glue("{out_dir}/at-least-one_post-COVID_pos-break_cumulative.csv") )

pos_break_cumulative.d_tmp = pos_break_cumulative.in %>%
  select( -X )  %>% 
  mutate( month = ymd( month ) ) %>%

  ### Remove indicators with no counts at any time
  group_by( indicator ) %>% 
  mutate( nocounts = all( count == 0 ) )

removed_indicators = pos_break_cumulative.d_tmp %>%
  filter( nocounts ) %>% 
  pull( indicator ) %>% unique

pos_break_cumulative.d = pos_break_cumulative.d_tmp %>% 
  filter( !nocounts ) %>% 
  select( -nocounts )
  
xbreaks = seq( pos_break_cumulative.d %>% pull(month) %>% min(na.rm=TRUE),
               pos_break_cumulative.d %>% pull(month) %>% max(na.rm=TRUE),
               by='1 month' )

### As line plot
ggplot( data = pos_break_cumulative.d,
        aes( x = month,
             y = count,
             group = indicator,
             col = indicator ) ) +
  geom_point() + 
  geom_line() +
  scale_x_date( date_labels = "%b %y", breaks = xbreaks ) +
  labs( title= "Count of positive breaks (cumulative since COVID)",
        subtitle = glue("{length(removed_indicators)} indicators \\
                        ({paste(removed_indicators,collapse=',')}) removed due to no counts" ),
        x = "Months relative to start of COVID (03/20)",
        y = "Number of practices with positive break identified in this month" ) +
  theme_bw() +
  facet_wrap( ~indicator ) +
  theme( axis.text.x = element_text(angle=90, hjust = 1, vjust=0.5))

ggsave(  glue("{out_dir}/BREAK-COUNT_POS_line-cumulative.png") )

### As histogram
ggplot( data = pos_break_cumulative.d,
        aes( x = month,
             y = count,
             group = indicator,
             fill = indicator,
             col = indicator ) ) +
  geom_bar( stat="identity") + 
  scale_x_date( date_labels = "%b %y", breaks = xbreaks ) +
  labs( title= "Count of positive breaks (cumulative since COVID)",
        subtitle = glue("{length(removed_indicators)} indicators \\
                        ({paste(removed_indicators,collapse=',')}) removed due to no counts" ),
        x = "Months relative to 03/20",
        y = "Number of practices with positive break identified in this month" ) +
  theme_bw() +
  facet_wrap( ~indicator ) +
  theme( axis.text.x = element_text(angle=90, hjust = 1, vjust=0.5))

ggsave(  glue("{out_dir}/BREAK-COUNT_POS_histogram-cumulative.png") )

### As stacked bar chart
ggplot( data = pos_break_cumulative.d,
        aes( x = month,
             y = count,
             group = indicator,
             fill = indicator,
             col = indicator ) ) +
  geom_bar(  stat="identity" ) + 
  scale_x_date( date_labels = "%b %y", breaks = xbreaks ) +
  labs( title= "Count of positive breaks (cumulative since COVID)",
        subtitle = glue("{length(removed_indicators)} indicators \\
                        ({paste(removed_indicators,collapse=',')}) removed due to no counts" ),
        x = "Months relative to 03/20",
        y = "Number of practices with positive break identified" ) +
  theme_bw() +
  theme( axis.text.x = element_text(angle=90, hjust = 1, vjust=0.5))

ggsave( glue("{out_dir}/BREAK-COUNT_POS_stacked-histogram-cumulative.png") )

# ### As ribbon chart
# ggplot( data = pos_break_cumulative.d,
#         aes( x = timenum,
#              y = count,
#              fill = indicator) ) +
#   geom_stream( type="ridge", colour="black" ) +
#   scale_x_continuous( breaks = xbreaks) +
#   labs( title= "Count of positive breaks per month",
#         subtitle = glue("{length(removed_indicators)} indicators \\
#                         ({paste(removed_indicators,collapse=',')}) removed due to no counts" ),
#         x = "Months relative to 03/20",
#         y = "Number of positive breaks identified in this month" ) +
#   theme_bw()
# 
# ggsave(  glue("{out_dir}/BREAK-COUNT_ribbon.png") )


#####################################################################
### STEP 2: READING IN THE PER MONTH OUTPUT AND GENERATING PLOTS
#####################################################################

###
### Negative breaks
###

pos_break_permonth.in = read.csv( glue("{out_dir}/num-pos-break_permonth.csv") )

pos_break_permonth.d = pos_break_permonth.in %>%
  select( -X ) %>% 
  filter( ! indicator %in% removed_indicators ) %>% 
  mutate( month = ymd( month ) )

xbreaks = seq( pos_break_permonth.d %>% pull(month) %>% min(na.rm=TRUE),
               pos_break_permonth.d %>% pull(month) %>% max(na.rm=TRUE),
               by='1 month' )

ggplot( data = pos_break_permonth.d,
        aes( x = month,
             y = count,
             group = indicator ) ) +
  geom_vline( xintercept = ymd("2020-03-01"),
              colour="orange",
              linetype="dashed") +
  geom_point( colour = colour_scheme["pos"] ) + 
  geom_line( colour = colour_scheme["pos"] ) +
  scale_x_date( date_labels = "%b %y", breaks = xbreaks ) +
  labs( title= "Count of positive breaks per month (from the index date)",
        subtitle = glue("{length(removed_indicators)} indicators \\
                        ({paste(removed_indicators,collapse=',')}) removed due to no counts" ),
        x = "Months relative to index date",
        y = "Number of practices with positive break identified in this month" ) +
  theme_bw() +
  theme( axis.text.x = element_text(angle=90, hjust = 1, vjust=0.5)) +
  facet_wrap( ~indicator )

ggsave(  glue("{out_dir}/BREAK-COUNT_POS_line-permonth.png") )

###
### Negative breaks
###

neg_break_permonth.in = read.csv( glue("{out_dir}/num-neg-break_permonth.csv") )

neg_break_permonth.d = neg_break_permonth.in %>% 
  select( -X ) %>% 
  filter( ! indicator %in% removed_indicators ) %>% 
  mutate( month = ymd( month ) ) 

xbreaks = seq( neg_break_permonth.d %>% pull(month) %>% min(na.rm=TRUE),
               neg_break_permonth.d %>% pull(month) %>% max(na.rm=TRUE),
               by='1 month' )

### As line plot
ggplot( data = neg_break_permonth.d,
        aes( x = month,
             y = count,
             group = indicator ) ) +
  geom_vline( xintercept = ymd("2020-03-01"),
              colour="orange",
              linetype="dashed") +
  geom_point( colour = colour_scheme["neg"] ) + 
  geom_line( colour = colour_scheme["neg"] ) +
  scale_x_date( date_labels = "%b %y", breaks = xbreaks ) +
  labs( title= "Count of negitive breaks per month (from the index date)",
        subtitle = glue("{length(removed_indicators)} indicators \\
                        ({paste(removed_indicators,collapse=',')}) removed due to no counts" ),
        x = "Months relative to index date",
        y = "Number of practices with negative break identified in this month" ) +
  theme_bw() +
  theme( axis.text.x = element_text(angle=90, hjust = 1, vjust=0.5)) +
  facet_wrap( ~indicator )

ggsave(  glue("{out_dir}/BREAK-COUNT_NEG_line-permonth.png") )

###
### Combined plot
### 

both_break_permonth.d = pos_break_permonth.d %>%
  select( indicator, count, month ) %>% 
  rename( pos = count ) %>% 
  inner_join( neg_break_permonth.d %>% select( indicator, count, month ),
              by=c("indicator","month")) %>% 
  rename( neg = count ) %>% 
  pivot_longer( c(pos, neg),
                names_to = "direction",
                values_to = "count" )

ggplot( data = both_break_permonth.d,
        aes( x = month,
             y = count,
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
        subtitle = glue("{length(removed_indicators)} indicators \\
                        ({paste(removed_indicators,collapse=',')}) removed due to no counts" ),
        x = "Months relative to index date",
        y = "Number of practices with breaks identified in this month" ) +
  theme_bw( ) +
  theme( axis.text.x = element_text(angle=90, hjust = 1, vjust=0.5)) +
  facet_wrap( ~indicator )

ggsave(  glue("{out_dir}/BREAK-COUNT_BOTH_line-permonth.png") )



