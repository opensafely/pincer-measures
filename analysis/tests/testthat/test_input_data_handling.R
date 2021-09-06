context( "Input data handling")

test_that( "Column names are amended correctly", {
    m = ChangeDetection(
        code_variable = "object",
        numerator_variable = "a_numerator",
        denominator_variable = "a_denominator",
        date_variable = "timestamp"
    )
    n = 4
    df = data.frame( 
        object = LETTERS[1:n],
        a_numerator = 1:n,
        a_denominator = (1:n)+2,
        timestamp = sample(seq(as.Date('1999/01/01'),
                                   as.Date('2000/01/01'), by="day"), n)
    )
    
    expect_equal( sort( amend_column_names(m,df) %>% colnames ),
                  m@expected_columns %>% names %>% sort )
}
)
