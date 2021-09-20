import json
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utilities import OUTPUT_DIR, drop_irrelevant_practices, get_practice_deciles

def plot_cusum(results, filename):
        plt.figure(figsize=(15,8))
        plt.plot([a+b for a, b in zip(results['target_mean'], results['smin'])], color='red')
        plt.plot([a+b for a, b in zip(results['target_mean'], results['smax'])], color='turquoise')
        plt.plot([a+b for a, b in zip(results['target_mean'], results['alert_threshold'])], color='black', linestyle='--')
        plt.plot([a-b for a, b in zip(results['target_mean'], results['alert_threshold'])], color='black', linestyle='--')  
        plt.ylabel('value')
        plt.xlabel('date')
        plt.xticks(ticks = [i for i in range(len(data['date']))], labels = data['date'].values, rotation=90)
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / f'cusum/cusum/{filename}')
        plt.clf()

def plot_median(array, results, filename):
        
        plt.figure(figsize=(15,8))
        plt.plot(array)
        plt.plot(results['target_mean'], color='red')
        plt.ylabel('value')
        plt.xlabel('date')
        plt.xticks(ticks = [i for i in range(len(data['date']))], labels = data['date'].values, rotation=90)
            
        for i in results['alert']:
            plt.scatter(x=i, y=array[i], color='green', s=50)
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / f'cusum/alerts/{filename}')
        plt.clf()



if not (OUTPUT_DIR / 'cusum').exists():
    os.mkdir(OUTPUT_DIR / 'cusum')
    os.mkdir(OUTPUT_DIR / 'cusum/cusum')
    os.mkdir(OUTPUT_DIR / 'cusum/alerts')

with open(OUTPUT_DIR / 'cusum_results.json') as file:
    # Load its content and make a new dictionary
    data = json.load(file)

    for indicator_key, indicator_value in data.items():
        print(indicator_key)
        
       
        for practice_key, practice_value in indicator_value.items():
            if len(practice_value['alert'])>0:
                
                df = pd.read_csv(OUTPUT_DIR / f'measure_indicator_{indicator_key}_rate.csv')
                df = df.replace(np.inf, np.nan)
                df = df[df['value'].notnull()]

                df = drop_irrelevant_practices(df)

                df['value'] = df['value']*1000

                df = get_practice_deciles(df, 'value')
                data = df[df['practice'] == int(practice_key)]


                percentile = data['percentile']
                percentile_array = np.array(percentile)
        
                plot_cusum(practice_value, f'cusum_indicator_{indicator_key}_{practice_key}.jpeg') 
                plot_median(percentile_array, practice_value, f'alerts_indicator_{indicator_key}_{practice_key}.jpeg')
                break
        