import pandas as pd
import csv
import os


def local_get_data(ticker:str) -> pd.DataFrame:

    """
    return the raw dataset from local disk
    """
    ticker = ticker.replace("/", "_")

    #selecting right path location of csv-file
    path = os.path.abspath(".")+f"/raw_data/ticker_data/{ticker}.csv"

    #reading data from csv file
    data = pd.read_csv(path, index_col = False)  # read all rows

    return data


def local_validate_data(ticker):
    validate = True
    ticker = ticker.replace("/", "_")
    data_dir = os.path.abspath("..")+ "/trading_tom/raw_data/ticker_data/"
    file_path = os.path.isfile(data_dir+ticker+".csv")

    if file_path == False:
       print(f"\nNo CSV present for: {ticker}")
       validate = False

   # CSV empty or only headers present
    try:
        with open(f"{data_dir + ticker}.csv", 'r') as csvfile:
            csv_dict = [row for row in csv.DictReader(csvfile)]
            if len(csv_dict) == 0:
                print(f"The CSV is empty: {ticker}")
                validate = False
    except:
       print(f"Preparing new build for: {ticker}")

    if validate is False and file_path == True:
        os.remove(f"{data_dir + ticker}.csv")

    return validate


def local_append_data(data:pd.DataFrame,ticker:str, columns:list):
    """
    append dataframe to local csv-file
    """
    ticker = ticker.replace("/", "_")

    #selecting right path location of csv-file
    path = os.path.abspath(".")+f"/raw_data/ticker_data/{ticker}"

    #writing data to local csv file
    print( f"Save data to {path}")
    data.to_csv(f"{path}.csv", mode='a', index=False, header=False)


def local_save_data(data:pd.DataFrame,ticker:str,columns:list):

    """
    save dataframe to local csv-file
    """
    ticker = ticker.replace("/", "_")

    #selecting right path location of csv-file
    path = os.path.abspath(".")+f"/raw_data/ticker_data/{ticker}"

    #writing data to local csv file
    print( f"\nSave data to {path}")
    data.to_csv(f"{path}.csv", header=columns, index=False)
