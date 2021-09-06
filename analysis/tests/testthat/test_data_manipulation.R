make_test_df_to_split = function(num_measurements = 10,
                                 num_entities = 5,
                                 num_months = 6,
                                 tag_string = default_values@code_tag ) {
    
    code_list  = glue( "OBJECT_{1:num_entities}" )
    month_list = seq( ymd("2020-01-01"),
                      ymd("2020-01-01")+months(num_months-1),
                      by="month" )
    
    df = matrix( data=rnorm( num_measurements * num_entities * num_months ),
                 ncol = num_measurements,
                 nrow = num_entities * num_months) %>%
        as.data.frame
    colnames(df) = colnames(df) %>% str_replace( "V", tag_string )
    
    df = df %>%
        mutate( code = rep.int( code_list, num_months ) ) %>% 
        mutate( month = rep( month_list, each=num_entities ) ) %>% 
        select( code, month, everything() ) %>%
        as_tibble() 
}


context( "Splitting dataframe to process in chunks" )

d_wide = make_test_df_to_split( )
d_long = d_wide %>%
    pivot_longer( starts_with(default_values@code_tag ),
                  names_to = "id",
                  values_to = "value" )

test_that( "All data are retained when input data are split", {
    split_d = divide_data_frame( default_values, d_wide )
    
    d_wide = d_wide %>% 
        arrange( code, month ) %>% 
        select(sort(tidyselect::peek_vars()))
    
    recon_d = split_d %>%
        reduce(left_join, by = c("code","month")) %>%
        arrange( code, month ) %>% 
        select(sort(current_vars()))
    
    expect_equal( d_wide, recon_d )
})

test_that( "Data are split into the right number of subsets", {
    tmp_cd = default_values
    for( i in 1:11 ) {
        tmp_cd@numcores=i
        split_d = divide_data_frame( tmp_cd, d_wide )
        expect_equal( length(split_d),
                      min(i,(ncol(d_wide)-2) ))
    }
})







