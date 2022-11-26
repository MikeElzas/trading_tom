from fastapi import FastAPI
import pickle
import pandas as pd
import numpy as np

app = FastAPI()
ticker_list = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]

# Define a root `/` endpoint
@app.get('/')
def index():
    return {'ok': True}


@app.get('/predict')
def predict():
    model = pickle.load(open("app/trained_log_model.pkl", "rb"))
    data = dict({"lagged_vol": [1544256894.22]})
    X = pd.DataFrame(data = data)
    var, = model.predict(X)
    var=int(var)
    return {'pred': var}

if __name__=="__main__":
    predict()
