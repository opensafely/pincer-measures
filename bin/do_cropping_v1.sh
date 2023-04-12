#!/bin/bash

### Modified figures generated for publication
### Journal: BMJ Medicine
### Includes:
### - resizing
### - removing white space
### - adding panel labels
### - combining panels vertically into one plot

# TRIM and LABEL (if required)
convert -trim -background white -gravity center -extent 7500x5800 output/figures/combined_plot_gi_bleed.png output/figures/combined_plot_gi_bleed+trimmed.png
convert output/figures/combined_plot_gi_bleed+trimmed.png -gravity NorthWest -pointsize 180 -annotate +1000+750 '(a)' output/figures/combined_plot_gi_bleed+trimmed+labelled.png

convert -trim -background white -gravity center -extent 7500x3000 output/figures/combined_plot_prescribing.png output/figures/combined_plot_prescribing+trimmed.png
convert output/figures/combined_plot_prescribing+trimmed.png -gravity NorthWest -pointsize 180 -annotate +1000+300 '(b)' output/figures/combined_plot_prescribing+trimmed+labelled.png

convert -trim -background white -gravity center -extent 7500x5500 output/figures/combined_plot_monitoring.png output/figures/figure2.png

# COMBINE
convert output/figures/combined_plot_gi_bleed+trimmed+labelled.png output/figures/combined_plot_prescribing+trimmed+labelled.png -append output/figures/figure1ab.png

# MOGRIFY
magick mogrify -format tiff output/figures/figure1ab.png
magick mogrify -format tiff output/figures/figure2.png

rm output/figures/*+trimmed*.png
rm output/figures/figure1ab.png
rm output/figures/figure2.png


