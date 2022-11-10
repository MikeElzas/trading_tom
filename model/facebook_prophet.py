import pandas as pd
from data_retrieval.retrieve_data import retrieve_data
from datetime import timedelta, datetime
from fbprophet import Prophet

data = retrieve_data()

# Temp read csv // Need to read csv from ticker_data
df = pd.read_csv('/Users/davidlewagon/code/David3-8/taxifare-website/trading_tom/raw_data/ticker_data/BTC_USDT.csv')

# Temp: This is fixed in retrieve_data.py
df['time'] = df['time'].apply(lambda x : datetime.fromtimestamp(x/1000).strftime('%Y-%m-%d %H:%M'))

# Split: Split for hour vs day vs month vs year checks
df['Year'] = df['time'].apply(lambda x: str(x)[:4])
df['Month'] = df['time'].apply(lambda x: str(x)[5:7])
df['Day'] = df['time'].apply(lambda x: str(x)[8:10])
df['Hour'] = df['time'].apply(lambda x: str(x)[-4:])

#Restructure Data if necessary // Can be done with 'time' column, need to test.
df['ds'] = pd.DatetimeIndex(df['Year']+'-'+df['Month']+'-'+df['Day'])



df = df.loc
df.drop(['Time Date', 'Close', 'Year', 'Month', 'Day'], axis=1, inplace=True)
df.columns = ['y', 'ds']

m = Prophet(interval_width=0.95, daily_seasonality=True)
model = m.fit(df)

future = m.make_future_dataframe(periods=100,freq='D')
forecast = m.predict(future)
forecast.head()


#https://facebook.github.io/prophet/docs/quick_start.html


print(df)