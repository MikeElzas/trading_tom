import pandas as pd
from data_retrieval.retrieve_data import retrieve_data
from datetime import timedelta, datetime
from matplotlib import pyplot
from prophet import Prophet



def fbprophet(retrieve_data):
    data = retrieve_data()

    print(data)
    # df['ds'] = pd.DatetimeIndex(df['Year']+'-'+df['Month']+'-'+df['Day'])
