import pandas as pd
import talib as ta
import plotly.graph_objects as go

def macd(close_price):
    exp1 = close_price.ewm(span=12, adjust=False).mean()
    exp2 = close_price.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2


    return macd

def macd_signal(close_price):
    exp1 = close_price.ewm(span=12, adjust=False).mean()
    exp2 = close_price.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    exp3 = macd.ewm(span=9, adjust=False).mean()

    return exp3


    return ta.RSI(df[close_col], timeperiod=14)

def macd_all(close_price):

    macd_f=macd(close_price)
    macd_s=macd_signal(close_price)
    macd_hist=macd_f-macd_s

    return macd_f, macd_s, macd_hist

def rsi(close_price):

    return ta.RSI(close_price, timeperiod=14)

def adx(high, low, close):
    return  ta.ADX(high, low, close, timeperiod=14)

