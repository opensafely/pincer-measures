source("indicator_saturation_functions.R")

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
