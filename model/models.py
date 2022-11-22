import pickle
import os
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_validate
from sklearn.model_selection import train_test_split

from prophet import Prophet
from data_retrieval.retrieve_data import retrieve_data

def log_regression(ticker_list):
  """"a function that based on the ticker creates a volume - return logistic regression
    ticker: Ticker should be in format XXX_XXX e.g. BTC_USDT
    """
    #create and import the data
    data_dict = retrieve_data(ticker_list)
    score_dict = {}


    for ticker in data_dict.keys():

        #returns the dataframe
        data = data_dict[ticker]


        #function that makes the return either 1, if it is above 0.005 and otherwise 0
        def return_log(df):
            if df["return"] >= 0.005:
                return 1
            else:
                return 0

        #function is then applied to the dataset
        data["return_log"] = data.apply(lambda df: return_log(df), axis =1 )

        #create a variable lagged volume, which is a shift of volume by 1
        data["lagged_vol"] = data["volume"].shift(1)

        #previous function creates a NaN, so we drop whole row
        data = data[1:]

        #define X and y
        X = data[["lagged_vol"]]
        y = data["return_log"]


        #split the data in train and test sets
        X_train, X_test, y_train, y_test =  train_test_split(X,y, test_size= 0.3, random_state=42)


        #define, train and score the model
        model = LogisticRegression()
        model.fit(X_train, y_train)
        score = model.score(X_test, y_test)
        score_dict[ticker] = score

        #eventually I think we should use a cross validate
        #cross_validate(model, X_train, y_train, cv = 5)

        #saving the trained model to disk, EVENTUALLY SHOULD MAKE FOLDER FOR TRAINED MODELS
        filename = 'trained_log_model'
        pickle.dump(model, open(filename, 'wb'))


    return score_dict



# def prophet(ticker_list):


if __name__ == "__main__":


    ticker_list = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
    print(f"\n{log_regression(ticker_list)}")
