import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import pickle
import numpy as np
import pandas as pd
import tensorflow as tf
keras = tf.keras

from sklearn.preprocessing import MinMaxScaler
from keras.layers import Bidirectional, Dropout, Activation, Dense, LSTM
# from tf.compat.v1.keras.layers import CuDNNLSTM
from keras.models import Sequential
from keras.optimizers import RMSprop

from data_retrieval.retrieve_data import retrieve_data


def to_sequences(data, seq_len):
    seq_lst = []

    for index in range(len(data) - seq_len):
        seq_lst.append(data[index: index + seq_len])

    return np.array(seq_lst)

def preprocess(data_raw, seq_len, train_split):

    data = to_sequences(data_raw, seq_len)

    num_train = int(train_split * data.shape[0])

    X_train = data[:num_train, :-1, :]
    y_train = data[:num_train, -1, :]

    X_test = data[num_train:, :-1, :]
    y_test = data[num_train:, -1, :]

    return X_train, y_train, X_test, y_test

def lstm_model_return(ticker_list):
    """
    a function that based on the ticker creates a LSTM deep learning model
    ticker: Ticker should be in format XXX_XXX e.g. BTC_USDT
    """

    # Create and import the data
    data_dict = retrieve_data(ticker_list)
    score_dict = {}

    for ticker in data_dict.keys():

        # Returns the dataframe
        data = data_dict[ticker]

        # Preprocesses the data
        scaler = MinMaxScaler()

        close_price = data["close"].values.reshape(-1, 1)

        scaled_close = scaler.fit_transform(close_price)
        scaled_close = scaled_close[~np.isnan(scaled_close)]
        scaled_close = scaled_close.reshape(-1, 1)

        # Splits the data in train and test sets
        seq_len = 100

        X_train, y_train, X_test, y_test =\
        preprocess(scaled_close, seq_len, train_split = 0.95)

        # Creates the model
        dropout = 0.2
        window_size = seq_len - 1

        model = Sequential()

        model.add(Bidirectional(
        LSTM(window_size, return_sequences=True),
        input_shape=(window_size, X_train.shape[-1])
        ))
        model.add(Dropout(rate=dropout))

        model.add(Bidirectional(
        LSTM((window_size * 2), return_sequences=True)
        ))
        model.add(Dropout(rate=dropout))

        model.add(Bidirectional(
        LSTM(window_size, return_sequences=False)
        ))

        model.add(Dense(units=1))

        model.add(Activation('linear'))

        # Trains the model
        opt = RMSprop(learning_rate=0.01)
        batch_size = 64

        model.compile(
            loss='mse',
            optimizer=opt,
            metrics=['mae']
        )

        history = model.fit(
            X_train,
            y_train,
            epochs=30,
            batch_size=batch_size,
            shuffle=False,
            validation_split=0.1
        )

        loss = model.evaluate(X_test, y_test)

        # predicts the returns over the selected period
        y_hat = model.predict(X_test)

        y_test_inv = scaler.inverse_transform(y_test)
        y_hat_inv = scaler.inverse_transform(y_hat)

        # Returns the model and parameters
        score_dict[ticker] = [model, history, loss, y_test_inv, y_hat_inv]

    return score_dict

# def lstm_model_update(ticker_list):
#     """
#     a function that based on the ticker updates a LSTM deep learning model
#     ticker: Ticker should be in format XXX_XXX e.g. BTC_USDT
#     """

#     # Create and import the data
#     data_dict = retrieve_data(ticker_list)
#     score_dict = {}

#     for ticker in ticker_list:

#         # Returns the dataframe
#         data = data_dict[ticker]
#         data = data.tail(300)

#         # Preprocesses the data
#         scaler = MinMaxScaler()

#         close_price = data["close"].values.reshape(-1, 1)

#         scaled_close = scaler.fit_transform(close_price)
#         scaled_close = scaled_close[~np.isnan(scaled_close)]
#         scaled_close = scaled_close.reshape(-1, 1)

#         # Splits the data in train and test sets
#         seq_len = 100

#         X_train, y_train, X_test, y_test =\
#         preprocess(scaled_close, seq_len, train_split = 0.95)

#         # Imports the current LSMT (return) model for the indicated ticker
#         model = pickle.load(open("TEST/TEST", "rb"))

#         # Trains the model
#         opt = RMSprop(learning_rate=0.0001)
#         batch_size = 64

#         model.compile(
#             loss='mse',
#             optimizer=opt,
#             metrics=['mae']
#         )

#         history = model.fit(
#             X_train,
#             y_train,
#             epochs=1,
#             batch_size=batch_size,
#             shuffle=False,
#             validation_split=0.1
#         )

#         loss = model.evaluate(X_test, y_test)

#         # predicts the returns over the selected period
#         y_hat = model.predict(X_test)

#         y_test_inv = scaler.inverse_transform(y_test)
#         y_hat_inv = scaler.inverse_transform(y_hat)

#         # Returns the model and parameters
#         score_dict[ticker] = [model, history, loss, y_test_inv, y_hat_inv]

#     return score_dict


if __name__ == "__main__":

    ticker_list = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
    print(f"\n{lstm_model_return(ticker_list)}")
