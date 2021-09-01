print("Extracting and classifying changes")

library(caTools)
library(gets) ### main package for break detection - see Pretis, Reade, and Sucarrat, Journal of Stat. Software, in press.
library(dplyr)
library(magrittr)
library(glue)
library(tidyr)

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

source(file.path("change_detection", "trend_isat_functions.R"))

time_since_epoch <- function(d) {
  x1 <- as.POSIXct(d)
  x2 <- format(x1, tz="GMT", usetz=F)
  x3 <- lubridate::ymd_hms(x2)
  epoch <- lubridate::ymd_hms('1970-01-01 00:00:00')
  time_since_epoch <- (x3 - epoch) / dseconds()
  return(time_since_epoch)
}


#top_level_dir = arguments[1]
top_level_dir = "/Users/lisahopcroft/Work/Projects/PINCER/pincer-measures/output/indicator_saturation"
#direction = arguments[5]
direction_flag = "both"
# intervention_moment
#intervention_moment = "2019-10-15"
#known.t = time_since_epoch( intervention_moment )
#annotation.t = 10

results_information = data.frame(
  file_name = list.files(path=top_level_dir, pattern="*.RData", recursive = TRUE )
) %>%
  mutate( file_name_full = paste( top_level_dir, file_name, sep="/" ) ) %>% 
  mutate( indicator = dirname( file_name ) ) %>% 
  mutate( id = 1:n() )

results_holder = data.frame()
plotdata_holder = data.frame()


fig_path_tis_analysis = top_level_dir

###### Timing Measures
### ADD CHANGE OF GUIDANCE HERE
known.t      = 0  ### Time of known intervention in the sample, e.g. medication became available as generic at observation t=18
annotation.t = 0
break.t.lim  = .8 ### Proportion offset after negative break

###### Slope Measures
slope.lim <- 0.5   ### Proportion of slope drop for construction of slope measure



# sprintf( "[%2d] %s", 1:length(results_files), results_files)

