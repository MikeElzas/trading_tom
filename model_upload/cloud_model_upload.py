from google.cloud import storage
import os
import pickle
from model.models import log_regression

def save_cloud_model(score_dict, ticker_list):
    client = storage.Client()
    ticker_list = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
    for ticker in ticker_list:
        model = score_dict[ticker]
        bucket = client.bucket(os.environ.get('BUCKET_NAME'))
        pickle_upload = pickle.dumps(model)
        check = ticker.replace("/", "_")
        blob = bucket.blob(f'{check}.pickle')
        blob.upload_from_string(pickle_upload)
        print(f'{ticker} model saved in cloud')


if __name__ == "__main__":

    ticker_list = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
    save_cloud_model(log_regression(ticker_list),ticker_list)
