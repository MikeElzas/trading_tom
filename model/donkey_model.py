from data_retrieval.retrieve_data import retrieve_data
import random

# retrieve data
data = retrieve_data(100, "BTC/EUR", timeframe = "1h")
commision = 10

# return simple model
def donkey_model(data, commision):
    start = min(data['low'].tail())
    stop = max(data['high'].tail())

    prediction = random.randrange(start=start, stop=stop)
    prediction_adj = prediction - commision

    if prediction_adj > data['close'].iloc[-1]:
        return "buy"
    else:
        return "hold"

print(donkey_model(data, commision))

# ARIMA MODEL

# from statsmodels.tsa.stattools import adfuller
# from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# print('p-value zero-diff: ', adfuller(data['close'])[1])
# print('p-value zero-diff: ', adfuller(data['close'].diff().dropna())[1])
