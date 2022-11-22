from fastapi import FastAPI
from model.models import log_regression

app = FastAPI()
ticker_list = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]

# Define a root `/` endpoint
@app.get('/')
def index():
    return {'ok': True}


@app.get('/predict')
def creating_model():
    score = log_regression(ticker_list)
    return score

if __name__=="__main__":
    creating_model()
