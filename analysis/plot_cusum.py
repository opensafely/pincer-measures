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
        plt.ylabel('Percentile')
        plt.xlabel('date')
        plt.xticks(ticks = [i for i in range(len(data['date']))], labels = data['date'].values, rotation=90)
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / f'cusum/cusum/{filename}')
        plt.clf()

def plot_median(array, results, filename):
        
        plt.figure(figsize=(15,8))
        plt.plot(array)
        plt.plot(results['target_mean'], color='red')
        plt.ylabel('Percentile')
        plt.xlabel('date')
        plt.xticks(ticks = [i for i in range(len(data['date']))], labels = data['date'].values, rotation=90)
            
        for i in results['alert']:
            plt.scatter(x=i, y=array[i], color='green', s=50)
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / f'cusum/alerts/{filename}')
        plt.clf()



if not (OUTPUT_DIR / 'cusum').exists():
    os.mkdir(OUTPUT_DIR / 'cusum')

if not (OUTPUT_DIR / 'cusum/cusum').exists():
    os.mkdir(OUTPUT_DIR / 'cusum/cusum')

if not (OUTPUT_DIR / 'cusum/alerts').exists():
    os.mkdir(OUTPUT_DIR / 'cusum/alerts')
 

with open(OUTPUT_DIR / 'cusum/cusum_results.json') as file:
    # Load its content and make a new dictionary
    data = json.load(file)
    
    for indicator_key, indicator_value in data.items():
        
       
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
        

fig, axs = plt.subplots(7, 2)
x = np.arange(0, 7, 1)
y = np.arange(0, 2, 1)
axs_list = [(i, j) for i in x for j in y]
fig, axs = plt.subplots(7, 2, figsize=(30,20), sharex='col')

z=0
with open(OUTPUT_DIR / 'cusum/cusum_alerts_by_date.json') as file:
    data = json.load(file)
    
    for indicator_key in data['positive'].keys():
        
        df_pos = pd.DataFrame.from_dict(data['positive'][indicator_key], orient='index', columns=['count']).reset_index()
        df_pos = df_pos.sort_values(['index'])
        
        df_neg = pd.DataFrame.from_dict(data['negative'][indicator_key], orient='index', columns=['count']).reset_index()
        df_neg = df_neg.sort_values(['index'])
    
        
        axs[axs_list[z]].plot(df_pos['index'], df_pos['count'], color='red')
        
        axs[axs_list[z]].plot(df_neg['index'], df_neg['count'], color='cyan')
        axs[axs_list[z]].set_title(f'Indicator {indicator_key}', size=20)
        axs[axs_list[z]].set_ylabel('Count', size=14)
        z+=1
        
plt.gcf().autofmt_xdate(rotation=90)
fig.legend(['Positive', 'Negative'], loc='upper right', bbox_to_anchor=(1.0, 0.8), prop={'size': 20})

fig.savefig('output/cusum/combined_cusum_count.png')