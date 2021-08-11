import pandas as pd
import re
from pathlib import Path
from datetime import timedelta as td

BASE_DIR = Path(__file__).parents[1]
OUTPUT_DIR = BASE_DIR / "output"

def match_input_files(file: str) -> bool:
    """Checks if file name has format outputted by cohort extractor"""
    pattern = r'^input_20\d\d-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])\.csv' 
    return True if re.match(pattern, file) else False

def co_prescription(df, a: str, b: str) -> None:
    columns = [ f"earliest_{a}_month_3",
                f"earliest_{a}_month_2",
                f"earliest_{a}_month_1",
                f"earliest_{b}_month_3",
                f"earliest_{b}_month_2",
                f"earliest_{b}_month_1",
                f"latest_{a}_month_3",
                f"latest_{a}_month_2",
                f"latest_{a}_month_1",
                f"latest_{b}_month_3",
                f"latest_{b}_month_2",
                f"latest_{b}_month_1"
                ]
    
    for column in columns:
        df[column] = pd.to_datetime(df[column])
    
    df[f"co_prescribed_{a}_{b}"] = (
    (df[f"{a}"] & df[f"{b}"]) &
    (
        (
            (df[f"earliest_{a}_month_3"] < (df[f"earliest_{b}_month_3"] + td(days=28))) & 
            (df[f"earliest_{a}_month_3"] > (df[f"earliest_{b}_month_3"] - td(days=28)))
        ) |
        
        (
            (df[f"earliest_{a}_month_3"] < (df[f"latest_{b}_month_3"] + td(days=28))) & 
            (df[f"earliest_{a}_month_3"] > (df[f"latest_{b}_month_3"] - td(days=28)))
        ) |
        
        (
            (df[f"latest_{a}_month_3"] < (df[f"earliest_{b}_month_3"] + td(days=28))) & 
            (df[f"latest_{a}_month_3"] > (df[f"earliest_{b}_month_3"] - td(days=28)))
        ) |
        
        (
            (df[f"latest_{a}_month_3"] < (df[f"latest_{b}_month_3"] + td(days=28))) & 
            (df[f"latest_{a}_month_3"] > (df[f"latest_{b}_month_3"] - td(days=28)))
        ) |
        
        (df[f"latest_{a}_month_3"] > (df[f"earliest_{b}_month_2"] - td(days=28))) |
        
        (df[f"earliest_{a}_month_2"] > (df[f"latest_{b}_month_3"] + td(days=28))) |
        
        (
            (df[f"earliest_{a}_month_2"] < (df[f"earliest_{b}_month_2"] + td(days=28))) & 
            (df[f"earliest_{a}_month_2"] > (df[f"earliest_{b}_month_2"] - td(days=28)))
        ) |
        
        (
            (df[f"earliest_{a}_month_2"] < (df[f"latest_{b}_month_2"] + td(days=28))) & 
            (df[f"earliest_{a}_month_2"] > (df[f"latest_{b}_month_2"] - td(days=28)))
        ) |
        
        (
            (df[f"latest_{a}_month_2"] < (df[f"earliest_{b}_month_2"] + td(days=28))) & 
            (df[f"latest_{a}_month_2"] > (df[f"earliest_{b}_month_2"] - td(days=28)))
        ) |
        
        (
            (df[f"latest_{a}_month_2"] < (df[f"latest_{b}_month_2"] + td(days=28))) & 
            (df[f"latest_{a}_month_2"] > (df[f"latest_{b}_month_2"] - td(days=28)))
        ) |
        
        (df[f"latest_{a}_month_2"] > (df[f"earliest_{b}_month_1"] - td(days=28))) |
        
        (df[f"earliest_{a}_month_1"] > (df[f"latest_{b}_month_2"] + td(days=28))) |
        
        (
            (df[f"earliest_{a}_month_1"] < (df[f"earliest_{b}_month_1"] + td(days=28))) & 
            (df[f"earliest_{a}_month_1"] > (df[f"earliest_{b}_month_1"] - td(days=28)))
        ) |
        
        (
            (df[f"earliest_{a}_month_1"] < (df[f"latest_{b}_month_1"] + td(days=28))) & 
            (df[f"earliest_{a}_month_1"] > (df[f"latest_{b}_month_1"] - td(days=28)))
        ) |
        
        (
            (df[f"latest_{a}_month_1"] < (df[f"earliest_{b}_month_1"] + td(days=28))) & 
            (df[f"latest_{a}_month_1"] > (df[f"earliest_{b}_month_1"] - td(days=28)))
        ) |
        
        (
            (df[f"latest_{a}_month_1"] < (df[f"latest_{b}_month_1"] + td(days=28))) & 
            (df[f"latest_{a}_month_1"] > (df[f"latest_{b}_month_1"] - td(days=28)))
        ) 
    )
    
    )
    
for file in OUTPUT_DIR.iterdir():
    
    if match_input_files(file.name):
        df = pd.read_csv(OUTPUT_DIR / file.name)

        # for indicator E
        co_prescription(df, "anticoagulant", "antiplatelet_including_aspirin")
        df['indicator_e_numerator'] = df["anticoagulant"].notnull() & df["ppi"].isnull() & df["co_prescribed_anticoagulant_antiplatelet_including_aspirin"].notnull()

        # for indicator F
        co_prescription(df, "aspirin", "antiplatelet_excluding_aspirin")
        df['indicator_f_numerator'] = df["aspirin"].notnull() & df["ppi"].isnull() & df["co_prescribed_aspirin_antiplatelet_excluding_aspirin"].notnull()
        df.to_csv(OUTPUT_DIR / file.name)