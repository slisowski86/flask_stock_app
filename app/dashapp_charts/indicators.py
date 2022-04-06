import pandas as pd
import talib as ta
import plotly.graph_objects as go

def macd(df, close_col):
    exp1 = df[close_col].ewm(span=12, adjust=False).mean()
    exp2 = df[close_col].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2


    return macd

def macd_signal(df, close_col):
    exp1 = df[close_col].ewm(span=12, adjust=False).mean()
    exp2 = df[close_col].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    exp3 = macd.ewm(span=9, adjust=False).mean()

    return exp3


    return ta.RSI(df[close_col], timeperiod=14)

def macd_all(df, close_col):
    macd_f=macd(df,close_col)
    macd_s=macd_signal(df,close_col)
    macd_hist=macd_f-macd_s

    return macd_f, macd_s, macd_hist

def rsi(df,close_col):

    return ta.RSI(df[close_col], timeperiod=14)



