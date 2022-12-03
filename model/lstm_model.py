import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import pickle
import numpy as np
import pandas as pd
import tensorflow as tf
import mlflow

keras = tf.keras

from sklearn.preprocessing import MinMaxScaler
from keras.callbacks import EarlyStopping
from keras.layers import Bidirectional, Dropout, Activation, Dense, LSTM
from keras.models import Sequential
from keras.optimizers import RMSprop

from data_retrieval.retrieve_data import retrieve_data
from model_upload.mlflow import mlflow_save, mlflow_load


def to_sequences(data, seq_len):
    seq_lst = []

    for index in range(len(data) - seq_len):
        seq_lst.append(data[index: index + seq_len])

    return np.array(seq_lst)

def preprocess(data_raw, seq_len, train_split):

    data = to_sequences(data_raw, seq_len)

    num_train = int(train_split * data.shape[0])

    X_train = data[:num_train, :-1, :]
    y_train = data[:num_train, -1, 0]

    X_test = data[num_train:, :-1, :]
    y_test = data[num_train:, -1, 0]

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

        close_price = data[["close"]].values.reshape(-1, 1)

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
        es = EarlyStopping(patience=5, restore_best_weights=True)

        model.compile(
            loss='mse',
            optimizer=opt,
            metrics=['mae']
        )

        history = model.fit(
            X_train,
            y_train,
            epochs=50,
            batch_size=batch_size,
            callbacks=[es],
            shuffle=False,
            validation_split=0.1
        )

        loss = model.evaluate(X_test, y_test)

        # predicts the returns over the selected period
        y_hat = model.predict(X_test)

        y_test_inv = scaler.inverse_transform(y_test.reshape(-1, 1))
        y_hat_inv = scaler.inverse_transform(y_hat)

        # Returns the model and parameters
        score_dict[ticker] = [model, history, loss, y_test_inv, y_hat_inv]

    return score_dict

def lstm_model_new(ticker_list):
    """
    a function that based on the ticker creates a LSTM deep learning model
    ticker: Ticker should be in format XXX_XXX e.g. BTC_USDT
    """

    # Create and import the data
    data_dict = retrieve_data(ticker_list)
    score_dict = {}

    for ticker in data_dict.keys():

        # Returns the dataframe
        data = data_dict[ticker].head(1000)

        # Preprocesses the data
        scaler = MinMaxScaler()
        scaler_close = MinMaxScaler()

        data_set = data[["volume", "MACD", "obv_ema"]].values.reshape(-1, 1)
        data_close = data[["close"]].values.reshape(-1, 1)

        scaled_data_set = scaler.fit_transform(data_set)
        scaled_data_set = scaled_data_set[~np.isnan(scaled_data_set)]
        scaled_data_set = scaled_data_set.reshape(-1, 3)

        scaled_data_close = scaler_close.fit_transform(data_close)
        scaled_data_close = scaled_data_close[~np.isnan(scaled_data_close)]
        scaled_data_close = scaled_data_close.reshape(-1, 1)

        scaled_data = np.concatenate([scaled_data_close, scaled_data_set], axis=1)

        # Splits the data in train and test sets
        seq_len = 100

        X_train, y_train, X_test, y_test =\
        preprocess(scaled_data, seq_len, train_split = 0.95)

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
        learning_rate=0.01
        opt = RMSprop(learning_rate=learning_rate)
        batch_size = 256 #64
        es = EarlyStopping(patience=5, restore_best_weights=True)

        model.compile(
            loss='mse',
            optimizer=opt,
            metrics=['mae']
        )

        history = model.fit(
            X_train,
            y_train,
            epochs=1,
            batch_size=batch_size,
            callbacks=[es],
            shuffle=False,
            validation_split=0.1
        )

        test_eval = model.evaluate(X_test, y_test)

        # predicts the returns over the selected period
        y_hat = model.predict(X_test)

        y_test_inv = scaler_close.inverse_transform(y_test.reshape(-1, 1))
        y_hat_inv = scaler_close.inverse_transform(y_hat)

        # saves to MLFLOW
        params = dict(learning_rate=learning_rate,
                      batch_size=batch_size,
                      seq_len=seq_len)

        metrics = dict(train_mse=history.history['loss'],
                       val_mse=history.history['val_loss'],
                       test_mse=test_eval[0],
                       train_mae=history.history['mae'],
                       val_mae=history.history['val_mae'],
                       test_mae=test_eval[1])

        # mlflow_save(ticker, model, params, metrics)

        # Returns the model and parameters
        score_dict[ticker] = [model, y_test_inv, y_hat_inv]

    return score_dict

