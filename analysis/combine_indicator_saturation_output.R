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

#rm(list = ls())  #clear the workspace

#setwd("C:\\Users\\ajwalker\\Documents\\GitHub\\prescribing_change_metrics\\data\\testing") # for testing only
#setwd(arguments[1])

draw_change_detection_plot = function( plot_data,
                                       plot_title="Change detection plot",
                                       annotations = c( COVID = "2020-03-01" ) ) {
  
  cd = ggplot( plot_data,
               aes(group=code)) +
    annotate( "segment",
              x = annotations,
              xend=annotations,
              y = -Inf,
              yend = Inf,
              colour="green", size=1)+
    ### Plot the real data
    geom_line( data = plot_data %>% filter( set == "real" ),
               aes(x=x, y=y) ) +
    ### Plot the trend on top of that
    geom_line( data = plot_data %>% filter( set == "trend" ),
               aes(x=x, y=y),
               col="red") +
    ### Plot the start/end points
    # geom_rect( data=plot_data %>%
    #              filter( set == "startend" ) %>%
    #              arrange(y) %>%
    #              mutate( val = LETTERS[1:n()] ) %>%
    #              pivot_wider( names_from="val", values_from="y") %>%
    #              mutate( xmin=plot_data %>% pull(x) %>% min(na.rm=TRUE) - years(1), #as.POSIXct("2019-05-01"),
    #                      xmax=plot_data %>% pull(x) %>% max(na.rm=TRUE) + years(1) ),
    #            aes( ymin=A, ymax=B, xmin = xmin, xmax=xmax ),
    #            fill="purple",
    #            alpha=0.2) +
  
  geom_hline( data = plot_data %>% filter( set == "startend" ),
              aes(yintercept=y),
              col="purple", linetype="dashed", size=1) +
    ### Highlight the slope
    geom_line( data = plot_data %>% filter( set == "slope" ),
               aes(x=x, y=y),
               col=rgb(red = 1, green = 0.4118, blue = 0, alpha = 0.5),
               size=5,
               lineend = "round" ) +
    ### Plot the breaks
    geom_vline( data = plot_data %>% filter( set == "break" ),
                aes( xintercept = x ),
                col="blue", linetype = "dashed", size=1) +
    ### Plot the intervention of interest
    geom_vline( data = plot_data %>% filter( set == "intervention" ),
                aes( xintercept = x ),
                col="orange", linetype = "dashed", size=1) +
    ### Add any annotation of interest
    geom_vline( data = plot_data %>% filter( set == "annotation" ),
                aes( xintercept = x ),
                col="green", linetype = "dashed", size=1) 

  if ( nrow( plot_data %>% filter( set == "firstbreak" ) ) > 1 ) {
    cd = cd + geom_rect( data = plot_data %>% filter( set == "firstbreak" ),
                         aes( xmin = -Inf,
                              xmax = x,
                              ymin = -Inf,
                              ymax = Inf ), col="grey", alpha=0.3)
    
  }
  
  ### Remove space between data and axes
  #scale_x_continuous(expand = c(0, 0)) +
  #scale_y_continuous(expand = c(0, 0)) +
  ### Add new labels
  cd = cd +
    labs( title = glue( "{this_indicator} // {this_direction} // {this_object}" ),
                  x = "Time series months",
                  y = "Numerator over denominator" ) +
    # coord_cartesian( xlim = c(plot_data %>% pull(x) %>% min(na.rm=TRUE),
    #                           plot_data %>% pull(x) %>% max(na.rm=TRUE)) ) +
    theme_bw() +
    theme( axis.text.x = element_text( angle=90))
  
  # ggsave(glue("{fig_path_tis_analysis}/{this_indicator}_{this_direction}_{this_object}_NEW.png"),
  #        units = "mm",
  #        width = 270,
  #        height = 270 )
  
  return( cd )
  
}



time_since_epoch <- function(d) {
  x1 <- as.POSIXct(d)
  x2 <- format(x1, tz="GMT", usetz=F)
  x3 <- lubridate::ymd_hms(x2)
  epoch <- lubridate::ymd_hms('1970-01-01 00:00:00')
  time_since_epoch <- (x3 - epoch) / dseconds()
  return(time_since_epoch)
}


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
### STEP 1: READING IN THE ANALYSIS RESULTS
#####################################################################

