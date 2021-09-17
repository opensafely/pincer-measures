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

###################################################################
#######################################
########### B: Extract Trend-Break Results
#######################################
####################################################################

#rm(list = ls())  #clear the workspace

#setwd("C:\\Users\\ajwalker\\Documents\\GitHub\\prescribing_change_metrics\\data\\testing") # for testing only
#setwd(arguments[1])

draw_change_detection_plot = function( pd,
                                       plot_title="Change detection plot" ) {
  cd_plot = ggplot( pd ) +
    ### Plot the real data
    geom_line( data = pd %>% filter( set == "real" ),
               aes(x=x, y=y)) +
    ### Plot the trend on top of that
    geom_line( data = pd %>% filter( set == "trend" ),
               aes(x=x, y=y),
               col="red") +
    ### Plot the start/end points
    geom_rect( data=pd %>%
                 filter( set == "startend" ) %>%
                 arrange(y) %>%
                 mutate( val = LETTERS[1:n()] ) %>%
                 pivot_wider( names_from="val", values_from="y") %>% 
                 mutate( xmin=plot_data %>% pull(x) %>% min(na.rm=TRUE) - years(1), #as.POSIXct("2019-05-01"),
                         xmax=plot_data %>% pull(x) %>% max(na.rm=TRUE) + years(1) ),
               aes( ymin=A, ymax=B, xmin = xmin, xmax=xmax ),
               fill="purple",
               alpha=0.2) +
    geom_hline( data = pd %>% filter( set == "startend" ),
                aes(yintercept=y),
                col="purple", linetype="dashed", size=1) +
    ### Highlight the slope
    geom_line( data = pd %>% filter( set == "slope" ),
               aes(x=x, y=y),
               col=rgb(red = 1, green = 0.4118, blue = 0, alpha = 0.5),
               size=5,
               lineend = "round" ) +
    ### Plot the breaks
    geom_vline( data = pd %>% filter( set == "break" ),
                aes( xintercept = x ),
                col="blue", linetype = "dashed", size=1) +
    ### Plot the intervention of interest
    geom_vline( data = pd %>% filter( set == "intervention" ),
                aes( xintercept = x ),
                col="orange", linetype = "dashed", size=1) +
    ### Add any annotation of interest
    geom_vline( data = pd %>% filter( set == "annotation" ),
                aes( xintercept = x ),
                col="green", linetype = "dashed", size=1) +
    ### Remove space between data and axes
    #scale_x_continuous(expand = c(0, 0)) +
    #scale_y_continuous(expand = c(0, 0)) +
    ### Add new labels
    labs( title = plot_title,
          x = "Time series months",
          y = "Numerator over denominator" ) +
    coord_cartesian( xlim = c( pd %>% pull(x) %>% min(na.rm=TRUE),
                               pd %>% pull(x) %>% max(na.rm=TRUE)) ) +
    theme_bw()

  return( cd_plot )
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
  file_name = list.files(path=in_dir, pattern="r_output_.*.csv", recursive = TRUE )
) %>%
  mutate( file_name_full = paste( in_dir, file_name, sep="/" ) ) %>% 
  mutate( indicator = dirname( file_name ) ) %>% 
  mutate( id = 1:n() )

results_holder = data.frame()

for ( results_i in 1:nrow( results_files ) ) {
  this_result_file = ( results_files %>% pull(file_name_full) )[results_i]
  this_indicator = ( results_files %>% pull(indicator) )[results_i]
  
  these_results = read.csv( this_result_file,
                            row.names = 1) %>% 
    mutate( indicator = this_indicator )
  
  results_holder = results_holder %>% 
    bind_rows( these_results )
}

#####################################################################
### STEP 2: READING IN THE PLOT INFORMATION
#####################################################################

