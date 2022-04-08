import pandas as pd
import talib as ta
import plotly.graph_objects as go



def macd_line(close_price):
    exp1 = close_price.ewm(span=12, adjust=False).mean()
    exp2 = close_price.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2


    return macd

def macd_signal_line(close_price):
    exp1 = close_price.ewm(span=12, adjust=False).mean()
    exp2 = close_price.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    exp3 = macd.ewm(span=9, adjust=False).mean()

    return exp3


    return ta.RSI(df[close_col], timeperiod=14)

def macd_all(close_price):

    macd=macd_line(close_price)
    macd_signal=macd_signal_line(close_price)
    macd_hist=macd-macd_signal

    return macd, macd_signal, macd_hist

def rsi(close_price):

    return ta.RSI(close_price, timeperiod=14)

def adx(high, low, close):
    return  ta.ADX(high, low, close, timeperiod=14)
def bop(open, high, low, close):
    return ta.BOP(open, high, low, close)
