import mlflow
import os

def mlflow_save(ticker, model, params, metrics):

    mlflow_tracking_uri = os.environ.get("MLFLOW_TRACKING_URI")
    mlflow_experiment = os.environ.get("MLFLOW_EXPERIMENT")
    mlflow_model_name = f'{os.environ.get("MLFLOW_MODEL_NAME")}_{ticker}'

    mlflow.set_tracking_uri(mlflow_tracking_uri)
    mlflow.set_experiment(experiment_name=mlflow_experiment)

    with mlflow.start_run():

        mlflow.log_params(params)
        mlflow.log_metrics(metrics)

        mlflow.keras.log_model(keras_model=model,
                            # artifact_path="model",
                            keras_module="tensorflow.keras",
                            registered_model_name=mlflow_model_name)

    return None

def mlflow_load(ticker):

    mlflow_tracking_uri = os.environ.get("MLFLOW_TRACKING_URI")
    mlflow.set_tracking_uri(mlflow_tracking_uri)

    mlflow_model_name = f'{os.environ.get("MLFLOW_MODEL_NAME")}_{ticker}'
    stage = "Production"
    model_uri = f"models:/{mlflow_model_name}/{stage}"

    model = mlflow.keras.load_model(model_uri=model_uri)

    return model