results_files = data.frame(
  file_name = list.files(path=in_dir, pattern="summary_output.csv", recursive = TRUE )
) %>%
  mutate( file_name_full = paste( in_dir, file_name, sep="/" ) ) %>% 
  mutate( indicator = dirname( file_name ) ) %>% 
  mutate( direction = indicator %>% str_replace("indicator_saturation_", "") %>% str_replace( "_.*", "" )) %>% 
  mutate( indicator_string = indicator %>% str_replace( glue("indicator_saturation_{direction}_"), "" )) %>% 
  mutate( id = 1:n() )

results_holder = data.frame()

expand_list_from_character = function(c) {
  l = list(eval(parse(text=c)))
  return(l)
}

for ( results_i in 1:nrow( results_files ) ) {
  this_result_file = ( results_files %>% pull(file_name_full) )[results_i]
  this_indicator = ( results_files %>% pull(indicator_string) )[results_i]
  this_direction = ( results_files %>% pull(direction) )[results_i]
  
  these_results = read.csv( this_result_file ) %>% 
    mutate( indicator = this_indicator ) %>% 
    mutate( direction = this_direction ) %>% 
    ungroup() %>% 
    rowwise( ) %>%
    # mutate( breaks.loc.pos.l = expand_list_from_character(breaks.loc.pos)) %>% 
    # mutate( breaks.loc.neg.l = expand_list_from_character(breaks.loc.neg)) 
    mutate_at( vars(starts_with( "breaks." )), expand_list_from_character )
  
  results_holder = results_holder %>% 
    bind_rows( these_results )
}

#####################################################################
### STEP 2: READING IN THE PLOT INFORMATION
#####################################################################

plotdata_files = data.frame(
  file_name = list.files(path=in_dir, pattern="plot_data.csv$", recursive = TRUE )
) %>%
  mutate( file_name_full = paste( in_dir, file_name, sep="/" ) ) %>% 
  mutate( indicator = dirname( file_name ) ) %>% 
  mutate( direction = indicator %>% str_replace("indicator_saturation_", "") %>% str_replace( "_.*", "" )) %>% 
  mutate( indicator_string = indicator %>% str_replace( glue("indicator_saturation_{direction}_"), "" )) %>%
  mutate( id = 1:n() )

plotdata_holder = data.frame()

fig_path_tis_analysis = out_dir

###### Timing Measures
### ADD CHANGE OF GUIDANCE HERE
known.t      = 0  ### Time of known intervention in the sample, e.g. medication became available as generic at observation t=18
annotation.t = 0
break.t.lim  = .8 ### Proportion offset after negative break

###### Slope Measures
slope.lim <- 0.5   ### Proportion of slope drop for construction of slope measure

for ( results_i in 1:nrow( plotdata_files ) ) {
  
  this_result_file = ( plotdata_files %>% pull(file_name_full) )[results_i]
  this_indicator = ( plotdata_files %>% pull(indicator_string) )[results_i]
  this_direction = ( plotdata_files %>% pull(direction) )[results_i]
  this_object = basename( this_result_file )
  
  cat( glue("[{results_i}] Reading data from {this_indicator} // {this_direction} // {this_object}\n\n"))
  
  if ( file.info(this_result_file)$size > 0 ) {
  
  these_results = read.csv( this_result_file,
                            col.names = c( "y", "x", "set", "code")) %>%
    mutate( indicator = this_indicator ) %>% 
    mutate( direction = this_direction )
  
  plotdata_holder = plotdata_holder %>% 
    bind_rows( these_results )
  
  }

  # draw_change_detection_plot( these_results %>% filter( code == "ratio_quantity.34"))

}

date_mapping = plotdata_holder %>% pull( x ) %>% unique() %>% sort
COVID_start =  which(date_mapping=="2020-03-01") 

# save( results_holder,
#       plotdata_holder,
#       file = glue("{fig_path_tis_analysis}/ANALYSIS_OUTPUT.RData") )

#####################################################################
##################################################################### 
### Recording interesting counts ####################################
#####################################################################
##################################################################### 

# NB. we can select only "up" results here, as these breaks will
# be the same for up and down analyses.

### For each indicator, the proportion of practices with at least one
### break identified
proportion_of_practices_with_any_breaks = 
  results_holder %>%
  filter( direction == "up") %>% 
  group_by( indicator ) %>%
  summarise( count=sum(is.nbreak>0),
             total=n() ) %>% 
  mutate( proportion = count/total )
write.csv( proportion_of_practices_with_any_breaks,
           file=glue("{out_dir}/at-least-one_break.csv"))

