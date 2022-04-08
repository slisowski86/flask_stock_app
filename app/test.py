import json

import datetime as datetime
import psycopg2
from IPython.core.display_functions import display
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

start_date_14=session.query(Stock_price.trade_date).filter(Stock_price.id==back_date_id).first()


result_for_rsi=session.query(Stock_price.trade_date, Stock_price.open,
                                                            Stock_price.high, Stock_price.low, Stock_price.close,
                                                            Stock_price.volume).filter(
                Stock_price.name == company, Stock_price.trade_date.between(start_date_14[0], end_date)).all()

for column, i in zip(price_df_rsi.columns, range(len(result_for_rsi))):
    price_df_rsi[column] = [x[i] for x in result_for_rsi]


indicators_dict = {'macd': macd_all,
                           'rsi': rsi,
                            'adx':adx}

price_df['MACD']=indicators_dict['macd'](price_df['Close'])[0]
price_df['MACD_sig']=indicators_dict['macd'](price_df['Close'])[1]
price_df['macd_hist']=indicators_dict['macd'](price_df['Close'])[2]

indicators_args={
                'macd':[price_df['Close']],
                'rsi':[price_df['Close']],
                'adx':[price_df['High'],price_df['Low'],price_df['Close']]
            }

print(len(indicators_args['adx']))
adx_v=ta.BOP(price_df['Open'],price_df['High'],price_df['Low'],price_df['Close'])
print(adx_v)

import plotly.express as px
import plotly.graph_objs as go
import ipywidgets as widgets

iris = px.data.iris()
iris['index_new'] = iris.index
p = px.scatter(iris, x="sepal_width", y="sepal_length", color="species", hover_name='index_new')

def hover_fn(trace, points, state):
    if points.point_inds:
        ind = points.point_inds[0]
        hover_data.value = 'hover_df_index: \n {:d}'.format(int(trace.hovertext[ind]))
        inds =  trace.hovertext[ind]
        display(iris[inds])

hover_data = widgets.Label()

fig  = go.FigureWidget(p)

for f in fig.data:
    f.on_hover(hover_fn)

display(fig,hover_data)

string_j='{ "points": [ { "curveNumber": 0, "pointNumber": 4, "pointIndex": 4, "x": "2022-03-11", "open": 265, "high": 291.5, "low": 260.8, "close": 290.3, "bbox": { "x0": 260.25, "x1": 281.68, "y0": 469.04, "y1": 469.04 } } ] }'

res=json.loads(string_j)
print(type(res))
print(type(res['points'][0]['pointIndex']))