plotdata_files = data.frame(
  file_name = list.files(path=in_dir, pattern=".*_plotdata.RData", recursive = TRUE )
) %>%
  mutate( file_name_full = paste( in_dir, file_name, sep="/" ) ) %>% 
  mutate( indicator = dirname( file_name ) ) %>% 
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
  this_indicator = ( plotdata_files %>% pull(indicator) )[results_i]
  this_object = basename( this_result_file ) %>% str_remove( "_plotdata.RData" )
  
  cat( glue("[{results_i}] Reading data from {this_indicator} // {this_object}\n\n"))
  
  load( this_result_file )
  
  model_months = data.pick$month.c
  y            = data.pick[this_object]
  
  
  ### Construct the plot data
  real_data = data.frame(
    y=islstr.res$aux$y ) %>%
    mutate( y = ifelse( y==99, NA, y) ) %>% 
    mutate( x = model_months ) %>% 
    mutate( set = "real" )
  
  trend_data = data.frame(
    y = tis.path$indic.fit$indic.fit+islstr.res$coefficients[islstr.res$specific.spec["mconst"]]
  ) %>% 
    mutate( x = model_months ) %>% 
    mutate( set="trend" )
  
  startend_data = data.frame()
  slope_data = data.frame()
  break_data = data.frame()
  
  if ( nbreak > 0 ) {
    startend_data = data.frame(
      y = as.vector( fit.res[c(is.first.pknown-1,NROW(fit.res))] )
    ) %>%
      mutate( x = NA ) %>%
      mutate( set = "startend")
    
    slope_data = data.frame(
      y = coef.p.hl+mconst.res
    ) %>% 
      mutate( x = model_months )  %>% 
      filter( !is.na(y) ) %>% 
      mutate( set = "slope" )
    
    break_data = data.frame(
      # x = tdates[min(big.break.index)]
      x = model_months[tdates[big.break.index]]
    ) %>% 
      mutate( y=NA) %>% 
      mutate( set = "break" )
    
  }
  
  intervention_data = data.frame(
    x = model_months[known.t]
  ) %>% 
    mutate( y=NA ) %>% 
    mutate( set = "intervention" ) %>% 
    filter( x != 0 )
  
  annotation_data = data.frame(
    x = model_months[annotation.t]
  ) %>% 
    mutate( y=NA ) %>% 
    mutate( set = "annotation" ) %>% 
    filter( x != 0 )

  plot_data = real_data %>% 
    bind_rows( trend_data )
  
  if ( nbreak > 0 ) {
    if( !is.first==Inf ) {
      plot_data = plot_data %>% 
        bind_rows( startend_data ) %>% 
        bind_rows( slope_data )
      if ( length(big.break.index) != 0 ) {
        plot_data = plot_data %>% bind_rows( break_data )
      } else {
        plot_data = plot_data %>% bind_rows( data.frame( x=NA,
                                                         y=NA,
                                                         set="break") )
      }
    }  
  } else {
    plot_data = plot_data %>% bind_rows( data.frame( x=c(NA,NA),
                                                     y=c(NA,NA),
                                                     set=c("startend","startend") ) )
    plot_data = plot_data %>% bind_rows( data.frame( x=NA,
                                                     y=NA,
                                                     set="slope") )
  }
  
  plot_data = plot_data %>% 
    bind_rows( intervention_data ) %>% 
    bind_rows( annotation_data ) %>% 
    mutate( indicator = this_indicator,
            name = this_name )
  
  plotdata_holder = plotdata_holder %>% 
    bind_rows( plot_data )
  
  ggplot( plot_data ) +
    ### Plot the real data
    geom_line( data = plot_data %>% filter( set == "real" ),
               aes(x=x, y=y)) +
    ### Plot the trend on top of that
    geom_line( data = plot_data %>% filter( set == "trend" ),
               aes(x=x, y=y),
               col="red") +
    ### Plot the start/end points
    geom_rect( data=plot_data %>%
                 filter( set == "startend" ) %>%
                 arrange(y) %>%
                 mutate( val = LETTERS[1:n()] ) %>%
                 pivot_wider( names_from="val", values_from="y") %>% 
                 mutate( xmin=plot_data %>% pull(x) %>% min(na.rm=TRUE) - years(1), #as.POSIXct("2019-05-01"),
                         xmax=plot_data %>% pull(x) %>% max(na.rm=TRUE) + years(1) ),
               aes( ymin=A, ymax=B, xmin = xmin, xmax=xmax ),
               fill="purple",
               alpha=0.2) +
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
                col="green", linetype = "dashed", size=1) +
    ### Remove space between data and axes
    #scale_x_continuous(expand = c(0, 0)) +
    #scale_y_continuous(expand = c(0, 0)) +
    ### Add new labels
    labs( title = glue( "{this_indicator} // {this_name}" ),
          x = "Time series months",
          y = "Numerator over denominator" ) +
    coord_cartesian( xlim = c(plot_data %>% pull(x) %>% min(na.rm=TRUE),
                              plot_data %>% pull(x) %>% max(na.rm=TRUE)) ) +
    theme_bw()
  
  ggsave(glue("{fig_path_tis_analysis}/{this_indicator}_{this_object}_NEW.png"),
         units = "mm",
         width = 270,
         height = 270 )
  
  filename <- glue("{fig_path_tis_analysis}/{this_indicator}_{this_object}_ORIGINAL.png")
  
  wid <- 500
  hei <- 500
  png(filename)
  
  par(mfrow=c(1,1))
  islstr.res$aux$y[islstr.res$aux$y == 99] <- NA
  plot(islstr.res$aux$y, col="black", ylab="Numerator over denominator", xlab="Time series months", type="l",las=1) ##
  trendline <- tis.path$indic.fit$indic.fit+islstr.res$coefficients[islstr.res$specific.spec["mconst"]]
  lines(trendline,  col="red", lwd=2) ###fitted lines
  if (nbreak > 0){
    if (!is.first==Inf){
      abline(h=fit.res[is.first.pknown-1], lty=3, col="purple", lwd=2)### start value
      abline(h=fit.res[NROW(fit.res)], lty=3, col="purple", lwd=2)### end value
      lines(coef.p.hl+mconst.res, col=rgb(red = 1, green = 0.4118, blue = 0, alpha = 0.5), lwd=15) ###section used to evaluate slope
      #print(big.break.index)
      if (length(big.break.index) != 0){
        abline(v=tdates[min(big.break.index)], lty=2, col="blue", lwd=2) ## first negative break after intervention which is not off-set
      }
    }
  }
  abline(v=known.t, lty=1, col="blue", lwd=2)### known intervention, blue dottedwarnings()
  
  #print(names.rel[i])
  dev.copy(png,filename=filename, width=wid, height=hei)
  dev.off()
  dev.off()
  
}

