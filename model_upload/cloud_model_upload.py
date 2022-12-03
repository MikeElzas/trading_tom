from google.cloud import storage
import os
import pickle
from model.lstm_model import lstm_model_new
from google.oauth2.service_account import Credentials

def save_cloud_model(ticker_list):
    credentials = Credentials.from_service_account_file(os.path.abspath(".") + f"/trading-tom.json")
    client = storage.Client(credentials=credentials)
    score_dict = lstm_model_new(ticker_list)

    for ticker in ticker_list:
        model_info = score_dict[ticker]
        bucket = client.bucket(os.environ.get('BUCKET_NAME'))
        pickle_upload = pickle.dumps(model_info)
        check = ticker.replace("/", "_")
        blob = bucket.blob(f'{check}.pickle')
        blob.upload_from_string(pickle_upload)
        print(f'{ticker} model info saved in cloud')


if __name__ == "__main__":

    ticker_list = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
    save_cloud_model(ticker_list)
