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

engine=create_engine(BaseConfig.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

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

price_df = pd.DataFrame(columns=["trade_date", "close"])
start_date_period = company_max_date(company) - relativedelta(months=1)
result = session.query(Stock_price.trade_date, Stock_price.close).filter(
    Stock_price.name == company, Stock_price.trade_date.between(start_date_period, company_max_date(company))).all()
price_df["trade_date"] = [x[0] for x in result]
price_df["close"] = [x[1] for x in result]
#figure = px.line(data_frame=price_df, x="trade_date", y="close", title=str(company))
#figure.update_xaxes(range=update_xaxes_range(price_df,'trade_date'))

#figure.show()
price_df['trade_date']=pd.to_datetime(price_df['trade_date'])
date_list=list(datetime_range(min(price_df['trade_date']),max(price_df['trade_date'])))
print(type(price_df['trade_date'][0]))
print(type(date_list[0]))

diff=set(date_list)-set(price_df['trade_date'])
print(sorted(diff))
str_dates=list(map(str,diff))
print(type(str_dates[0]))


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





print()