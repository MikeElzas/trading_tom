import pandas as pd
import os
from datetime import datetime

def feature_calc(data):
    """This function calculates all the features used in the training
     """
    # Add time column to datetime
    data['datetime'] = data['time'].apply(lambda x: datetime.fromtimestamp(x / 1000).strftime('%Y-%m-%d %H:%M'))

    #calculating different exponential weighted moving averages (12 day, 26 day and 50 day )
    data["12dayewm"] = data['close'].ewm(span=(12 * 24), adjust=False).mean()
    data["26dayewm"] = data['close'].ewm(span=(26 * 24), adjust=False).mean()
    data["50dayewm"] = data['close'].ewm(span=(50 * 24), adjust=False).mean()

    #calculate the MACD
    data["MACD"] = data["12dayewm"] - data["26dayewm"]

    #calculate the OBV
    obv = 0
    data['obv'] = 0

    for i in range(len(data.index)):
        if i == 0:
            None
        elif data.iloc[i]['close'] > data.iloc[i-1]['close']:
            obv += data.iloc[i]['volume']
            data.loc[i, 'obv'] = obv
        elif data.iloc[i]['close'] < data.iloc[i-1]['close']:
            obv -= data.iloc[i]['volume']
            data.loc[i, 'obv'] = obv
        else:
            None

    #calculate the OBV_EMA
    data['obv_ema'] = data['obv'].ewm(span=(12 * 24), adjust=False).mean()

    # Calculate the return for a give period
    data['return'] = data['close'].pct_change()

    #TO_DO add more features here

    return data
