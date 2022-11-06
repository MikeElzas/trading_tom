from data_retrieval.retrieve_data import retrieve_data
import pandas as pd
from sklearn.linear_model import LogisticRegression

#update to latest data
retrieve_data()

#function that trains a logistic regression

def log_regression(ticker):
    #import the data, this should become a relative path
    data =pd.read_csv(f"raw_data/ticker_data/{ticker}.csv")
    data.drop(columns = "Unnamed: 0",inplace = True)

    #calculate the return for a given period
    data["return"] = data["close"].pct_change()
    #first value is a NaN so set to zero
    data["return"].iloc[0] = 0

    #function that makes the return either 1, if it is above 0.005 and otherwise 0
    def return_log(df):
        if df["return"] >= 0.005:
            return 1
        else:
            return 0

    #function is then applied to the dataset
    data["return_log"] = data.apply(lambda df: return_log(df), axis =1 )

    #setting data to use in regression
    #currently we are using volume, but I think this should be lagged volume by 1 want we want to use previous period volume to predict close
    X = data[["volume"]]
    y = data["return_log"]

    model = LogisticRegression()
    model.fit(X,y)

    #saving the trained model to disk, EVENTUALLY SHOULD MAKE FOLDER FOR TRAINED MODELS
    filename = 'trained_log_model'
    pickle.dump(model, open(filename, 'wb'))

    return model
