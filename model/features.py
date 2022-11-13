import pandas as pd
import os
from data_retrieval.retrieve_data import retrieve_data
import datetime


def feature_calc():
    """This function calculates all the features used in the training
     """
    #first create clean data
    retrieve_data()

    #define the path where to find the data_files
    #clean this up later
    files = os.listdir(os.path.abspath(".")+"/raw_data/ticker_data")
    path = os.path.abspath(".")+"/raw_data/ticker_data/"

    for ticker in files:
        #call up the csv data, index_col = 0 skips the first column
        data = pd.read_csv(f"raw_data/ticker_data/{ticker}",index_col = 0)

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

        #TO_DO add more features here

        #write the csv back into the ticker_data folder
        columns = data.columns
        data.to_csv(f"{path}{ticker}", header=columns)

feature_calc()
