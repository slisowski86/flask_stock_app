import json

import datetime as datetime
import psycopg2
from talib import ADX, MACD

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
from sqlalchemy import create_engine, select, func, text
from sqlalchemy.orm import sessionmaker
from models  import Stock_price
import talib as ta
from config import BaseConfig
from dashapp_charts.indicators import *
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import talib as ta
engine=create_engine(BaseConfig.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()
import pandas_ta as pta
company='PZU'
start_date='2020-01-10'
end_date='2022-03-10'
dt_start_date=datetime.strptime(start_date, '%Y-%m-%d').date()
rsi_length=14
start_date_before=dt_start_date-timedelta(days=rsi_length)
print(start_date_before)
price_df = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
price_df_rsi = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])



result = session.query(Stock_price.trade_date, Stock_price.open,
                                                            Stock_price.high, Stock_price.low, Stock_price.close,
                                                            Stock_price.volume).filter(
                Stock_price.name == company, Stock_price.trade_date.between(start_date, end_date)).all()

for column, i in zip(price_df.columns, range(len(result))):
    price_df[column] = [x[i] for x in result]




def macd_my():
    macd_ta, macd_sig, macd_hist = ta.MACD(price_df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
    return macd_ta, macd_sig, macd_hist




result_14=result = session.execute("WITH CTE AS (SELECT id, trade_date FROM stock_price WHERE name='LPP' AND trade_date BETWEEN :start_date AND :end_date FETCH FIRST ROW ONLY ) SELECT id-33 FROM CTE",
                                   {'start_date':start_date, 'end_date':end_date}).all()

back_date_id=result_14[0][0]
print(back_date_id)
start_date_14=session.query(Stock_price.trade_date).filter(Stock_price.id==back_date_id).first()
print(start_date_14[0])

result_for_rsi=session.query(Stock_price.trade_date, Stock_price.open,
                                                            Stock_price.high, Stock_price.low, Stock_price.close,
                                                            Stock_price.volume).filter(
                Stock_price.name == company, Stock_price.trade_date.between(start_date_14[0], end_date)).all()

for column, i in zip(price_df_rsi.columns, range(len(result_for_rsi))):
    price_df_rsi[column] = [x[i] for x in result_for_rsi]

print(price_df.info())
print(price_df_rsi.info())


price_df['MACD']=ta.MACD(price_df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)[0]
price_df_rsi['MACD']=ta.MACD(price_df_rsi['Close'], fastperiod=12, slowperiod=26, signalperiod=9)[0]

print(price_df)
print(price_df_rsi)


figure = make_subplots(rows=3, cols=1, shared_xaxes=True,
                           vertical_spacing=0.042,
                           subplot_titles=(str(company),'Volume'),
                           row_width=[0.17,0.17, 0.58])

figure.update_layout(height=900)
figure.add_trace(go.Candlestick(
    x=price_df['Date'],
    open=price_df['Open'],
    high=price_df['High'],
    low=price_df['Low'],
    close=price_df['Close']

),row=1,col=1)

set_df=price_df_rsi.dropna()


figure.add_trace(go.Bar(x=price_df['Date'], y=price_df['Volume'], showlegend=False), row=2,
                 col=1)

figure.add_trace(go.Scatter(x=price_df['Date'], y=set_df['MACD'], showlegend=False), row=3,
                 col=1)

print(price_df.head(34))
print(price_df_rsi.head(34))
print(price_df_rsi.info())
price_df_rsi['Date']=pd.to_datetime(price_df_rsi['Date'])
set_df=price_df_rsi[price_df_rsi['Date']>=datetime.strptime(start_date,'%Y-%m-%d')]

print(set_df)

