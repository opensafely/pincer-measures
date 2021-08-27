import logging
import multiprocessing
import sys

import pandas as pd

from utilities import OUTPUT_DIR
#from study_definition import indicators_list

### Importing the local change_detection functions
sys.path.append('../bin')
from change_detection import functions as chg

indicators_list = ["a", "b", "c", "d", "e", "f", "g",
                   "i", "k", "ac", "me_no_fbc", "me_no_lft", "li", "am"]

if __name__ == '__main__':
    multiprocessing.log_to_stderr()
    logger = multiprocessing.get_logger()
    logger.setLevel(logging.INFO)
    
    for i in indicators_list:
        measures_file = f"{OUTPUT_DIR}/measure_indicator_{i}_rate.csv"

        print( f"Processing measure [{i}]: {measures_file}")

        measures_indicator = measure_indicator = chg.ChangeDetection(f'indicator_saturation_{i}',
                                   verbose=True,
                                   code_variable="practice",
                                   numerator_variable=f"indicator_{i}_numerator",
                                   denominator_variable=f"indicator_{i}_denominator",
                                   date_variable="date",
                                   date_format="%Y-%m-%d",
                                   overwrite=True,
                                   draw_figures='yes',
                                   base_dir=OUTPUT_DIR,
                                   data_subdir='indicator_saturation',
                                   csv_name=measures_file)
        measure_indicator.run()