### For each indicator, the proportion of practices with at least one
### positive break identified
proportion_of_practices_with_pos_breaks = 
  results_holder %>%
  filter( direction == "up") %>% 
  group_by( indicator ) %>%
  summarise( count=sum(!is.na(breaks.loc.pos)),
             total=n() ) %>% 
  mutate( proportion = count/total )
write.csv( proportion_of_practices_with_pos_breaks,
           file=glue("{out_dir}/at-least-one_pos-break.csv"))

### For each indicator, the proportion of practices with at least one
### negative break identified
proportion_of_practices_with_neg_breaks = 
  results_holder %>%
  filter( direction == "up") %>% 
  group_by( indicator ) %>%
  summarise( count=sum(!is.na(breaks.loc.neg)),
             total=n() ) %>% 
  mutate( proportion = count/total )
write.csv( proportion_of_practices_with_neg_breaks,
           file=glue("{out_dir}/at-least-one_neg-break.csv"))

### For each practice, how many positive and negative breaks

per_indicator_per_practice_pos_breaks = results_holder %>%
  filter( direction == "up" ) %>% 
  select( indicator, name, breaks.loc.pos ) %>% 
  unnest( cols = "breaks.loc.pos" ) %>% 
  filter( !is.na( breaks.loc.pos ) ) %>% 
  group_by( indicator, name ) %>% 
  summarise( pos_count = length(unique(breaks.loc.pos)) )

per_indicator_per_practice_neg_breaks = results_holder %>%
  filter( direction == "up" ) %>% 
  select( indicator, name, breaks.loc.neg ) %>% 
  unnest( cols = "breaks.loc.neg" ) %>% 
  filter( !is.na( breaks.loc.neg ) ) %>% 
  group_by( indicator, name ) %>% 
  summarise( neg_count = length(unique(breaks.loc.neg)) )

per_indicator_per_practice_breaks = per_indicator_per_practice_pos_breaks %>% 
  full_join( per_indicator_per_practice_neg_breaks,
             by=c( "indicator", "name" ) )

write.csv( per_indicator_per_practice_breaks,
           file=glue("{out_dir}/BREAK-COUNT_per_indicator_per_practice.csv"))

### For each indicator, the number of practices with a positive break at each timepoint

proportion_of_practices_with_postCOVID_pos_break = results_holder %>%
  filter( direction == "up" ) %>% 
  select( indicator, name, breaks.loc.pos ) %>% 
  unnest( cols = "breaks.loc.pos" ) %>% 
  filter( !is.na( breaks.loc.pos ) ) %>% 
  group_by( indicator, breaks.loc.pos ) %>% 
  summarise( n=n() ) %>%
  ungroup() %>% 
  complete( breaks.loc.pos, indicator, fill = list( n=0)) %>% 
  mutate( month = date_mapping[ breaks.loc.pos ] ) %>%
  select( indicator, breaks.loc.pos, month, n ) %>% 
  arrange( indicator, month )
  
write.csv( proportion_of_practices_with_postCOVID_pos_break,
           file=glue("{out_dir}/num-pos-break_permonth.csv"))

### For each indicator, the number of practices with a negative break at each timepoint

proportion_of_practices_with_postCOVID_neg_break = results_holder %>%
  filter( direction == "up" ) %>% 
  select( indicator, name, breaks.loc.neg ) %>% 
  unnest( cols = "breaks.loc.neg" ) %>% 
  filter( !is.na( breaks.loc.neg ) ) %>% 
  group_by( indicator, breaks.loc.neg ) %>% 
  summarise( n=n() ) %>%
  ungroup() %>% 
  complete( breaks.loc.neg, indicator, fill = list( n=0)) %>% 
  mutate( month = date_mapping[ breaks.loc.neg ] ) %>%
  select( indicator, breaks.loc.neg, month, n ) %>% 
  arrange( indicator, month )

write.csv( proportion_of_practices_with_postCOVID_neg_break,
           file=glue("{out_dir}/num-neg-break_permonth.csv"))

#####################################################################
##################################################################### 
### Recording interesting counts ####################################
#####################################################################
##################################################################### 


# results_toplot = results_holder %>% 
  # filter( is.nbreak > 0 )

