setClass("ChangeDetection",
         representation(
             name = 'character',
             verbose = 'logical',
             sample='logical',
             measure='logical',
             custom_measure='logical',
             numcores = 'numeric',
             code_variable = 'character',
             numerator_variable = 'character',
             denominator_variable = 'character',
             date_variable = 'character',
             date_format = "character",
             indir = 'character',
             outdir = 'character',
             direction='character',
             use_cache='logical',
             csv_name='character',
             overwrite='logical',
             draw_figures='logical',
             bq_folder='character',
             expected_columns = 'list',
             working_dir = 'character',
             code_tag = 'character',
             min_NA_proportion = 'numeric'
         ),
         prototype(name = NA_character_,
                   verbose = FALSE,
                   sample = FALSE,
                   measure = FALSE,
                   custom_measure=FALSE,
                   numcores = detectCores()-1,
                   code_variable = 'code',
                   numerator_variable = NA_character_,
                   denominator_variable = NA_character_,
                   date_variable = 'month',
                   date_format = "%Y-%m-%d",
                   indir = getwd(),
                   outdir = 'output',
                   direction='both',
                   use_cache=TRUE,
                   csv_name='bq_cache.csv',
                   overwrite=FALSE,
                   draw_figures=FALSE,
                   bq_folder='measures',
                   expected_columns=list(),
                   working_dir = NA_character_,
                   code_tag = 'ratio_quantity.',
                   min_NA_proportion = 0.5)
         )

ChangeDetection <- function(...) {
    a = new("ChangeDetection", ...)

    a@expected_columns = list(
        code = a@code_variable,
        month = a@date_variable,
        numerator = a@numerator_variable,
        denominator = a@denominator_variable
    )

    return( a )
}

report_info = function(cd, m) {
    if ( cd@verbose )  cat( sprintf( "[INFO::%s] %s\n", cd@name, m ) )
}

report_error = function(cd, m) {
    tag = ifelse( is.na(cd@name), "", sprintf("::%s",cd@name) )
    return( glue( "[ERROR{tag}] {m}\n" ) )
}

get_working_dir = function(cd) {
    folder_name = cd@name %>% str_replace( '%', '' )
    return( glue("{cd@outdir}/{folder_name}") )
}

create_dirs = function(cd) {
    dir.create(cd@working_dir, showWarnings = FALSE)
    dir.create(glue("{cd@working_dir}/figures"), showWarnings = FALSE)
} 

identify_missing_column_names = function(required_fields,df) {
    return( setdiff( required_fields, colnames(df) ) %>% unlist )
}

amend_column_names = function(cd,df) {
    return( df %>% rename( !!!syms(cd@expected_columns) ) )
}

check_date_format = function(cd, x) {
    report_info( cd, glue( "Checking date format {cd@date_format}") )
    return( any( is.na(as.Date(x, format=cd@date_format)) ) )
}

reformat_date = function(cd, x) {
    report_info( cd, glue( "Checking date format {cd@date_format}") )
    return( as.Date(x, format='%Y-%m-%d') )
}

date_to_epoch = function( x=today() ) {
    return( difftime( x,ymd("1970-01-01"),unit="secs") %>% as.numeric )
}

