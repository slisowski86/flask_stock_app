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
        Output(component_id='stock_graph', component_property='children'),
        [Input('show','n_clicks'),
         Input('clear','n_clicks')],
        [State('stock_dropdown','value'),
        State(component_id='start_date', component_property='date'),
        State(component_id='end_date', component_property='date'),
         State('stock_graph','children')]


    )

    def update_stock_graph(show_button,clear, company, start_date, end_date, children):
        children=[]
        template='plotly_dark'
        price_df = pd.DataFrame(columns=["trade_date", "close"])
        result = Stock_price.query.with_entities(Stock_price.trade_date, Stock_price.close).filter(
            Stock_price.name == company, Stock_price.trade_date.between(start_date, end_date))
        price_df["trade_date"] = [x[0] for x in result]
        price_df["close"] = [x[1] for x in result]
        if show_button>0:
            if children:
                children[0]["props"]["figure"] = px.line(data_frame=price_df, x="trade_date", y="close", title=str(company))
            else:
                fig=px.line(data_frame=price_df, x="trade_date", y="close", title=str(company))
                fig.update_layout(plot_bgcolor='#31302F', paper_bgcolor='#31302F')
                children.append(dcc.Graph(figure=fig))

        return children







