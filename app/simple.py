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
def predict(lagged_vol: float,
            ewma: float):
    model = pickle.load(open("app/trained_log_model.pkl", "rb"))
    X_pred = pd.DataFrame({"lagged_vol" : [float(lagged_vol)]
                           }, index = [0])
    var, = model.predict(X_pred)
    var = int(var)
    return {'pred': var}

if __name__=="__main__":
    predict()
