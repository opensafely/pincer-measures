from utilities import get_practice_deciles
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from utilities import OUTPUT_DIR, drop_irrelevant_practices
from study_definition import indicators_list
import os

if not (OUTPUT_DIR / 'cusum').exists():
    os.mkdir(OUTPUT_DIR / 'cusum')

def compute_deciles(
    measure_table, values_col, has_all_percentiles=True
):
    """Computes deciles.
    Args:
        measure_table: A measure table.
        groupby_col: The name of the column to group by.
        values_col: The name of the column for which deciles are computed.
        has_outer_percentiles: Whether to compute the nine largest and nine smallest
            percentiles as well as the deciles.
    Returns:
        A data frame with `groupby_col`, `values_col`, and `percentile` columns.
    """
    quantiles = np.arange(0.1, 1, 0.1)
    if has_all_percentiles:
        quantiles = np.arange(0.01, 1, 0.01)

    percentiles = (
        measure_table.groupby(['date'])[values_col]
        .quantile(pd.Series(quantiles, name="percentile"))
        .reset_index()
        
    )
    
    percentiles["percentile"] = percentiles["percentile"] * 100
    return percentiles


class CUSUM(object):
    """See Introduction to Statistical Quality Control, Montgomery DC, Wiley, 2009
    and our paper
    http://dl4a.org/uploads/pdf/581SPC.pdf
    """

    def __init__(self, data, window_size=12, sensitivity=5, name=""):
        data = np.array([np.nan if x is None else x for x in data])
        # Remove sufficient leading nulls to ensure we can start with
        # any value
        self.start_index = 0
        while pd.isnull(data[self.start_index : self.start_index + window_size]).all():
            if self.start_index > len(data):
                data = []
                break
            self.start_index += 1
        self.data = data
        self.window_size = window_size
        self.sensitivity = sensitivity
        self.current_cusum = []
        self.pos_cusums = []
        self.neg_cusums = []
        self.target_means = []
        self.alert_thresholds = []
        self.alert_indices = []
        self.pos_alerts = []
        self.neg_alerts = []
        self.name = name

    def work(self):
        for i, datum in enumerate(self.data):
            if i <= self.start_index:
                window = self.data[i : self.window_size + i]
                self.new_target_mean(window)
                self.new_alert_threshold(window)
                self.compute_cusum(datum, reset=True)
            elif self.cusum_within_alert_threshold():
                # Note this will always be true for the first `window_size`
                # data points
                self.maintain_target_mean()
                self.maintain_alert_threshold()
                self.compute_cusum(datum)
            else:
                # Assemble a moving window of the last `window_size`
                # non-null values
                window = self.data[i - self.window_size : i]
                self.new_target_mean(window)
                if self.moving_in_same_direction(datum):  # this "peeks ahead"
                    self.maintain_alert_threshold()
                    self.compute_cusum(datum)
                else:
                    self.new_alert_threshold(window)  # uses window
                    self.compute_cusum(datum, reset=True)
            # Record alert
            self.record_alert(datum, i)
        return self.as_dict()

    def as_dict(self):
        return {
            "smax": self.pos_cusums,
            "smin": self.neg_cusums,
            "target_mean": self.target_means,
            "alert_threshold": self.alert_thresholds,
            "alert": self.alert_indices,
            "alert_percentile_pos": self.pos_alerts,
            "alert_percentile_neg": self.neg_alerts,
        }

    
    def moving_in_same_direction(self, datum):
        # Peek ahead to see what the next CUSUM would be
        next_pos_cusum, next_neg_cusum = self.compute_cusum(datum, store=False)
        going_up = (
            next_pos_cusum > self.current_pos_cusum()
            and self.cusum_above_alert_threshold()
        )
        going_down = (
            next_neg_cusum < self.current_neg_cusum()
            and self.cusum_below_alert_threshold()
        )
        return going_up or going_down

    def __repr__(self):
        return """
        name:             {name}
        data:             {data}
        pos_cusums:       {pos_cusums}
        neg_cusums:       {neg_cusums}
        target_means:     {target_means}
        alert_thresholds: {alert_thresholds}"
        alert_incides:    {alert_indices}"
        """.format(
            **self.__dict__
        )

    def record_alert(self, datum, i):
        if self.cusum_above_alert_threshold():
            self.alert_indices.append(i)
            self.pos_alerts.append(datum)
            self.neg_alerts.append(None)
        elif self.cusum_below_alert_threshold():
            self.alert_indices.append(i)
            self.pos_alerts.append(None)
            self.neg_alerts.append(datum)
        else:
            self.pos_alerts.append(None)
            self.neg_alerts.append(None)

    def maintain_alert_threshold(self):
        self.alert_thresholds.append(self.alert_thresholds[-1])
        return self.alert_thresholds[-1]

    def maintain_target_mean(self):
        self.target_means.append(self.target_means[-1])
        return self.target_means[-1]

    def cusum_above_alert_threshold(self):
        return self.pos_cusums[-1] > self.alert_thresholds[-1]

    def cusum_below_alert_threshold(self):
        return self.neg_cusums[-1] < -self.alert_thresholds[-1]

    def cusum_within_alert_threshold(self):
        return not (
            self.cusum_above_alert_threshold() or self.cusum_below_alert_threshold()
        )

    def new_target_mean(self, window):
        self.target_means.append(np.nanmean(window))

    def new_alert_threshold(self, window):
        self.alert_thresholds.append(np.nanstd(window * self.sensitivity))

    def current_pos_cusum(self):
        return self.pos_cusums[-1]

    def current_neg_cusum(self):
        return self.neg_cusums[-1]

    def compute_cusum(self, datum, reset=False, store=True):
        alert_threshold = self.alert_thresholds[-1]
        delta = 0.5 * alert_threshold / self.sensitivity
        current_mean = self.target_means[-1]
        cusum_pos = datum - (current_mean + delta)
        cusum_neg = datum - (current_mean - delta)
        if not reset:
            cusum_pos += self.pos_cusums[-1]
            cusum_neg += self.neg_cusums[-1]
        cusum_pos = round(max(0, cusum_pos), 2)
        cusum_neg = round(min(0, cusum_neg), 2)
        if store:
            self.pos_cusums.append(cusum_pos)
            self.neg_cusums.append(cusum_neg)
        return cusum_pos, cusum_neg
    

