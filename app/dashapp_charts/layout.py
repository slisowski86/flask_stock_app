import psycopg2
from config import BaseConfig
from dash import dcc, html, Dash, dash
import plotly.express as px
from dash.dependencies import Input, Output
import pandas as pd
from .chart_utils import companies_list
from datetime import date



layout=html.Div(
    children=[
        html.H3("Stock price charts"),
        dcc.Dropdown(companies_list(), None, id="stock_dropdown"),
        dcc.DatePickerSingle(id="start_date",
            min_date_allowed=date(1993,7,8),
            max_date_allowed=date(2025,3,11),
            initial_visible_month=date.today(),
            date=date.today()
        ),
        dcc.DatePickerSingle(id="end_date",
            min_date_allowed=date(1993,7,8),
            max_date_allowed=date(2025,3,11),
            initial_visible_month=date.today(),
            date=date.today()
        ),

        dcc.Graph(id='stock_graph')],
    style={'height':800,'width':800})