for ( results_i in 1:nrow( results_information ) ) {
  this_result_file = ( results_information %>% pull(file_name_full) )[results_i]
  this_indicator = ( results_information %>% pull(indicator) )[results_i]
  
  load( this_result_file )
  
  vars.list = length(result.list)
  
  #################################################################
  ### Calibration of Analysis
  #################################################################
  
  # saveplots_analysis <- FALSE ###save plots of output of analysis
  # if (arguments[6] == 'yes'){
  #   saveplots_analysis <- TRUE
  # }
  
  #################################################################
  #################################################################
  
  # names.rel is the list of objects being analysed (e.g., practices)
  # result.list is a list of model results, for each object being analysed
  #   should be the same length as names.rel
  
  ### Initialising an empty data frame to store results
  these_results = data.frame( name=names.rel )
  
  # Number of Detected Breaks
  these_results$is.nbreak <- NA ### Number of breaks
  # Timing Measures
  these_results$is.tfirst <- NA ### First negative break
  these_results$is.tfirst.pknown <- NA  ### First negative break after a known intervention date
  these_results$is.tfirst.pknown.offs <- NA  ### First negative break after a known intervention date not offset by a XX% increase
  these_results$is.tfirst.offs <- NA  ###First negative break not offset by a XX% increase
  these_results$is.tfirst.big <- NA ###steepest break as identified by is.slope.ma
  # Slope Measures
  these_results$is.slope.ma <- NA ### Average slope over steepest segment contributing at least XX% of total drop
  these_results$is.slope.ma.prop <- NA ### Average slope as proportion to prior level
  these_results$is.slope.ma.prop.lev <- NA ### Percentage of the total drop the segment used to evaluate the slope makes up
  # Level Measures
  these_results$is.intlev.initlev <- NA  ### Pre-drop level
  these_results$is.intlev.finallev <- NA ### End level
  these_results$is.intlev.levd <- NA ### Difference between pre and end level
  these_results$is.intlev.levdprop <- NA ### Proportion of drop
  
  #################################################################
  ### Loop over different series
  #################################################################
  
  for (i in 1:(vars.list)) {
    
    sprintf( "Looking at object: %s",  names.rel[i] )
    
    model_months          = data.pick$month.c
    y                     = data.pick[names.rel[i]]
    these_results$name[i] = names.rel[i]
    islstr.res            = result.list[[i]]

    ### Number of trend breaks
    nbreak = NROW(grep("tis", islstr.res$ISnames))
    these_results$is.nbreak[i] = nbreak #number of breaks
    
    ###coefficient path
    tis.path = trend.var(islstr.res)
    
    #############################################
    ##### Measure 1: Timing of Breaks
    ################################################
    
    if (nbreak > 0) { ##if there are any relevant breaks
      
      #trend break names:
      tnames = islstr.res$ISnames[grep("tis", islstr.res$ISnames)]
      
      if (NCOL(islstr.res$aux$mX[,tnames]) > 1){
        tdates <-  apply(islstr.res$aux$mX[,tnames], 2, function(x) (which(x>0))[1])  ##finds first non-zero index
      } else {
        tdates <-  min(which(islstr.res$aux$mX[,tnames] > 0))
      }
      
      ###coefficients and fitted values
      rel.coef.num <- islstr.res$specific.spec[tnames]
      rel.coef <- islstr.res$coefficients[rel.coef.num]
      mconst.res <- islstr.res$coefficients[islstr.res$specific.spec["mconst"]]
      fit.res <- fitted(islstr.res) ##fitted values
      fit.res <- fit.res[!fit.res<0]
      
      # #### Measure 1.1: the first breaks where the coefficient path is also downward sloping
      # if ( direction_flag == 'both') {
      #   direction <- 'min(which(tis.path$indic.fit$coef != 0))'
      # }
      # else if ( direction_flag == 'up') {
      #   direction <- 'min(which(tis.path$indic.fit$coef > 0))'
      # }
      # else if ( direction_flag == 'down') {
      #   direction <- 'min(which(tis.path$indic.fit$coef < 0))'
      # } else {
      #   # If not provided, assume both
      #   direction 
      # }
      # 
      direction_operator = case_when( direction_flag == "both" ~ "!=",
                                      direction_flag == "up"   ~ ">",
                                      direction_flag == "down" ~ "<",
                                      TRUE                ~ "!=" )
      
      direction_filter_statement = glue("min(which(tis.path$indic.fit$coef {direction_operator} 0))")
      
      is.first <- eval(parse(text=direction_filter_statement))
      these_results$is.tfirst[i] <- is.first
      
      ### Measure 1.2: first negative break after the known break-date intervention
      # if ( direction_flag == 'both'){
      #   direction <- 'min( tdates[which(tis.path$indic.fit$coef[tdates] != 0)][tdates[which(tis.path$indic.fit$coef[tdates] != 0)] > known.t] )'
      # }
      # else if ( direction_flag == 'up'){
      #   direction <- 'min( tdates[which(tis.path$indic.fit$coef[tdates] > 0)][tdates[which(tis.path$indic.fit$coef[tdates] > 0)] > known.t] )'
      # }
      # else if ( direction_flag == 'down'){
      #   direction <- 'min( tdates[which(tis.path$indic.fit$coef[tdates] < 0)][tdates[which(tis.path$indic.fit$coef[tdates] < 0)] > known.t] )'
      # }
      
      direction_filter_statement = glue("min( tdates[which(tis.path$indic.fit$coef[tdates] {direction_operator} 0)][tdates[which(tis.path$indic.fit$coef[tdates]  {direction_operator} 0)] > known.t] ) ")
      
      is.first.pknown <- eval(parse(text=direction_filter_statement))
      these_results$is.tfirst.pknown[i] <- is.first.pknown

      
      
      #### Measure 1.3: the first negative break where there is no subsequent offset of at least break.t.lim
      offset <- array(NA, dim=NROW(tdates))
      levels <- array(NA, dim=NROW(tdates))
      
      for (j in 1:NROW(tdates)){
        
        ###for each break, compute the total change
        date <- tdates[j]
        
        if (j < NROW(tdates)){
          enddate <- tdates[j+1]
        } else {
          enddate <- NROW(tis.path$indic.fit$indic.fit)
        }
        startlev <- tis.path$indic.fit$indic.fit[date-1]
        endlev <- tis.path$indic.fit$indic.fit[enddate-1]
        levchange <- endlev - startlev
        
        levels[j] <- levchange
        
      }
      
      ratios <- array(NA, dim= (NROW(levels)-1))
      
      if ( NROW(levels) > 1){
        
        for (j in 1: (NROW(levels)-1)){
          
          ratios[j] <-  levels[j+1]/levels[j]
          
          if (ratios[j] < -break.t.lim & !is.na(ratios[j])){
            offset[j] <- TRUE
          } else {
            offset[j] <- FALSE
          }
          
          offset[NROW(levels)] <- FALSE
        }
        
      } else {
        offset <- FALSE
      }
      
      
      ############ FUTURE - ADD IN OFFSETS *BEFORE* BREAK TOO ###############
      ### Store first negative break which is not offset and which occurs after known break date
      # if (arguments[5] == 'both'){
      #   direction <- 'min(tdates[rel.coef != 0 & tdates >= known.t & tis.path$indic.fit$coef[tdates] != 0 & offset == FALSE])'
      # }
      # else if (arguments[5] == 'up'){
      #   direction <- 'min(tdates[rel.coef > 0 & tdates >= known.t & tis.path$indic.fit$coef[tdates] > 0 & offset == FALSE])'
      # }
      # else if (arguments[5] == 'down'){
      #   direction <- 'min(tdates[rel.coef < 0 & tdates >= known.t & tis.path$indic.fit$coef[tdates] < 0 & offset == FALSE])'
      # }
      # 
      
      direction_filter_statement = glue("min(tdates[rel.coef {direction_operator} 0 & tdates >= known.t & tis.path$indic.fit$coef[tdates] {direction_operator} 0 & offset == FALSE])")
      
      is.first.pknown.offs <- eval(parse(text=direction_filter_statement))
      these_results$is.tfirst.pknown.offs[i] <- is.first.pknown.offs
      
      ### Store first negative break which is not offset  (regardless of known break date)
      # if (arguments[5] == 'both'){
      #   direction <- 'min(tdates[rel.coef != 0  & tis.path$indic.fit$coef[tdates] != 0 & offset == FALSE])'
      # }
      # else if (arguments[5] == 'up'){
      #   direction <- 'min(tdates[rel.coef > 0  & tis.path$indic.fit$coef[tdates] > 0 & offset == FALSE])'
      # }
      # else if (arguments[5] == 'down'){
      #   direction <- 'min(tdates[rel.coef < 0  & tis.path$indic.fit$coef[tdates] < 0 & offset == FALSE])'
      # }
      
      direction_filter_statement = glue("min(tdates[rel.coef {direction_operator} 0  & tis.path$indic.fit$coef[tdates] {direction_operator} 0 & offset == FALSE])")
      
      is.first.offs <- eval(parse(text=direction_filter_statement))
      these_results$is.tfirst.offs[i] <- is.first.offs
      
      #############################################
      ##### Measure 2 Steepness/Slope: average slope of the steepest contiguous segment contributing to at least XX% of the total level change
      ################################################
      
      print(!is.first==Inf)
      
      if (!is.first==Inf)  { #first break not to lie before the known break date
        
        coefp.dif <- tis.path$indic.fit$coef
        const.path <-  tis.path$indic.fit$indic.fit
        
        first.index <-  which(tdates==is.first.pknown )
        interval <- const.path[tdates[first.index:length(tdates)]-1]
        #predrop <- fit.res[is.first.pknown-1] #changed: FP Sept 13th.
        predrop <- fit.res[is.first.pknown]
        
        #totaldif  <- sum(coefp.dif[(is.first.pknown-1):(NROW(coefp.dif))]) # total drop, change in every period, i.e. the slope #changed: FP Sept 13th.
        totaldif  <- sum(coefp.dif[(is.first.pknown):(NROW(coefp.dif))]) # total drop, change in every period, i.e. the slope
        
        max_interval <- NROW(const.path) - is.first.pknown + 1
        
        
        grid_sum <- matrix(NA, ncol=max_interval, nrow=max_interval)
        grid_mean <- matrix(NA, ncol=max_interval, nrow=max_interval)
        
        #####Grid Search:
        
        for (j in 1:max_interval){
          grid_sum[,j] <- runmean(coefp.dif[(is.first.pknown):NROW(coefp.dif)], j, align="left", endrule="NA")*j  #sum over every length (columns) at every point (rows)
          grid_mean[,j] <-  runmean(coefp.dif[(is.first.pknown):NROW(coefp.dif)], j, align="left", endrule="NA") #take the running mean of the slope, corresponding to the values above
          
        }
        
        grid_prop <- grid_sum*(as.numeric(totaldif))^(-1)
        
        maxc <- apply(grid_prop,2,max, na.rm=TRUE)
        min_index <- min(which(maxc>slope.lim))
        
        #Find the steepest slope that falls within this shortest interval and satisfies the XX% requirement:
        minslopgrid <- which(grid_prop[,min_index] > slope.lim)
        slopeval <- grid_mean[minslopgrid[which.max(abs(grid_mean[minslopgrid, min_index]))], min_index] ###find the maximum slope, on the shortest interval, that yields over XX% drop
        
        interval.full <- const.path[c(tdates[first.index:length(tdates)]-1, NROW(const.path))]
        
        if(length(tdates[first.index:length(tdates)])>1){   #if more than one break
          slopindex <- minslopgrid[which.max(abs(grid_mean[minslopgrid, min_index]))]
        } else { #if just one break
          slopindex <- 1   #start at the beginning
        }
        
        
        coef.p <- const.path
        coefp.dif.hl <- coefp.dif*NA
        coefp.dif.hl[(is.first.pknown+slopindex-2):((is.first.pknown+slopindex)+min_index-3) ] <- coefp.dif[(is.first.pknown+slopindex-2):((is.first.pknown+slopindex)+min_index-3) ]
        
        ### Store the part of the slope segment evaluated for plotting
        coef.p.hl <- coef.p*NA
        coef.p.hl[(is.first.pknown+slopindex-2):((is.first.pknown+slopindex)+min_index-2)] <- const.path[(is.first.pknown+slopindex-2):((is.first.pknown+slopindex)+min_index-2)]
        result.list[[i]]$is.results$coef.p.hl <- coef.p.hl
        
        
        big.break.index <- which(round(tis.path$coef.var$coef, digits = 4)==round(slopeval, digits = 4))
        
        ###Store Slope Results
        these_results$is.slope.ma[i] <- slopeval    #slope over the contiguous segment
        these_results$is.slope.ma.prop[i] <- slopeval/predrop #slope over the contiguous segment as proportion of prior level
        these_results$is.slope.ma.prop.lev[i] <- grid_prop[slopindex,min_index ] #percentage of total drop that the contiguous segment contributes
        
        ###Biggest break
        big.break <- is.first.pknown+slopindex-1 ### which(round(tis.path$coef.var$coef, digits = 4)==round(slopeval, digits = 4))
        these_results$is.tfirst.big[i] <- big.break

      }
      
      
      #############################################
      ##### Measure 3: Magnitude of Change
      ################################################
      
      start.lev <- is.first.pknown-1
      init.lev <- fit.res[start.lev]
      end.lev <- fit.res[NROW(fit.res)]
      
      ### Store Magnitude Results
      these_results$is.intlev.initlev[i] <- init.lev
      these_results$is.intlev.finallev[i] <- end.lev
      these_results$is.intlev.levd[i] <- as.numeric(init.lev) - as.numeric(end.lev)   #absulte change
      these_results$is.intlev.levdprop[i] <-  (as.numeric(init.lev) - as.numeric(end.lev))/as.numeric(init.lev)         #percentage change
      
      print(paste(round((i / vars)*100,1), "%"))
    } ## if there are breaks closed
    
    these_results = these_results  %>% 
      mutate( indicator = this_indicator,
              name = these_results$name )
    
    real_data = data.frame(
      y=islstr.res$aux$y
    ) %>%
      mutate( y = ifelse( y==99, NA, y) ) %>% 
      mutate( x = model_months ) %>% 
      mutate( set = "real" )
    
    trend_data = data.frame(
      y = tis.path$indic.fit$indic.fit+islstr.res$coefficients[islstr.res$specific.spec["mconst"]]
    ) %>% 
      mutate( x = model_months ) %>% 
      mutate( set="trend" )
    
    startend_data = data.frame(
      y = fit.res[c(is.first.pknown-1,NROW(fit.res))]
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
      x = model_months[tdates[min(big.break.index)]]
    ) %>% 
      mutate( y=NA) %>% 
      mutate( set = "break" )
    
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
    
    # if (!is.first==Inf){
    #   abline(h=fit.res[is.first.pknown-1], lty=3, col="purple", lwd=2)### start value
    #   abline(h=fit.res[NROW(fit.res)], lty=3, col="purple", lwd=2)### end value
    #   lines(coef.p.hl+mconst.res, col=rgb(red = 1, green = 0.4118, blue = 0, alpha = 0.5), lwd=15) ###section used to evaluate slope
    #   #print(big.break.index)
    #   if (length(big.break.index) != 0){
    #     abline(v=tdates[min(big.break.index)], lty=2, col="blue", lwd=2) ## first negative break after intervention which is not off-set
    #   }
    # }
    
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
              name = these_results$name[i] )
    
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
      labs( title = glue( "{this_indicator} // {these_results$name[i]}" ),
            x = "Time series months",
            y = "Numerator over denominator" ) +
      coord_cartesian( xlim = c(plot_data %>% pull(x) %>% min(na.rm=TRUE),
                                plot_data %>% pull(x) %>% max(na.rm=TRUE)) ) +
      theme_bw()
      
    ggsave(glue("{fig_path_tis_analysis}/{this_indicator}_{these_results$name[i]}_NEW.png"),
           units = "px",
           width = 1024,
           height = 1024 )
    
    filename <- glue("{fig_path_tis_analysis}/{this_indicator}_{these_results$name[i]}_ORIGINAL.png")
    
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
    
  } #loop over i closed 
  
  results_holder = results_holder %>% 
    bind_rows( these_results )
  
}

