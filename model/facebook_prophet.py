import pandas as pd
from data_retrieval.retrieve_data import retrieve_data
from prophet import Prophet



def fbprophet(ticker_list):

    data_dict = retrieve_data(ticker_list)
    fig_dict = {}

    for ticker in ticker_list:

        data = data_dict[ticker]
        data = data.rename(columns={'datetime': 'ds', 'close':'y'})
        df = data[['ds', 'y']]

        model = Prophet(changepoint_prior_scale=0.3).fit(df)

        # future = model.make_future_dataframe(periods=300, freq='H')
        # fcst = model.predict(future)
        # fig = m.plot(fcst)
        # fig2 = m.plot_components(fcst)

        fig_dict[ticker] = model

    return fig_dict


if __name__ == "__main__":

    ticker_list = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
    print(f"\n{fbprophet(ticker_list)}")
