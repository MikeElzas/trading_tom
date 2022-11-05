from data_retrieval.retrieve_data import retrieve_data
from random import randrange
import pandas as pd
import os

# retrieve data
ticker_list = retrieve_data()
ticker = 0
check = ticker_list[ticker].replace("/", "_")

data_dir = os.path.abspath("..")+ "/trading_tom/raw_data/ticker_data/"
data = pd.read_csv(f"{data_dir}{check}.csv", header=0)
data.drop(columns = "Unnamed: 0", inplace=True)

# inputs donkey model
commision = 0
donkey_basis = 4

# return donkey prediction
def donkey_model(data, commision, donkey_basis):
    start = min(data['low'].tail(donkey_basis))
    stop = max(data['high'].tail(donkey_basis))

    prediction = randrange(start=int(start), stop=int(stop))
    prediction_adj = prediction - commision

    if prediction_adj > data['close'].iloc[-1]:
        return "buy"
    else:
        return "hold"

# validate donkey prediction
def donkey_validate(data, commision, donkey_basis):

    data['y_result'] = (data['close'] - commision) - data['close'].shift(1)
    data['y_true'] = data['y_result'].apply(lambda x: "buy" if x > 0 else "hold")

    donkey_data = data.iloc[donkey_basis:,:].copy()

    donkey_lst = [donkey_model(data.head(row), commision, donkey_basis)
                  for row in range(len(data)) if row > donkey_basis - 1]

    donkey_data['y_pred'] = donkey_lst
    donkey_data['y_score'] = (donkey_data['y_pred'] == donkey_data['y_true'])

    score = donkey_data['y_score'].sum() / len(data)
    result = int(sum(donkey_data['y_result'][donkey_data['y_pred'] == "buy"]))

    def outcome():
        if result > 0:
            return 'gain'
        else:
            return 'lose'

    result_txt = outcome()

    return f'The accuracy of the donkey model is {round(score, 2)}\nYou will {result_txt} USD {abs(result)} when you pay a commision of USD {commision} per trade'

print(donkey_validate(data, commision, donkey_basis))
