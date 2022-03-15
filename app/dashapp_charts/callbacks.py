import psycopg2

import app
from config import BaseConfig
from dash import dcc, html, Dash, dash
import dash
import plotly.express as px
from dash.dependencies import Input, Output, State
import pandas as pd

from ..models import Stock_price


def register_callbacks(dashapp):
    @dashapp.callback(
        Output(component_id='stock_graph', component_property='figure'),
        [Input('show','n_clicks')],
        [State('stock_dropdown','value'),
        State(component_id='start_date', component_property='date'),
        State(component_id='end_date', component_property='date')]


    )

    def update_stock_graph(n_clicks, company, start_date, end_date):

        if n_clicks is None:
            return dash.no_update
        price_df = pd.DataFrame(columns=["trade_date", "close"])
        result = Stock_price.query.with_entities(Stock_price.trade_date, Stock_price.close).filter(
            Stock_price.name == company, Stock_price.trade_date.between(start_date, end_date)
        )
        price_df["trade_date"] = [x[0] for x in result]
        price_df["close"] = [x[1] for x in result]
        fig = px.line(data_frame=price_df, x="trade_date", y="close", title=str(company))
        return fig







