import json

import psycopg2

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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Stock_price
from config import BaseConfig
import plotly.graph_objects as go
from plotly.subplots import make_subplots
engine=create_engine(BaseConfig.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()
from dashapp_charts.chart_utils import register_chart_utils
from dashapp_charts.callbacks_store import register_callbacks

register_chart_utils()
def company_min_date(company):
    company_date = session.query(func.min(Stock_price.trade_date)).filter(
        Stock_price.name == company).first()
    return company_date[0]


def company_max_date(company):
    company_date = session.query(func.max(Stock_price.trade_date)).filter(
        Stock_price.name == company).first()
    return company_date[0]


def update_xaxes_range(df, col_date):
    df[col_date]=pd.to_datetime(df[col_date])
    delta_days = (max(df[col_date]) - min(df[col_date])).days
    xaxis_end_date = max(df[col_date]) + timedelta(delta_days / 20)
    return [str(min(df[col_date])), str(xaxis_end_date)]

def datetime_range(start=None, end=None):
    span = end - start
    for i in range(span.days + 1):
        yield start + timedelta(days=i)




company='LPP'
start_date='2018-01-01'
end_date='2022-03-10'
price_df = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
start_date_period = company_max_date(company) - relativedelta(months=1)
result = session.query(Stock_price.trade_date, Stock_price.open,
                                                            Stock_price.high, Stock_price.low, Stock_price.close,
                                                            Stock_price.volume).filter(
                Stock_price.name == company, Stock_price.trade_date.between(start_date, end_date)).all()
for column, i in zip(price_df.columns, range(len(result))):
    price_df[column] = [x[i] for x in result]
#figure = px.line(data_frame=price_df, x="trade_date", y="close", title=str(company))
#figure.update_xaxes(range=update_xaxes_range(price_df,'trade_date'))

#figure.show()
price_df['Date']=pd.to_datetime(price_df['Date'])
date_list=list(datetime_range(min(price_df['Date']),max(price_df['Date'])))
print(type(price_df['Date'][0]))
print(type(date_list[0]))

diff=set(date_list)-set(price_df['Date'])
print(sorted(diff))
str_dates=list(map(str,diff))
print(type(str_dates[0]))

print(price_df.columns.values)
def period_resample(df, col_date, period):
    df[col_date] = pd.to_datetime(df[col_date])
    df.set_index(col_date, inplace=True)
    df.sort_index(inplace=True)

    logic = {'Open': 'first',
             'High': 'max',
             'Low': 'min',
             'Close': 'last',
             'Volume': 'sum'}

    dfw = df.resample(period).apply(logic)

    dfw = dfw.reset_index()

    return dfw
period_value=36
interval_df=''
if period_value > 12 and period_value <= 60:
    price_df = period_resample(price_df, 'Date', 'W')
    interval_df = 'Week'
def diff_dates(df, col_date):
    date_list_all = list(datetime_range(min(df[col_date]), max(df[col_date])))
    diff_date = set(date_list_all) - set(df[col_date])
    diff_date_str = list(map(str, diff_date))
    return diff_date_str

def make_subplot_period(df,interval, chart_type, period_value):



    if chart_type == 'candle':

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
        figure.add_trace(go.Bar(x=price_df['Date'], y=price_df['Volume'], showlegend=False), row=2,
                         col=1)

        figure.update_xaxes(range=update_xaxes_range(price_df, 'Date'))
        if period_value <= 12:
            figure.update_xaxes(rangebreaks=[dict(values=diff_dates(df,'Date'))])
            figure.update_layout(title=str(company) + ' ' + interval, xaxis_rangeslider_visible=False)
        else:
            figure.update_layout(title=str(company) + ' ' + interval, xaxis_rangeslider_visible=False)


    else:

        figure = make_subplots(rows=2, cols=1, shared_xaxes=True,
                               vertical_spacing=0.1,
                               subplot_titles=(str(company) + ' ' + interval, 'Volume'),
                               row_width=[0.2, 0.7])

        figure.add_trace(go.Scatter(
            x=price_df['Date'],
            y=price_df['Close']

        ))
        figure.add_trace(go.Bar(x=price_df['Date'], y=price_df['Volume'], showlegend=False), row=2,
                         col=1)
        if period_value <= 12:
            figure.update_xaxes(rangebreaks=[dict(values=diff_dates(df,'Date'))])
        figure.update_xaxes(range=update_xaxes_range(price_df, 'Date'))
        figure.update_layout(height=750)


    return  figure

make_subplot_period(price_df,interval_df,'line',period_value).show()