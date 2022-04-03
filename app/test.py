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

candle_price_df = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close'])
candle_result = session.query(Stock_price.trade_date, Stock_price.open,
                                                        Stock_price.high, Stock_price.low, Stock_price.close).filter(
            Stock_price.name == company, Stock_price.trade_date.between('2020-01-01', '2022-03-10')).all()

for column, i in zip(candle_price_df.columns, range(len(candle_result))):
    candle_price_df[column] = [x[i] for x in candle_result]


def candle_week_resample(df, col_date, period):
    df[col_date] = pd.to_datetime(df[col_date])
    df.set_index(col_date, inplace=True)
    df.sort_index(inplace=True)

    logic = {'Open': 'first',
             'High': 'max',
             'Low': 'min',
             'Close': 'last'}

    dfw = df.resample(period).apply(logic)
    # set the index to the beginning of the week
    #dfw.index = dfw.index - pd.tseries.frequencies.to_offset("6D")
    #dfw.reset_index()
    return dfw

week_df=candle_week_resample(candle_price_df,'Date','M')

week_df=week_df.reset_index()
print(week_df.head())
c_date=company_max_date('LPP')
c_date_dt=datetime(c_date.year, c_date.month, c_date.day)
print(c_date_dt-relativedelta(months=2))
a_date = datetime.strptime("2019-01-13", "%Y-%m-%d")
print(a_date)
print(company_max_date('LPP'))
print(company_min_date('LPP'))
print(abs(company_max_date('LPP')-company_min_date('LPP')).days)