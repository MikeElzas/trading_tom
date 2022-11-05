from data_retrieval.retrieve_data import retrieve_data
import datetime
import pandas as pd
import plotly.graph_objects as go

data = retrieve_data(100, "BTC/EUR", timeframe = "1h")

fig = go.Figure(data=[go.Candlestick(x=data["time"], open=data['open'], high=data['high'], low=data['low'], close=data['close'])])

fig.update_layout(
    yaxis_title='Prices',
    font=dict(
        family="Arial",
        size=14,
        color="MidnightBlue"
    )
)
fig.show()
