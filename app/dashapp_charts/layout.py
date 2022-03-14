import psycopg2
from config import BaseConfig
from dash import dcc, html, Dash, dash
import plotly.express as px
from dash.dependencies import Input, Output
import pandas as pd
from .chart_utils import companies_list


layout=html.Div(
    children=[
        html.H3("Stock price charts"),
        dcc.Dropdown(companies_list(), None, id="stock_dropdown"),

        dcc.Graph(id='stock_graph')],
    style={'height':800,'width':800})
