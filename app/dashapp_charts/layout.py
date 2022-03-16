import psycopg2
from config import BaseConfig
from dash import dcc, html, Dash, dash
import plotly.express as px
from dash.dependencies import Input, Output
import pandas as pd
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from config import BaseConfig
from ..models import Company, Stock_price
from sqlalchemy import func

import dash_bootstrap_components as dbc


engine=create_engine(BaseConfig.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()
result_stock_list = session.query(Company.name).all()
companies_list = [x[0] for x in result_stock_list]
min_date=session.query(func.min(Stock_price.trade_date)).first()
min_date=min_date[0]
max_date=session.query(func.max(Stock_price.trade_date)).first()
max_date=max_date[0]


layout=html.Div(children=[
        html.Div(className='row',
        children=[
        html.Div(className='four columns div-user-controls',
        children=[dcc.Store(id='stock_memory'),
        html.H3("Stock price charts"),
        dcc.Dropdown(companies_list, None, id="stock_dropdown", style={'width':300}),
        dcc.DatePickerSingle(id="start_date",
            min_date_allowed=min_date,
            max_date_allowed=max_date,
            initial_visible_month=min_date,
            date=min_date
        ),
        dcc.DatePickerSingle(id="end_date",
            min_date_allowed=min_date,
            max_date_allowed=max_date,
            initial_visible_month=max_date,
            date=max_date
        ),
        html.Button('Show chart', id='show', n_clicks=0),
        html.Button('Clear', id='clear', n_clicks=0)]),

    html.Div(className='eight columns div-for-charts bg-grey',children=[
], id="stock_graph", style={'height':800,'width':800})])])

