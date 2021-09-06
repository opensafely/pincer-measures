library(optparse , quietly=T, warn.conflicts = FALSE)
library(glue     , quietly=T, warn.conflicts = FALSE)
library(parallel , quietly=T, warn.conflicts = FALSE)
library(magrittr , quietly=T, warn.conflicts = FALSE)
library(stringr  , quietly=T, warn.conflicts = FALSE)
library(readr    , quietly=T, warn.conflicts = FALSE)
library(dplyr    , quietly=T, warn.conflicts = FALSE)
library(tidyr    , quietly=T, warn.conflicts = FALSE)
library(tibble   , quietly=T, warn.conflicts = FALSE)
library(purrr    , quietly=T, warn.conflicts = FALSE)
library(lubridate, quietly=T, warn.conflicts = FALSE)


source("indicator_saturation_functions.R")

empty = new( "ChangeDetection" )

option_list = list(
    ### Parameters that define the analysis
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
    make_option(c("-Z", "--numcores"), type="numeric", default=empty@numcores,
                help="number of cores to use [default=%default]", metavar="numeric"),
    
    ### Parameters that define the input/output/reporting
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

opt = parse_args( opt_parser, positional_arguments = TRUE )

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
    stop(report_error( empty, paste(messages,collapse='\n') ), call.=FALSE)
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
    numcores = opt$options$numcores,
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
### Rscript indicator_saturation_analysis.R -I a -T date -C practice -v -i ../output -o ../output/indicator_saturation2 measure_indicator_a_rate.csv -f