save( results_holder,
      plotdata_holder,
      file = glue("{fig_path_tis_analysis}/ANALYSIS_OUTPUT.RData") )

#####################################################################
### Summary figure of slope intensity
#####################################################################

ggplot( data = results_holder %>% filter( is.nbreak > 0 ),
        aes( x = indicator,
             y = name,
             z = is.slope.ma,
             fill=is.slope.ma)) + geom_tile(col="black",size=0.5) +
  # scale_fill_brewer(type="div")
  scale_fill_distiller(palette = "PuOr") +
  theme_minimal() +
  theme( axis.text.x = element_text(angle=90,
                                    hjust=1)) 

ggsave( glue("{fig_path_tis_analysis}/SUMMARY_heatmap.png"),
        width = 6,
        height = 6 )



#####################################################################
### Draw all significant results
#####################################################################

significant_results = results_holder %>% filter( is.nbreak > 0 ) %>% select( name, indicator )

significant_plot_data = plotdata_holder %>% 
  inner_join( significant_results, by=c( "indicator", "name" ) ) %>% 
  mutate( tag = glue("{indicator}_{name}") ) %>% 
  group_by( indicator, name )

draw_change_detection_plot( significant_plot_data ) +
  theme( axis.text.x = element_text(angle=90,
                                    hjust=1)) +
  facet_wrap( ~tag, scales="free_y")

ggsave( glue("{fig_path_tis_analysis}/SUMMARY_significant.png"),
        width = 8,
        height = 8 )


#####################################################################
### Draw all results
#####################################################################

draw_change_detection_plot( plotdata_holder %>% group_by(indicator,name) ) +
  facet_grid( name~indicator, scales="free_y") +
  theme( axis.text.x = element_text(angle=90,
                                    hjust=1)) 

ggsave( glue("{fig_path_tis_analysis}/SUMMARY_all.png"),
        width = 24,
        height = 24 )

#####################################################################
### Draw all indicators for each practice
#####################################################################

for ( n in plotdata_holder %>% pull(name) %>% unique) {
  
  draw_change_detection_plot( plotdata_holder %>% 
                                filter( name == n ) %>% 
                                group_by( indicator) ) +
    facet_wrap( ~indicator, scales="free_y" ) +
    labs( title=glue("All indicators for [{n}]") ) +
    theme( axis.text.x = element_text(angle=90,
                                      hjust=1)) 
  
  ggsave( glue("{fig_path_tis_analysis}/SUMMARY_PRACTICE-{n}.png"),
          width = 8,
          height = 8 )
}

#####################################################################
### Draw all practices for each indicator
#####################################################################

for ( ind in plotdata_holder %>% pull(indicator) %>% unique) {
  
  draw_change_detection_plot( plotdata_holder %>% 
                                filter( indicator == ind ) %>% 
                                group_by( name ) ) +
    facet_wrap( ~name, scales="free_y" ) +
    labs( title=glue("All practices for [{ind}]") ) +
    theme( axis.text.x = element_text(angle=90,
                                      hjust=1)) 
  
  ggsave( glue("{fig_path_tis_analysis}/SUMMARY_INDICATOR-{ind}.png"),
          width = 8,
          height = 8 )
}



# write.csv(results, file = arguments[3])
print("Done extracting results")
