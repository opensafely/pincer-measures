import logging
import multiprocessing
import sys
import pandas as pd
import argparse

from utilities import OUTPUT_DIR
#from study_definition import indicators_list

### Importing the local change_detection functions
# sys.path.append('bin')
from change_detection import functions as chg

indicators_list = ["a", "b", "c", "d", "e", "f", "g",
                   "i", "k", "ac", "me_no_fbc", "me_no_lft", "li", "am"]

if __name__ == '__main__':

    argv = sys.argv[1:]

    p = argparse.ArgumentParser(description="Run an indicator saturation analysis",
    allow_abbrev=True)

    p.add_argument('-indicator', type=str, help='the indicator id',
                   choices=indicators_list, required=True)
    p.add_argument('-numerator', type=str, help='the numerator column')
    p.add_argument('-denominator', type=str, help='the denominator column')

    args = p.parse_args()        

    if args.numerator == None:
        args.numerator = f"indicator_{args.indicator}_numerator"

    if args.denominator==None:
        args.denominator = f"indicator_{args.indicator}_denominator"

    multiprocessing.log_to_stderr()
    logger = multiprocessing.get_logger()
    logger.setLevel(logging.INFO)
        
    measures_file = f"{OUTPUT_DIR}/measure_indicator_{args.indicator}_rate.csv"

    print( f"Processing measure [{args.indicator}]: {measures_file}")

    measure_indicator = chg.ChangeDetection(f'indicator_saturation_{args.indicator}',
                                    verbose=True,
                                    code_variable="practice",
                                    numerator_variable=args.numerator,
                                    denominator_variable=args.denominator,
                                    date_variable="date",
                                    date_format="%Y-%m-%d",
                                    overwrite=True,
                                    draw_figures='yes',
                                    base_dir=OUTPUT_DIR,
                                    data_subdir='indicator_saturation',
                                    csv_name=measures_file)
    measure_indicator.run()