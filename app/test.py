import json

import datetime as datetime

import bs4
import psycopg2
from IPython.core.display_functions import display
from talib import ADX, MACD
from bs4 import BeautifulSoup
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
from app.models import Stock_price
from talib import *
import urllib

from config import BaseConfig
from dashapp_charts.indicators import *
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import talib as ta
#from dashapp_charts.chart_utils import *

def update_xaxes_range(df, col_date):
    df[col_date] = pd.to_datetime(df[col_date])
    delta_days = (max(df[col_date]) - min(df[col_date])).days
    xaxis_end_date = max(df[col_date]) + timedelta(delta_days / 20)
    return [str(min(df[col_date])), str(xaxis_end_date)]
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


interval='day'
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

price_df['macd']=indicators_dict['macd'](price_df['Close'])[0]
price_df['macd_sig']=indicators_dict['macd'](price_df['Close'])[1]
price_df['macd_hist']=indicators_dict['macd'](price_df['Close'])[2]

indicators_args={
                'macd':[price_df['Close']],
                'rsi':[price_df['Close']],
                'adx':[price_df['High'],price_df['Low'],price_df['Close']]
            }

print(len(indicators_args['adx']))
adx_v=ta.BOP(price_df['Open'],price_df['High'],price_df['Low'],price_df['Close'])
print(adx_v)

figure = make_subplots(rows=3, cols=1, shared_xaxes=True,
                           vertical_spacing=0.042,
                           subplot_titles=(str(company) + ' ' + interval, 'Volume'),
                           row_width=[0.17,0.17, 0.58])
figure.update_layout(height=900)
figure.add_trace(go.Scatter(
    x=price_df['Date'],
    y=price_df['Close']

))
figure.add_trace(go.Bar(x=price_df['Date'], y=price_df['Volume'], showlegend=False), row=2,
                 col=1)
figure.update_xaxes(range=update_xaxes_range(price_df, 'Date'))
figure.update_layout(xaxis_rangeslider_visible=False)






import requests
import re
import regex
URL = "https://mrjbq7.github.io/ta-lib/func_groups/momentum_indicators.html"
page = requests.get(URL)
indicators=[]
cols=[]
soup = bs4.BeautifulSoup(page.content, "html.parser")
results = soup.find('div',id="main_content_wrap")
func_elements=results.find_all('pre')
strings_args=['open','high','low','close','volume']
args=[]

def match(input_string, string_list):
    words = re.findall(r'\w+', input_string)
    return [word for word in words if word in string_list]
for func in func_elements:
    res=func.text.strip()
    sentence = re.sub(r"\s+", "", res, flags=re.UNICODE)
    print(sentence)
    func_name=re.findall(r'=(.*)\(',sentence,re.M)
    args_all=re.search(r'\((.*?)\)',sentence).group(1)
    args_list=args_all.split(',')

    arg=[x for x in args_list if x in strings_args]
    args.append(arg)
    col=sentence.split('=')
    col_name=col[0].split(',')
    cols.append(col_name)

    indicators.append(func_name[0])

list_of_dicts=[]
col_func=[]
for i in range(len(indicators)):
    col_f=[]
    for j in range(len(cols[i])):
        col_name=str(indicators[i])+'-'+str(cols[i][j])
        col_f.append(col_name)
    col_func.append(col_f)
print(col_func)
for name,col,arg in zip(indicators,col_func,args):
    ind_dict={}
    ind_dict['name']=name
    ind_dict['cols']=col
    ind_dict['arg']=arg
    dict_to_append=ind_dict.copy()
    list_of_dicts.append(dict_to_append)

print(list_of_dicts)
result_dict={}

cols_calc=[]
to_calc_all=[]
to_calc_2=[]
indicators_ta=[]
for name in indicators:

    name='ta.'+name
    indicators_ta.append(name)

print(indicators_ta)

