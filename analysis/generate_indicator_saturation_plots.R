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
# library(ggstream)

##### Retrive arguments from Python command
arguments <- commandArgs(trailingOnly = TRUE)

### For testing
# arguments[1] = "output/indicator_saturation"
# arguments[2] = "output/indicator_saturation/combined"

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

pos_break_cumulative.d_tmp = pos_break_cumulative.in[,c(-1)] %>% 
  pivot_longer( starts_with( "plus"),
                names_to = "timetext",
                values_to = "count" ) %>% 
  mutate( timenum = str_remove( timetext, ".*_" ) %>% str_remove( "mo" ) %>% as.integer ) %>% 
  
  ### Remove indicators with no counts at any time
  group_by( indicator ) %>% 
  mutate( nocounts = all( count == 0 ) )

removed_indicators = pos_break_cumulative.d_tmp %>%
  filter( nocounts ) %>% 
  pull( indicator ) %>% unique

pos_break_cumulative.d = pos_break_cumulative.d_tmp %>% 
  filter( !nocounts ) %>% 
  select( -nocounts )
  
xbreaks = seq( pos_break_cumulative.d %>% pull(timenum) %>% min(na.rm=TRUE),
               pos_break_cumulative.d %>% pull(timenum) %>% max(na.rm=TRUE),
               by=1)

### As line plot
ggplot( data = pos_break_cumulative.d,
        aes( x = timenum,
             y = count,
             group = indicator,
             col = indicator ) ) +
  geom_point() + 
  geom_line() +
  scale_x_continuous( breaks = xbreaks) +
  labs( title= "Count of positive breaks per month (since COVID)",
        subtitle = glue("{length(removed_indicators)} indicators \\
                        ({paste(removed_indicators,collapse=',')}) removed due to no counts" ),
        x = "Months relative to 03/20",
        y = "Number of positive breaks identified in this month" ) +
  theme_bw() +
  facet_wrap( ~indicator ) +
  theme( axis.text.x = element_text(angle=90, hjust = 1))

ggsave(  glue("{out_dir}/BREAK-COUNT_line-cumulative.png") )

### As histogram
ggplot( data = pos_break_cumulative.d,
        aes( x = timenum,
             y = count,
             group = indicator,
             fill = indicator,
             col = indicator ) ) +
  geom_bar( stat="identity") + 
  scale_x_continuous( breaks = xbreaks) +
  labs( title= "Count of positive breaks per month (since COVID)",
        subtitle = glue("{length(removed_indicators)} indicators \\
                        ({paste(removed_indicators,collapse=',')}) removed due to no counts" ),
        x = "Months relative to 03/20",
        y = "Number of positive breaks identified in this month" ) +
  theme_bw() +
  facet_wrap( ~indicator ) +
  theme( axis.text.x = element_text(angle=90, hjust = 1))

ggsave(  glue("{out_dir}/BREAK-COUNT_histogram-cumulative.png") )

### As stacked bar chart
ggplot( data = pos_break_cumulative.d,
        aes( x = timenum,
             y = count,
             group = indicator,
             fill = indicator,
             col = indicator ) ) +
  geom_bar(  stat="identity" ) + 
  scale_x_continuous( breaks = xbreaks) +
  labs( title= "Count of positive breaks per month (since COVID)",
        subtitle = glue("{length(removed_indicators)} indicators \\
                        ({paste(removed_indicators,collapse=',')}) removed due to no counts" ),
        x = "Months relative to 03/20",
        y = "Number of positive breaks identified in this month" ) +
  theme_bw() 

ggsave( glue("{out_dir}/BREAK-COUNT_stacked-histogram-cumulative.png") )

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
### STEP 2: READING IN THE CUMULATIVE ANALYSIS OUTPUT AND GENERATING PLOTS
#####################################################################

pos_break_permonth.in = read.csv( glue("{out_dir}/num-pos-break_permonth.csv") )

pos_break_permonth.d = pos_break_permonth.in[,c(-1)] %>% 
  pivot_longer( starts_with( "mo"),
                names_to = "timetext",
                values_to = "count" ) %>% 
  mutate( timenum = str_remove( timetext, "mo0?" ) %>% as.integer ) %>% 
  mutate( count = replace_na( count, 0 ) ) %>% 
  filter( ! indicator %in% removed_indicators ) 

xbreaks = seq( pos_break_permonth.d %>% pull(timenum) %>% min(na.rm=TRUE),
               pos_break_permonth.d %>% pull(timenum) %>% max(na.rm=TRUE),
               by=1 )

### As line plot
ggplot( data = pos_break_permonth.d,
        aes( x = timenum,
             y = count,
             group = indicator,
             col = indicator ) ) +
  geom_point() + 
  geom_line() +
  scale_x_continuous( breaks = xbreaks) +
  labs( title= "Count of positive breaks per month (from the index date)",
        subtitle = glue("{length(removed_indicators)} indicators \\
                        ({paste(removed_indicators,collapse=',')}) removed due to no counts" ),
        x = "Months relative to 03/20",
        y = "Number of positive breaks identified in this month" ) +
  theme_bw() +
  theme( axis.text.x = element_text(angle=90, hjust = 1)) +
  facet_wrap( ~indicator )

ggsave(  glue("{out_dir}/BREAK-COUNT_line-permonth.png") )