# for ( plot_i in 1:nrow( results_toplot ) ) {
#   this_indicator = ( results_toplot %>% pull(indicator) )[plot_i]
#   this_direction = ( results_toplot %>% pull(direction) )[plot_i]
#   this_code      = ( results_toplot %>% pull(name)      )[plot_i]
#   
#   print( glue( "{this_indicator} in {this_code}\n" ) )
#   
#   this_d = plotdata_holder %>%
#     filter( code == this_code,
#             indicator == this_indicator,
#             direction == this_direction )
#   
#   this_graph_file = glue("{out_dir}/CDPLOT_{this_indicator}_{this_direction}_{this_code}_plot.png")
#   
#   ggsave( this_graph_file, plot=draw_change_detection_plot( this_d ) )
#   
# }
#   

#####################################################################
### Summary figure of slope intensity
#####################################################################

# ggplot( data = results_holder %>% filter( is.nbreak > 0 ) %>% filter( direction=="up"),
#         aes( x = indicator,
#              y = name,
#              z = is.slope.ma,
#              fill=is.slope.ma)) + geom_tile(col="black",size=0.5) +
#   # scale_fill_brewer(type="div")
#   scale_fill_distiller(palette = "PuOr") +
#   theme_minimal() +
#   theme( axis.text.x = element_text(angle=90,
#                                     hjust=1)) 
# 
# ggsave( glue("{fig_path_tis_analysis}/SUMMARY_up_heatmap.png"),
#         width = 6,
#         height = 6 )


# ggplot( data = results_holder %>% filter( is.nbreak > 0 ) %>% filter( direction=="down"),
#         aes( x = indicator,
#              y = name,
#              z = is.slope.ma,
#              fill=is.slope.ma)) + geom_tile(col="black",size=0.5) +
#   # scale_fill_brewer(type="div")
#   scale_fill_distiller(palette = "PuOr") +
#   theme_minimal() +
#   theme( axis.text.x = element_text(angle=90,
#                                     hjust=1)) 
# 
# ggsave( glue("{fig_path_tis_analysis}/SUMMARY_down_heatmap.png"),
#         width = 6,
#         height = 6 )

#####################################################################
### Draw all significant results
#####################################################################

# significant_results = results_holder %>% filter( is.nbreak > 0 ) %>% select( name, indicator, direction )

# significant_plot_data = plotdata_holder %>% 
#   inner_join( significant_results, by=c( "indicator", "name", "direction" ) ) %>% 
#   mutate( tag = glue("{indicator}_{name}") ) %>% 
#   group_by( indicator, name )

# draw_change_detection_plot( significant_plot_data ) +
#   theme( axis.text.x = element_text(angle=90,
#                                     hjust=1)) +
#   facet_wrap( ~tag, scales="free_y")

# ggsave( glue("{fig_path_tis_analysis}/SUMMARY_significant.png"),
#         width = 8,
#         height = 8 )


#####################################################################
### Draw all results
#####################################################################

# draw_change_detection_plot( plotdata_holder %>% group_by(indicator,name) ) +
#   facet_grid( name~indicator, scales="free_y") +
#   theme( axis.text.x = element_text(angle=90,
#                                     hjust=1)) 

# ggsave( glue("{fig_path_tis_analysis}/SUMMARY_all.png"),
#         width = 24,
#         height = 24 )

#####################################################################
### Draw all indicators for each practice
#####################################################################

# for ( n in plotdata_holder %>% pull(name) %>% unique) {
  
#   draw_change_detection_plot( plotdata_holder %>% 
#                                 filter( name == n ) %>% 
#                                 group_by( indicator) ) +
#     facet_wrap( ~indicator, scales="free_y" ) +
#     labs( title=glue("All indicators for [{n}]") ) +
#     theme( axis.text.x = element_text(angle=90,
#                                       hjust=1)) 
  
#   ggsave( glue("{fig_path_tis_analysis}/SUMMARY_PRACTICE-{n}.png"),
#           width = 8,
#           height = 8 )
# }

#####################################################################
### Draw all practices for each indicator
#####################################################################

# for ( ind in plotdata_holder %>% pull(indicator) %>% unique) {
  
#   draw_change_detection_plot( plotdata_holder %>% 
#                                 filter( indicator == ind ) %>% 
#                                 group_by( name ) ) +
#     facet_wrap( ~name, scales="free_y" ) +
#     labs( title=glue("All practices for [{ind}]") ) +
#     theme( axis.text.x = element_text(angle=90,
#                                       hjust=1)) 
  
#   ggsave( glue("{fig_path_tis_analysis}/SUMMARY_INDICATOR-{ind}.png"),
#           width = 8,
#           height = 8 )
# }



# write.csv(results, file = arguments[3])
print("Done extracting results")
