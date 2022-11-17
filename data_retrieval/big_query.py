from google.cloud import bigquery
from google.cloud.exceptions import NotFound

import pandas as pd

import os

client = bigquery.Client()
PROJECT_ID = os.environ.get("PROJECT_ID")
DATASET = os.environ.get("DATASET")

def cloud_get_data(ticker:str):
    """
    load data from BigQuery
    """

    check = ticker.replace("/", "_")

    dataset_ref = bigquery.DatasetReference(PROJECT_ID, DATASET)
    table_ref = dataset_ref.table(check)
    table = client.get_table(table_ref)

    #converting table into pd.dataframe
    data = client.list_rows(table).to_dataframe()

    return data

def cloud_validate_data(ticker:str):
    validate = True
    ticker = ticker.replace("/", "_")

    dataset_ref = bigquery.DatasetReference(PROJECT_ID, DATASET)
    table_ref = dataset_ref.table(ticker)

    try:
        client.get_table(table_ref)
    except NotFound:
        print("Table {} is not found.".format(table_ref))
        validate = False

    #if validate is False and file_path == True:
    #    client.delete_table(table_ref, not_found_ok=True)

    return validate


def cloud_save_data(data:pd.DataFrame,ticker:str):
    """
    save dataframe to BigQuery based on a pd.dataframe and a ticker
    """
    check = ticker.replace("/", "_")

    dataset_ref = bigquery.DatasetReference(PROJECT_ID, DATASET)
    table_ref = dataset_ref.table(check)

    # bq requires str columns starting with a letter or underscore
    data.columns = [f"_{column}" if type(column) != str else column for column in data.columns]

    # define write mode and schema
    write_mode = "WRITE_TRUNCATE" #if is_first else "WRITE_APPEND"
    job_config = bigquery.LoadJobConfig(write_disposition=write_mode)

    # load data
    job = client.load_table_from_dataframe(data, table_ref, job_config=job_config)
    result = job.result()
