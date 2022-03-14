import psycopg2

import app
from config import BaseConfig
from dash import dcc, html, Dash, dash
import plotly.express as px
from dash.dependencies import Input, Output
import pandas as pd

from ..models import Stock_price


def register_callbacks(dashapp):
    @dashapp.callback(
        Output(component_id='stock_graph', component_property='figure'),
        Input(component_id='stock_dropdown', component_property='value')
    )

    def update_stock_graph(company):
        price_df = pd.DataFrame(columns=["trade_date", "close"])
        date_1='2021-06-01'
        date_2='2022-03-08'
        result=Stock_price.query.with_entities(Stock_price.trade_date, Stock_price.close).filter(
            Stock_price.name==company, Stock_price.trade_date.between(date_1,date_2)
        )
        price_df["trade_date"] = [x[0] for x in result]
        price_df["close"] = [x[1] for x in result]
        fig = px.line(data_frame=price_df, x="trade_date", y="close", title=str(company))
        return fig
