import pandas as pd
import os


def feature_calc():
    """This function calculates all the features used in the training
     """
    #define the path where to find the data_files

    files = os.listdir(os.path.abspath(".")+"/raw_data/ticker_data")
    path = os.path.abspath(".")+"/raw_data/ticker_data/"

    for ticker in files:
        #call up the csv data, index_col = 0 skips the first column
        data = pd.read_csv(f"raw_data/ticker_data/{ticker}",index_col = 0)

        #calculating different exponential weighted moving averages (12 day, 26 day and 50 day )
        data["12dayewm"] = data['close'].ewm(span=(12 * 24), adjust=False).mean()
        data["26dayewm"] = data['close'].ewm(span=(26 * 24), adjust=False).mean()
        data["50dayewm"] = data['close'].ewm(span=(50 * 24), adjust=False).mean()

        #TO_DO add more features here


        #write the csv back into the ticker_data folder
        columns = data.columns
        data.to_csv(f"{path}{ticker}", header=columns)
