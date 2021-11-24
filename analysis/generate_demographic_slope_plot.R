library(ggplot2)
library(dplyr)
library(readr)
library(magrittr)
library(tidyr)
library(glue)
library(ggrepel)

file_in = "output/demographic_aggregates.csv"

d_in = read_csv( file_in )

d_toplot = d_in %>%
    mutate( delta = post_mean - pre_mean ) %>% 
    mutate( change_class = factor( ifelse( delta < 0 ,
                                           "decrease",
                                           "increase" ),
                                   ordered=TRUE,
                                   levels=c("decrease","increase") ) ) %>% 
    pivot_longer( cols=ends_with("_mean"),
                  names_to = "timepoint",
                  values_to = "rate" ) %>% 
    mutate( timepoint_order = ifelse( timepoint == "pre_mean",
                                      "Q1 2020",
                                      "Q1 2021")) %>% 
    mutate( grouping_variable = glue("{indicator}_{group}") ) %>% 
    mutate( indicator_set = case_when(
        indicator %in% c( "li", "me_no_lft", "me_no_fbc", "ac", "am") ~ "monitoring",
        indicator %in% c( "a", "b", "c", "d", "e", "f") ~ "gi",
        TRUE ~ "other"
    )) %>%
    arrange( change_class )  %>% 
    unique( )

d_averages = d_toplot %>% 
    group_by( indicator, demographic, indicator_set, timepoint_order )  %>% 
    summarise( mean = mean( rate ) )


### 
### BY INDICATOR TYPE
### 

indicator_sets = d_toplot %>% pull( indicator_set ) %>% unique()
change_class_colour_scheme = c(
    increase = "red",
    decrease = "grey"
)
change_class_alpha_scheme = c(
    increase = 1,
    decrease = 0.6
)

demographic_labeller = c( "Age band", "Sex", "Region", "IMD", "Ethnicity" )
names( demographic_labeller ) = c( "age_band", "sex", "region", "imd", "ethnicity" )

# indicator_labeller = c( "NSAID without gastroprotection, age >=65",
#                         "NSAID without gastroprotection, H/O peptic ulcer",
#                         "Antiplatelet without gastroprotection, H/O peptic ulcer",
#                         "DOAC with warfarin",
#                         "Anticoagulation and antiplatelet, no gastroprotection",
#                         "Aspirin and antiplatelet, no gastroprotection",
#                         "Asthma and non-selective beta-blocker",
#                         "Heart failure and NSAID",
#                         "Chronic renal impairment and NSAID",
#                         "ACE inhibitor or loop diuretic without renal function/electrolyte test",
#                         "Methotrexate without full blood count",
#                         "Methotrexate without liver function test",
#                         "Lithium without lithium concentration test",
#                         "Amiodarone without thyroid function test" )

indicator_labeller = c( "GI bleed (1)", #"NSAID without gastroprotection, age >=65",
                        "GI bleed (2)", #"NSAID without gastroprotection, H/O peptic ulcer",
                        "GI bleed (3)", #"Antiplatelet without gastroprotection, H/O peptic ulcer",
                        "GI bleed (4)", #"DOAC with warfarin",
                        "GI bleed (5)", #"Anticoagulation and antiplatelet, no gastroprotection",
                        "GI bleed (6)", #"Aspirin and antiplatelet, no gastroprotection",
                        "Asthma"       , #"Asthma and non-selective beta-blocker",
                        "Heart Failure", #"Heart failure and NSAID",
                        "CKD"          , #"Chronic renal impairment and NSAID",
                        "ACEi"              , #"ACE inhibitor or loop diuretic without renal function/electrolyte test",
                        "Methotrexate (FBC)", #"Methotrexate without full blood count",
                        "Methotrexate (LFT)", #"Methotrexate without liver function test",
                        "Lithium"           , #"Lithium without lithium concentration test",
                        "Amiodarone"        #, "Amiodarone without thyroid function test"
                        )


names( indicator_labeller ) = c( "a", "b", "c", "d", "e", "f",
                                 "g", "i", "k",
                                "ac", "me_no_fbc", "me_no_lft", "li", "am" )

for ( this_set in indicator_sets ) {
    this_data = d_toplot %>% filter( indicator_set == this_set )
    these_means = d_averages %>% filter( indicator_set == this_set )
    
    num_indicators = this_data %>% pull( indicator ) %>% unique %>% length

    cat( glue("generating plots for: {this_set}\n\n"))
    
    base_plot0 = ggplot( this_data, 
                        aes(x=timepoint_order,
                            y=rate,
                            label = group,
                            group = grouping_variable,
                            colour = change_class,
                            alpha = change_class
                        )) +
        geom_line( data = this_data %>% filter( change_class == "decrease" )) + 
        geom_point( data = this_data %>% filter( change_class == "decrease" )) +
        geom_line( data = this_data %>% filter( change_class == "increase" )) + 
        geom_point( data = this_data %>% filter( change_class == "increase" )) +
        geom_text_repel( data = this_data %>%
                                filter( timepoint_order == "Q1 2021") %>%
                                filter( change_class == "increase" ),
                         direction = "y",
                         nudge_x = 0.50,
                         segment.color = "grey",
                         size = 2,
                         xlim = c(-Inf, Inf),
                         hjust = 0 ) +
        scale_x_discrete( expand = expansion(add = c(0.5,2)),
                          labels=c( "Q1 2020" = "Q1\n2020",
                                    "Q1 2021" = "Q1\n2021" ) ) +
        scale_colour_manual( values = change_class_colour_scheme ) +
        scale_alpha_manual( values = change_class_alpha_scheme ) +
        theme_bw() +
        theme( plot.margin = margin(1, 1, 2, 1, "cm"),
               legend.position = "none" ) +
        labs( title="" )

    base_plot1 = base_plot0 + geom_point( data=these_means,
                            aes(x=timepoint_order,
                                y=mean,
                                group=demographic,
                                label=demographic),
                            colour="black", alpha=1 ) +
                geom_line( data=these_means,
                            aes(x=timepoint_order,
                                y=mean,
                                group=demographic,
                                label=demographic),
                            colour="black", size=1, alpha=1 )

    plot_width = 1+1.2*num_indicators 
    base_plot1 + facet_grid( demographic ~ indicator, scales = "free",
                            labeller = labeller(demographic = demographic_labeller,
                                                indicator = indicator_labeller )  ) +
                theme( strip.text = element_text(size = 8) )
    ggsave(glue("output/figures/SLOPE_{this_set}_slope-plot.png"),
    height=9, width=plot_width )
    
}
    



