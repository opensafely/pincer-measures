#!/usr/bin/env Rscript
library(optparse)
library(glue)
library(parallel)
library(magrittr)
library(stringr)
library(readr)
library(dplyr)

source("indicator_saturation_functions.R")

empty = new( "ChangeDetection" )

option_list = list(
    ### Indicator/numerator/denominator/dateformat
    # make_option(c("-f", "--file"), type="character", default=NULL,
    #             help="input file name (required)", metavar="character"),
    make_option(c("-I", "--indicator"), type="character", default=NULL,
                help="indicator name (required)", metavar="character"),
    make_option(c("-C", "--code"), type="character", default=empty@code_variable,
                help="code column name", metavar="character"),
    make_option(c("-A", "--numerator"), type="character", default=NULL, 
                help="numerator column name", metavar="character"),
    make_option(c("-B", "--denominator"), type="character", default=NULL, 
                help="output directory name", metavar="character"),
    make_option(c("-T", "--date"), type="character", default=empty@date_variable,
                help="date column name [default=%default]", metavar="character"),
    make_option(c("-Y", "--ymd"), type="character", default=empty@date_format,
                help="date format of input file [default=%default]", metavar="character"),
    make_option(c("-D", "--direction"), type="character", default=empty@direction,
                help="direction (up/down/both) of change to identify [default=%default]", metavar="character"),
    
    ### Input/output
    make_option(c("-v", "--verbose"), action="store_true", default=empty@verbose,
                help="Print extra output [default]"),
    make_option(c("-i", "--indir"), type="character", default=empty@indir, 
                help="output directory name [default= %default]", metavar="character"),
    make_option(c("-o", "--outdir"), type="character", default=empty@outdir, 
                help="output directory name [default= %default]", metavar="character"),
    make_option(c("-x", "--overwrite"), action="store_true", default=empty@overwrite,
                help="overwrite existing content? [default= %default]", metavar="character"),
    make_option(c("-f", "--figures"), action="store_true", default=empty@draw_figures,
                help="generate figures? [default=%default]", metavar="character")
)

#####################################################################
### Parsing arguments ###############################################
#####################################################################

opt_parser = OptionParser(usage = "%prog [options] csv_file",
                           option_list=option_list )

opt = parse_args(opt_parser, positional_arguments = 1)

fatal_missing_args = c()

### Checking for missing required arguments #########################

if ( length( opt$args) == 0 ) {
    fatal_missing_args = c( fatal_missing_args,
                            "You must supply a file name" )
}

if (is.null(opt$options$indicator)){
    fatal_missing_args = c( fatal_missing_args,
                            "You must supply an indicator name" )
}

if ( length(fatal_missing_args) > 0 ) {
    print_help(opt_parser)
    messages = glue("- {fatal_missing_args}")
    
    stop(glue("\n\n{paste(messages,collapse='\n')}\n\n\n"), call.=FALSE)
}

### Assuming numerators/denominators if not supplied ################

if (is.null( opt$options$numerator ) ) {
    opt$options$numerator = sprintf( "indicator_%s_numerator", opt$options$indicator )
}

if (is.null( opt$options$denominator ) ) {
    opt$options$denominator = sprintf( "indicator_%s_denominator", opt$options$indicator )
}


measure_indicator = ChangeDetection(
    name = glue('indicator_saturation_{opt$options$indicator}'),
    code_variable = opt$options$code,
    numerator_variable = opt$options$numerator,
    denominator_variable = opt$options$denominator,
    date_variable = unlist(opt$options$date),
    date_format = opt$options$ymd,
    indir = opt$options$indir,
    outdir = opt$options$outdir,
    direction = opt$options$direction,
    overwrite = opt$options$overwrite,
    draw_figures = opt$options$figures,
    verbose = opt$options$verbose,
    csv_name = opt$args[1]
)

run( measure_indicator )

### To test:
### Rscript indicator_saturation_analysis.R -I a -T date -C practice -v -i /Users/lisahopcroft/Work/Projects/PINCER/pincer-measures/output measure_indicator_a_rate.csv

