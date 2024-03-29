
n = 4

test_df = data.frame( 
    object = LETTERS[1:n],
    a_numerator = 1:n,
    a_denominator = (1:n)+2,
    timestamp = ymd(sample(seq(as.Date('1999/01/01'),
                           as.Date('2000/01/01'), by="day"), n))
)

test_m = ChangeDetection(
    code_variable = "object",
    numerator_variable = "a_numerator",
    denominator_variable = "a_denominator",
    date_variable = "timestamp"
)

context( "Input data handling" )

test_that( "Column names are amended correctly",
    expect_equal( sort( amend_column_names(test_m,test_df) %>% colnames ),
                  test_m@expected_columns %>% names %>% sort )
)

test_that( "All missing column names are identified",
           expect_equal( sort( identify_missing_column_names(
               test_m@expected_columns %>% names,
               test_df) ),
               test_m@expected_columns %>% names %>% sort
           )
)

test_that( "Input file check works", {
    t = tempfile(pattern = "file", tmpdir = tempdir(), fileext = "")
    test_m@csv_name = basename( t )
    test_m@name = basename( t )
    test_m@indir = dirname( t )
    write_csv( test_df, t )
    
    expect_equal( check_input_file_exists(test_m),
                  glue( "{default_values@outdir}/{basename(t)}" ) )
    
})

test_that( "Missing input file gives error", {
    t = tempfile(pattern = "file", tmpdir = tempdir(), fileext = "")
    test_m@csv_name = basename( t )
    test_m@name = basename( t )
    test_m@indir = dirname( t )
    write_csv( test_df, t )
    system( glue( "rm {t}" ) ) # Removing so that we know it doesn't exist
    
    expect_error( check_input_file_exists(test_m) )
})

test_that( "Date to epoch calculation is correct", {
    expect_equal( date_to_epoch(as.Date("1970-01-01")), 0 )
    expect_equal( date_to_epoch(as.Date("1970-01-01") + seconds(10)), 10)
    expect_equal( date_to_epoch(ymd("1970-01-01") + seconds(10)), 10)
})