demographics = ["age_band", "sex", "region", "imd", "care_home_type"]

cusum_results = {}

#these are not generated in the main generate measures action
additional_indicators = ["e","f", "li"]
indicators_list.extend(additional_indicators)

num_alerts = {}


for i in indicators_list:
    num_alerts[i] = {}
    num_alerts[i]['positive'] = 0
    num_alerts[i]['negative'] = 0
    num_alerts[i]['any'] = 0

    df = pd.read_csv(OUTPUT_DIR / f'measure_indicator_{i}_rate.csv')
    dates = df['date'].unique()
    for date in dates:
        num_alerts[i][date] = 0

    df = df.replace(np.inf, np.nan)
    
    df = df[df['value'].notnull()]

    df = drop_irrelevant_practices(df)

    df['value'] = df['value']*1000

    df = get_practice_deciles(df, 'value')
    
    
    cusum_results[i] = {}
    for practice in df['practice'].unique():
        data = df[df['practice'] == practice]

    
        percentile = data['percentile']
        percentile_array = np.array(percentile)
        
        cs = CUSUM(data= percentile_array, window_size=6)
        results = cs.work()

        alert=False

        if len(results['alert']) >0:
            for alert in results['alert']:
                date = dates[alert]
                num_alerts[i][date] +=1


        # if there is a value in positive alerts add 1 to count and positive count
        if not all(i is None for i in results['alert_percentile_pos']):
            num_alerts[i]['positive'] +=1
            alert=True
        
        # if there is a value in positive alerts add 1 to count and positive count
        if not all(i is None for i in results['alert_percentile_neg']):
            num_alerts[i]['negative'] +=1
            alert=True

        if alert:

            num_alerts[i]['any'] +=1

            


        cusum_results[i][str(practice)] = results
        


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


with open(OUTPUT_DIR / 'cusum/cusum_results.json', 'w') as f:
    json.dump(cusum_results, f,  cls=NpEncoder)

with open(OUTPUT_DIR / 'cusum/cusum_alerts_summary.json', 'w') as f:
    json.dump(num_alerts, f,  cls=NpEncoder)