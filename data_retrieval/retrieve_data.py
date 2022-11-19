import ccxt
import pandas as pd
import os
import csv

from datetime import datetime
from data_retrieval.big_query import cloud_get_data, cloud_save_data, cloud_validate_data, cloud_append_data
from data_retrieval.local_disk import local_get_data, local_save_data, local_validate_data, local_append_data
from model.features import feature_calc


def retrieve_data(ticker_list):
    """
    this function is used to retrieve data from FTX.
    """

    columns = ["time", "open", "high", "low", "close", "volume"]
    # ticker_list = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
    exchange = ccxt.binance()
    start_ts = exchange.parse8601('2021-01-01 00:00:00')
    data_dict = {}

    # Retrieve data from the exchange
    for ticker in ticker_list:
        check = ticker.replace("/", "_")

        # Validate the data, return data & bool
        if os.environ.get('DATA_SOURCE') == 'local':
            validate = local_validate_data(ticker)
            if validate == True:
                data = local_get_data(ticker)
                data = update_data(data,ticker,exchange,columns)

                local_append_data(data,ticker,columns)

                data = local_get_data(ticker)

            else: data = write_data(ticker, exchange, columns, start_ts)

        elif os.environ.get('DATA_SOURCE') == 'cloud':
            validate = cloud_validate_data(ticker)
            if validate == True:
                data = cloud_get_data(ticker)

                data = update_data(data,ticker,exchange,columns)

                cloud_append_data(data,ticker)

                data = cloud_get_data(ticker)

            else: data = write_data(ticker, exchange, columns, start_ts)

        else:
            raise ValueError(f"Value in .env{os.environ.get('DATA_SOURCE')} is unknown")

        data_dict[ticker] = data

    return data_dict


def update_data(data, ticker, exchange, columns):

    last_date = int(data["time"].max())
    data = data[data['time']!=last_date]

    ohlcv = exchange.fetch_ohlcv(ticker, '1h', since=last_date, limit=1000)
    ohlcv_list = ohlcv.copy()

    while (len(ohlcv) == 1000):
        from_ts = ohlcv[-1][0]
        ohlcv.clear()
        ohlcv = exchange.fetch_ohlcv(ticker, '1h', since=from_ts, limit=1000)
        ohlcv_list.extend(ohlcv)

    ohlcv_list = pd.DataFrame(ohlcv_list, columns=columns)

    data = feature_calc(ohlcv_list)
    last_date2 = datetime.fromtimestamp(last_date/ 1000).strftime('%Y-%m-%d %H:%M')

    print(f"\nUpdated data for {ticker} per {last_date2}")
    return data


def write_data(ticker, exchange, columns, start_ts):
    ohlcv = exchange.fetch_ohlcv(ticker, '1h', since=start_ts, limit=1000)
    ohlcv_list = ohlcv.copy()

    while (len(ohlcv) == 1000):
        from_ts = ohlcv[-1][0]
        ohlcv.clear()
        ohlcv = exchange.fetch_ohlcv(ticker, '1h', since=from_ts, limit=1000)
        ohlcv_list.extend(ohlcv)
        data = ohlcv_list

    ohlcv = pd.DataFrame(data, columns=columns)
    ticker = ticker.replace("/", "_")

    data = feature_calc(ohlcv)
    data = data[1:]
    columns = data.columns

    #save data based on data_source type
    if os.environ.get('DATA_SOURCE') == 'local':
        local_save_data(data,ticker,columns)

    elif os.environ.get('DATA_SOURCE') == 'cloud':
        cloud_save_data(data,ticker)

    else:
        raise ValueError(f"Value in .env{os.environ.get('DATA_SOURCE')} is unknown")

    print(f"Building new CSV for: {ticker}")

    return data


if __name__ == "__main__":

    ticker_list = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
    retrieve_data(ticker_list)
