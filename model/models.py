from data_retrieval.retrieve_data import retrieve_data
import pandas as pd
from sklearn.linear_model import LogisticRegression
import pickle
from sklearn.model_selection import cross_validate
from sklearn.model_selection import train_test_split


#update to latest data


def log_regression(ticker):
    """"a function that based on the ticker creates a volume - return logistic regression
    ticker: Ticker should be in format XXX_XXX e.g. BTC_USDT
    """
    #always ensure latest data is present
    retrieve_data()

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

    #eventually I think we should use a cross validate
    #cross_validate(model, X_train, y_train, cv = 5)

    #saving the trained model to disk, EVENTUALLY SHOULD MAKE FOLDER FOR TRAINED MODELS
    filename = 'trained_log_model'
    pickle.dump(model, open(filename, 'wb'))

    return score