def lstm_model_update(ticker_list):
    """
    a function that based on the ticker updates a LSTM deep learning model
    ticker: Ticker should be in format XXX_XXX e.g. BTC_USDT
    """

    # Create and import the data
    data_dict = retrieve_data(ticker_list)
    score_dict = {}

    for ticker in ticker_list:

        # Returns the dataframe
        data = data_dict[ticker]

        # Preprocesses the data
        scaler = MinMaxScaler()
        scaler_close = MinMaxScaler()

        data_set = data[["volume", "MACD", "obv_ema"]]
        data_close = data[["close"]]

        scaled_data_set = scaler.fit_transform(data_set)
        scaled_data_set = scaled_data_set[~np.isnan(scaled_data_set)]
        scaled_data_set = scaled_data_set.reshape(-1, 3)

        scaled_data_close = scaler_close.fit_transform(data_close)
        scaled_data_close = scaled_data_close[~np.isnan(scaled_data_close)]
        scaled_data_close = scaled_data_close.reshape(-1, 1)

        scaled_data = np.concatenate([scaled_data_close, scaled_data_set], axis=1)

        seq_len = 100

        data_new = to_sequences(scaled_data, seq_len)[-24:, :]

        X_train = data_new[:18, :-1, :]
        y_train = data_new[:18, -1, 0]

        X_test = data_new[18:, :-1, :]
        y_test = data_new[18:, -1, 0]

        # Imports the current LSMT (return) model for the indicated ticker
        model = mlflow_load(ticker)

        # Trains old model on new data
        test_eval_old = model.evaluate(X_test, y_test)
        test_mse_old = test_eval_old[0]
        test_mae_old = test_eval_old[1]

        # Trains the model
        learning_rate=0.0001
        opt = RMSprop(learning_rate=learning_rate)
        batch_size = 64

        model.compile(
            loss='mse',
            optimizer=opt,
            metrics=['mae']
        )

        history = model.fit(
            X_train,
            y_train,
            epochs=1,
            batch_size=batch_size,
            shuffle=False,
            validation_split=0.1
        )

        test_eval = model.evaluate(X_test, y_test)

        # predicts the returns over the selected period
        y_hat = model.predict(X_test)

        y_test_inv = scaler.inverse_transform(y_test)
        y_hat_inv = scaler.inverse_transform(y_hat)

        # saves to MLFLOW
        params = dict(learning_rate=learning_rate,
                      batch_size=batch_size,
                      seq_len=seq_len)

        metrics = dict(train_mse=history.history['loss'],
                       val_mse=history.history['val_loss'],
                       test_mse=test_eval[0],
                       train_mae=history.history['mae'],
                       val_mae=history.history['val_mae'],
                       test_mae=test_eval[1],
                       test_mse_old=test_mse_old,
                       test_mae_old=test_mae_old)

        mlflow_save(ticker, model, params, metrics)

        # Returns the model and parameters
        score_dict[ticker] = [model, y_test_inv, y_hat_inv]

    return score_dict


if __name__ == "__main__":

    ticker_list = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
    print(f"\n{lstm_model_new(ticker_list)}")
    # print(f"\n{lstm_model_update(ticker_list)}")
