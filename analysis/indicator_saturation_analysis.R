source("analysis/indicator_saturation_functions.R")

#####################################################################
### Parsing arguments ###############################################
#####################################################################

opt_parser = OptionParser(usage = "%prog [options] csv_file",
                          option_list=option_list )

opt = parse_args( opt_parser, positional_arguments = TRUE )

fatal_missing_args = c()

### Checking for missing required arguments/problematic inputs ######

if ( length( opt$args) == 0 ) {
    fatal_missing_args = c( fatal_missing_args,
                            "You must supply a file name" )
}

if (is.null(opt$options$indicator)){
    fatal_missing_args = c( fatal_missing_args,
                            "You must supply an indicator name" )
}

if ( opt$options$numcores < 1 ) {
    fatal_missing_args = c( fatal_missing_args,
                            "You must request at least 2 cores for processing" )
}

if ( length(fatal_missing_args) > 0 ) {
    print_help(opt_parser)
    messages = glue("- {fatal_missing_args}")
    stop(report_error( default_values, paste(messages,collapse='\n') ), call.=FALSE)
}

### Assuming numerators/denominators if not supplied ################

if (is.null( opt$options$numerator ) ) {
    opt$options$numerator = sprintf( "indicator_%s_numerator", opt$options$indicator )
}

if (is.null( opt$options$denominator ) ) {
    opt$options$denominator = sprintf( "indicator_%s_denominator", opt$options$indicator )
}

for ( this_direction in c( "up","down" ) ) {
    
    measure_indicator = ChangeDetection(
        name = glue('indicator_saturation_{this_direction}_{opt$options$indicator}'),
        code_variable = opt$options$code,
        numerator_variable = opt$options$numerator,
        denominator_variable = opt$options$denominator,
        date_variable = unlist(opt$options$date),
        date_format = opt$options$ymd,
        numcores = opt$options$numcores,
        indir = opt$options$indir,
        outdir = opt$options$outdir,
        direction = this_direction,
        overwrite = opt$options$overwrite,
        draw_figures = opt$options$figures,
        verbose = opt$options$verbose,
        test_number = opt$options$test,
        csv_name = opt$args[1]
    )
    
    run( measure_indicator )
    
}


### To test:
### Rscript indicator_saturation_analysis.R -I a -T date -C practice -v -i ../output -o ../output/indicator_saturation2 measure_indicator_a_rate.csv -f