for dict in list_of_dicts:
    to_calc=[]


    for i in range(len(dict['arg'])):

        price=price_df[dict['arg'][i].capitalize()]
        to_calc.append(price)
    for i in range(len(dict['cols'])):
        if len(dict['cols'])==1:
            price_df[dict['cols'][i]]=globals()[dict['name']](*to_calc)
        else:
            price_df[dict['cols'][i]] = globals()[dict['name']](*to_calc)[i]

    to_calc_all.append(to_calc)

#for i in range(len(to_calc_all)):

    #for j in range(len(to_calc_all[i])):
        #print(str(len(to_calc_all[i])) + '-' + str(len(args[i]))+'-'+str(len(to_calc_all[i][j])))




indicators_df=price_df.copy()
indicators_df.drop(indicators_df.iloc[:,0:9],inplace=True, axis=1)
print(indicators_df.info())
nan_count_dict={}
for col in indicators_df.columns:
    nan_count=indicators_df[col].isna().sum()
    f=str(col).split('-')[0]
    print(f)
    if f in indicators:

        nan_count_dict[f]=nan_count

print(indicators)
print(cols)
print(args)
print(nan_count_dict)
#print(len(list_of_dicts[2]['arg']))
cols_df=[]
for i in range(len(cols)):
    col_to_add=[]
    if 'real' in cols[i]:
        c=str(indicators[i]).lower()
        col_to_add.append(c)
    else:
        for j in range(len(cols[i])):
            col_to_add.append(cols[i][j])
    cols_df.append(col_to_add)

print(cols_df)
print(len(indicators))
print(len(cols))
print(len(args))
func_dict=dict.fromkeys(indicators)
print(func_dict)
print(list(nan_count_dict.values()))
nest_val=['name','cols','period','args']
list_to_convert=list(map(list,zip(indicators,cols_df,args,list(nan_count_dict.values()))))
from collections import defaultdict
indicator='MACD'
for i in range(len(indicators)):
    nest_dict=dict.fromkeys(nest_val)
    nest_dict['name']=list_to_convert[i][0]
    nest_dict['cols'] = list_to_convert[i][1]
    nest_dict['args'] = list_to_convert[i][2]
    nest_dict['period'] = list_to_convert[i][3]
    func_dict[indicators[i]]=nest_dict

print([key for key in func_dict.keys()])

for value in func_dict['MACD']['cols']:
    print(value)

price_df.drop(price_df.iloc[:,6:], inplace=True, axis=1)
indicators_dict=func_dict
print(indicators_dict)
for value, i in zip(indicators_dict[indicator]['cols'], range(len(indicators_dict[indicator]['cols']))):
    cols_to_calc = []
    for dfcol in indicators_dict[indicator]['args']:
        col_to_calc = price_df[str(dfcol).capitalize()]
        cols_to_calc.append(col_to_calc)
    print(cols_to_calc)
    for j in indicators_dict[indicator]['cols']:
        if len(indicators_dict[indicator]['cols'])==1:
            price_df[value] = locals()[indicator](*cols_to_calc)
        else:
            price_df[value] = locals()[indicator](*cols_to_calc)[i]
indicators_df_test=price_df.drop(price_df.loc[:,:'Volume'], inplace=True, axis=1)
print(indicators_df_test)
print(price_df.head(100))
for cols in price_df.loc[:,price_df.columns!='macd']:
    print(cols)


def get_df_name(df):
    name =[x for x in globals() if globals()[x] is df][0]
    return name





def fibonacci(n):
    # Check is n is less
    # than 0
    FibArray = [0, 1]
    if n <= 0:
        print("Incorrect input")

    # Check is n is less
    # than len(FibArray)
    elif n <= len(FibArray):
        return FibArray[n - 1]
    else:
        temp_fib = fibonacci(n - 1) + fibonacci(n - 2)
        FibArray.append(temp_fib)
        return temp_fib


# Driver Program
print(fibonacci(6))

for i in range(1,10):
    print(fibonacci(i))