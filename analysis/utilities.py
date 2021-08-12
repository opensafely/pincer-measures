import re

def match_input_files(file: str) -> bool:
    """Checks if file name has format outputted by cohort extractor"""
    pattern = r'^input_20\d\d-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])\.csv' 
    return True if re.match(pattern, file) else False

def get_date_input_file(file: str) -> str:
    """Gets the date in format YYYY-MM-DD from input file name string"""
    #check format
    if not match_input_files(file):
        raise Exception('Not valid input file format')
    
    else:
        date = result = re.search(r'input_(.*)\.csv', file)
        return date.group(1)