#####################################################################
### Draw all significant results
#####################################################################

significant_results = results_holder %>% filter( is.nbreak > 0 ) %>% select( name, indicator )

significant_plot_data = plotdata_holder %>% 
  inner_join( significant_results, by=c( "indicator", "name" ) ) %>% 
  mutate( tag = glue("{indicator}_{name}") ) %>% 
  group_by(indicator, name )

draw_change_detection_plot( significant_plot_data ) + facet_wrap( ~tag, scales="free_y")

ggsave( glue("{fig_path_tis_analysis}/SUMMARY_significant.png"),
        units = "px",
        width = 1024*5,
        height = 1024*5 )


#####################################################################
### Draw all results
#####################################################################

draw_change_detection_plot( plotdata_holder %>% group_by(indicator,name) ) +
  facet_grid( name~indicator, scales="free_y")

ggsave( glue("{fig_path_tis_analysis}/SUMMARY_all.png"),
        units = "px",
        width = 1024*5,
        height = 1024*10 )

#####################################################################
### Draw all indicators for each practice
#####################################################################

for ( n in plotdata_holder %>% pull(name) %>% unique) {
  
  draw_change_detection_plot( plotdata_holder %>% 
                                filter( name == n ) %>% 
                                group_by( indicator) ) +
    facet_wrap( ~indicator, scales="free_y" ) +
    labs( title=glue("All indicators for [{n}]") )
  
  ggsave( glue("{fig_path_tis_analysis}/SUMMARY_PRACTICE-{n}.png"),
          units = "px",
          width = 1024,
          height = 1024 )
}

#####################################################################
### Draw all practices for each indicator
#####################################################################

for ( ind in plotdata_holder %>% pull(indicator) %>% unique) {
  
  draw_change_detection_plot( plotdata_holder %>% 
                                filter( indicator == ind ) %>% 
                                group_by( name ) ) +
    facet_wrap( ~name, scales="free_y" ) +
    labs( title=glue("All practices for [{ind}]") )
  
  ggsave( glue("{fig_path_tis_analysis}/SUMMARY_INDICATOR-{ind}.png"),
          units = "px",
          width = 1024,
          height = 1024 )
}


# write.csv(results, file = arguments[3])
print("Done extracting results")
