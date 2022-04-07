

import psycopg2
from plotly.subplots import make_subplots

import app
from config import BaseConfig
from dash import dcc, html, Dash, dash
import dash
import plotly.express as px
from dash.dependencies import Input, Output, State
import pandas as pd
from datetime import timedelta, datetime
from sqlalchemy import func
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go
from ..models import Stock_price
from dash.exceptions import PreventUpdate
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .indicators import *


engine = create_engine(BaseConfig.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

def datetime_range(start=None, end=None):
    span = end - start
    for i in range(span.days + 1):
        yield start + timedelta(days=i)

def company_max_date(company):
    company_date = session.query(func.max(Stock_price.trade_date)).filter(
        Stock_price.name == company).first()
    return company_date[0]

def update_xaxes_range(df, col_date):
    df[col_date] = pd.to_datetime(df[col_date])
    delta_days = (max(df[col_date]) - min(df[col_date])).days
    xaxis_end_date = max(df[col_date]) + timedelta(delta_days / 20)
    return [str(min(df[col_date])), str(xaxis_end_date)]

def diff_dates(df, col_date):
    date_list_all = list(datetime_range(min(df[col_date]), max(df[col_date])))
    diff_date = set(date_list_all) - set(df[col_date])
    diff_date_str = list(map(str, diff_date))
    return diff_date_str

def make_subplot_candle(df, company, interval):



    figure = make_subplots(rows=2, cols=1, shared_xaxes=True,
                           vertical_spacing=0.05,
                           subplot_titles=(str(company) + ' ' + interval, 'Volume',),
                           row_width=[0.2, 0.7])
    figure.update_layout(height=750)
    figure.add_trace(go.Candlestick(
        x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close']

    ))
    figure.add_trace(go.Bar(x=df['Date'], y=df['Volume'], showlegend=False), row=2,
                     col=1)

    figure.update_xaxes(range=update_xaxes_range(df, 'Date'))
    figure.update_layout(title=str(company) + ' ' + interval, xaxis_rangeslider_visible=False)



    return figure


def make_subplot_line(df, company, interval):
    figure = make_subplots(rows=2, cols=1, shared_xaxes=True,
                           vertical_spacing=0.05,
                           subplot_titles=(str(company) + ' ' + interval, 'Volume'),
                           row_width=[0.2, 0.7])
    figure.update_layout(height=750)
    figure.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Close']

    ))
    figure.add_trace(go.Bar(x=df['Date'], y=df['Volume'], showlegend=False), row=2,
                     col=1)
    figure.update_xaxes(range=update_xaxes_range(df, 'Date'))
    figure.update_layout(title=str(company) + ' ' + interval, xaxis_rangeslider_visible=False)
    return figure

def make_subplot_candle_indicator(df, company, interval,indicator):

    figure = make_subplots(rows=3, cols=1, shared_xaxes=True,
                           vertical_spacing=0.042,
                           subplot_titles=(str(company) + ' ' + interval, 'Volume', indicator),
                           row_width=[0.17,0.17, 0.58])

    figure.update_layout(height=900)
    figure.add_trace(go.Candlestick(
        x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close']

    ))

    figure.add_trace(go.Bar(x=df['Date'], y=df['Volume'], showlegend=False), row=2,
                     col=1)


    figure.add_trace(go.Scatter(x=df['Date'], y=df[indicator]), row=3, col=1)

    figure.update_xaxes(range=update_xaxes_range(df, 'Date'))
    figure.update_layout(title=str(company) + ' ' + interval, xaxis_rangeslider_visible=False)

    return figure

