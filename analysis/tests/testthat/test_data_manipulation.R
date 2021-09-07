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

d_wide = make_test_df_to_split()
d_long = d_wide %>%
    pivot_longer( starts_with(default_values@code_tag ),
                  names_to = "id",
                  values_to = "value" )

test_that( "All data are retained when input data are split", {
    ### The test dataframe (d_wide) contains data for:
    ### (1) 10 measurements for...
    ### (2) 5 different entities (e.g., practice) over the course of...
    ### (3) 6 months.
    ### The divide_data_frame() function will divide the 10 measurements
    ### into the requested number of chunks (which is captured by
    ### the @numcores variable in the provided ChangeDetection() object,
    ### in this case default_values.
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
    ### Note that checks following option parsing prevent the
    ### case where i = 0 so that dies not need to be tested 
    ### here.
    for( i in 1:11 ) {
        tmp_cd@numcores=i
        split_d = divide_data_frame( tmp_cd, d_wide )
        ### The data will be split into either the requested number
        ### of chunks, or the number of data columns in the data
        ### frame, whichever is less. This explains the use of 
        ### min() in the test below.
        expect_equal( length(split_d),
                      min(i,(ncol(d_wide)-2) ))
    }
})