shape_dataframe = function(cd) {
    input_file = glue( "{cd@indir}/{cd@csv_name}" ) 
    input_data = read_csv( input_file, col_types = cols() )

    ### Check that all the expected columns exist in the data
    missing_columns = identify_missing_column_names( cd@expected_columns, input_data )
    if ( length(missing_columns)>0 ) {
        stop( report_error( cd, glue( "Expected column missing: '{missing_columns}'" ) ) )
    }

    ### Amend column names as required to produce expected format
    input_data = amend_column_names( cd, input_data )

    ### Check that the date is in the expected format
    input_data = input_data %>% mutate( month = as.Date(as.character(month),format=cd@date_format) )
    if ( any( is.na(input_data %>% pull(month)) ) ) {
        stop( report_error( cd, c( glue("Field '{cd@date_variable}' is not of the format '{cd@date_format}'"),
                                   glue("Try using the -Y flag to specify the date format used in the input file") ) )
        )
    }
    input_data = input_data %>% mutate( month = as.Date(month, format="%Y-%m-%d"))

    ### Retain only those data that we're expecting
    input_data = input_data %>% select( !!!syms(cd@expected_columns %>% names) )
    
    ### Calculation of new variables
    input_data = input_data %>% arrange( code, month ) %>% 
        ### Calculate the ratio
        mutate( ratio = numerator/denominator ) %>% 
        ### Modify the 'code' variable as expected
        mutate( code = glue({"{cd@code_tag}{code}"})) %>% 
        ### Remove the numerator and denominator columns
        select( -numerator, -denominator ) %>% 
        ### Replace values of +/-infinity to NA
        mutate( ratio = ifelse(is.infinite(ratio), NA, ratio ) )
    
    input_data = input_data  %>% 
        ### Convert to wide format
        pivot_wider( names_from = "code", values_from = "ratio" ) %>%
        ### Add a code variable and reorder for ease of reading
        mutate( code = 1:n() ) %>%
        select( code, month, everything() ) 
    
    ### Python script removes the bottom 5 rows - is this necessary?
    ### I'll do this here so that I can check that the results are the same
    input_data = input_data %>%
        ungroup() %>% # removing grouping to allow slice
        slice(  1:(n()-5) ) 
    
    ### Drop columns with identical values
    ratio_variability = input_data %>% ungroup() %>% select( -month, -code ) %>%
        map( ~sd(.,na.rm=T) )
    
    columns_to_keep = ratio_variability %>%
        discard( ~is.na(.) ) %>%
        discard( . == 0 ) %>% 
        names
    
    columns_to_drop = setdiff( ratio_variability %>% names, columns_to_keep)
    
    report_info( cd, glue( "Removing data for item \\
                           '{columns_to_drop %>% str_remove(cd@code_tag)}' \\
                           due to lack of variability data" ))
    
    input_data = input_data %>%
        select( code, month, !!!syms(columns_to_keep) )
    
    ### Drop columns with high proportion of NAs
    NA_proportion = input_data %>% ungroup() %>% select( -month, -code ) %>%
        map(~sum(is.na(.))) 
    
    NA_threshold = cd@min_NA_proportion * nrow(input_data)
    columns_to_keep = NA_proportion %>%
        discard( . > NA_threshold ) %>%
        names
    
    columns_to_drop = setdiff( NA_proportion %>% names, columns_to_keep)
    
    report_info( cd, glue( "Removing data for item \\
                           '{columns_to_drop %>% str_remove(cd@code_tag)}' \\
                           due to >{cd@min_NA_proportion*100}% NA values" ))
    
    input_data = input_data %>%
        select( code, month, !!!syms(columns_to_keep) )
    
    ### Add column (index) to represent number of seconds from 1970-01-01
    input_data = input_data %>% 
        mutate( index = date_to_epoch(month) ) %>% 
        select( month, index, everything())
    
    if ( cd@sample ) {
        input_data = input_data %>% sample_n(df, 100, seed=1234)
    }
    
    return(input_data)
    
}

check_input_file_exists = function(cd) {

    if ( file.exists( glue( "{cd@indir}/{cd@csv_name}" ) ) ) {
        
        ### Create working directory
        cd@working_dir = get_working_dir(cd)
        report_info( cd, glue("working directory set to: {cd@working_dir}") )
        create_dirs( cd )
        
    } else {
        stop( report_error( cd, glue( "input file does not exist: {cd@indir}/{cd@csv_name}" ) ) )
    }
}

detect_change = function(cd) {

    #####################################################################
    ### Launch R scripts ################################################
    #####################################################################
    
    #[Rscript /Users/lisahopcroft/Work/Projects/PINCER/pincer-measures/analysis/change_detection/change_detection.R /Users/lisahopcroft/Work/Projects/PINCER/pincer-measures/output/indicator_saturation/indicator_saturation_f r_input_0.csv r_intermediate_0.RData]
    #[Rscript /Users/lisahopcroft/Work/Projects/PINCER/pincer-measures/analysis/change_detection/results_extract.R /Users/lisahopcroft/Work/Projects/PINCER/pincer-measures/output/indicator_saturation/indicator_saturation_f r_intermediate_0.RData r_output_0.csv /Users/lisahopcroft/Work/Projects/PINCER/pincer-measures/analysis/change_detection both yes]
    
}

divide_data_frame = function( cd, df ) {
    
    split_groupings = df %>% pivot_longer( starts_with(cd@code_tag ),
                         names_to = "id",
                         values_to = "value" ) %>% 
        mutate( group_tmp = as.numeric( as.factor(id) )-1 )
    
    group_size = ( split_groupings %>% pull( group_tmp ) %>% max ) / cd@numcores
    
    split_groupings = split_groupings %>% 
        mutate( group = group_tmp %/% group_size ) %>% 
        select( -group_tmp ) %>% 
        group_by( group ) %>% 
        group_split() 

    split_list = vector("list",length(split_groupings))

    for ( i in 1:length(split_groupings) ) {
        split_list[[i]] = split_groupings[[i]] %>%
            select(-group) %>% 
            pivot_wider( names_from = id,
                         values_from = value )
    }
    
    return( split_list )
}



r_detect = function( cd ) {
    
    df = shape_dataframe( cd )
    df_list = divide_data_frame(cd, df)
    
}


run = function(cd) {
    report_info( cd, "running new change detection..." )
    
    check_input_file_exists( cd )
    
    r_detect( cd )

    report_info( cd, "change detection analysis complete")

}