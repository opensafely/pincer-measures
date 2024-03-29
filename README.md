# pincer-measures

[View on OpenSAFELY](https://jobs.opensafely.org/repo/https%253A%252F%252Fgithub.com%252Fopensafely%252Fpincer-measures)

Details of the purpose and any published outputs from this project can be found at the link above.

The contents of this repository MUST NOT be considered an accurate or valid representation of the study or its purpose. 
This repository may reflect an incomplete or incorrect analysis with no further ongoing work.
The content has ONLY been made public to support the OpenSAFELY [open science and transparency principles](https://www.opensafely.org/about/#contributing-to-best-practice-around-open-science) and to support the sharing of re-usable code for other subsequent users.
No clinical, policy or safety conclusions must be drawn from the contents of this repository.

# Project Pipeline

The project pipeline is outlined in `project.yaml`. A visual representation is shown below. All analysis code that forms part of this pipeline can be found in the `analysis` folder.

```mermaid
---
title: Project Pipeline
---
graph 
generate_study_population_1["generate_study_population_1"]
generate_study_population_2["generate_study_population_2"]
generate_study_population_3["generate_study_population_3"]
generate_study_population_4["generate_study_population_4"]
generate_study_population_5["generate_study_population_5"]
generate_study_population_ethnicity["generate_study_population_ethnicity"]
join_ethnicity_region["join_ethnicity_region"]
filter_population["filter_population"]
calculate_numerators["calculate_numerators"]
calculate_composite_indicators["calculate_composite_indicators"]
generate_measures["generate_measures"]
generate_measures_demographics["generate_measures_demographics"]
produce_stripped_measures["produce_stripped_measures"]
generate_summary_counts["generate_summary_counts"]
generate_plots["generate_plots"]
generate_notebook["generate_notebook"]
generate_notebook_updating["generate_notebook_updating"]
run_tests["run_tests"]
generate_study_population_1 ---> join_ethnicity_region
generate_study_population_2 ---> join_ethnicity_region
generate_study_population_3 ---> join_ethnicity_region
generate_study_population_4 ---> join_ethnicity_region
generate_study_population_5 ---> join_ethnicity_region
generate_study_population_ethnicity ---> join_ethnicity_region
join_ethnicity_region ---> filter_population
filter_population ---> calculate_numerators
calculate_numerators ---> calculate_composite_indicators
filter_population ---> calculate_composite_indicators
filter_population ---> generate_measures
calculate_numerators ---> generate_measures_demographics
filter_population ---> generate_measures_demographics
generate_measures ---> produce_stripped_measures
generate_measures_demographics ---> produce_stripped_measures
filter_population ---> generate_summary_counts
generate_measures ---> generate_summary_counts
generate_measures_demographics ---> generate_summary_counts
calculate_numerators ---> generate_summary_counts
produce_stripped_measures ---> generate_plots
generate_plots ---> generate_notebook
generate_summary_counts ---> generate_notebook
generate_plots ---> generate_notebook_updating
generate_summary_counts ---> generate_notebook_updating
```
# About the OpenSAFELY framework

The OpenSAFELY framework is a Trusted Research Environment (TRE) for electronic
health records research in the NHS, with a focus on public accountability and
research quality.

Read more at [OpenSAFELY.org](https://opensafely.org).

# Licences
As standard, research projects have a MIT license. 