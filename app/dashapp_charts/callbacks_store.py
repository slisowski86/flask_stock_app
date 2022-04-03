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
import plotly.graph_objects as go
from ..models import Stock_price
from dash.exceptions import PreventUpdate


def register_callbacks(dashapp):
    def company_min_date(company):
        company_date = Stock_price.query.with_entities(func.min(Stock_price.trade_date)).filter(
            Stock_price.name == company).first()
        return company_date[0]
    def company_max_date(company):
        company_date = Stock_price.query.with_entities(func.max(Stock_price.trade_date)).filter(
            Stock_price.name == company).first()
        return company_date[0]

    def update_xaxes_range(df, col_date):
        df[col_date] = pd.to_datetime(df[col_date])
        delta_days = (max(df[col_date]) - min(df[col_date])).days
        xaxis_end_date = max(df[col_date]) + timedelta(delta_days / 20)
        return [str(min(df[col_date])), str(xaxis_end_date)]

    def datetime_range(start=None, end=None):
        span = end - start
        for i in range(span.days + 1):
            yield start + timedelta(days=i)
    def candle_resample(df, col_date, period):
        df[col_date] = pd.to_datetime(df[col_date])
        df.set_index(col_date, inplace=True)
        df.sort_index(inplace=True)

        logic = {'Open': 'first',
                 'High': 'max',
                 'Low': 'min',
                 'Close': 'last',
                 'Volume': 'sum'}

        dfw = df.resample(period).apply(logic)

        dfw=dfw.reset_index()

        return dfw
    def line_resample(df, col_date, period):
        df[col_date] = pd.to_datetime(df[col_date])
        df.set_index(col_date, inplace=True)
        df.sort_index(inplace=True)

        logic = {'close': 'first',
                 'volume':'sum'}

        dfw = df.resample(period).apply(logic)

        dfw = dfw.reset_index()
        return dfw


    @dashapp.callback(Output('date_df','data'),
                      [Input('stock_dropdown','value'),
        Input(component_id='start_date', component_property='date'),
        Input(component_id='end_date', component_property='date')])
    def make_date_df(company, start_date, end_date):

        price_df = pd.DataFrame(columns=["trade_date", "close"])


        result = Stock_price.query.with_entities(Stock_price.trade_date, Stock_price.close, Stock_price.volume).filter(
            Stock_price.name == company, Stock_price.trade_date.between(start_date, end_date))
        price_df["trade_date"] = [x[0] for x in result]
        price_df["close"] = [x[1] for x in result]
        price_df["volume"]=[x[2] for x in result]

        return price_df.to_json(date_format='iso', orient='split')

    @dashapp.callback(Output('period_df', 'data'),
                      [Input('stock_dropdown', 'value'),
                      Input('period_dropdown', 'value')])
    def make_period_df(company,period_value):
        price_df = pd.DataFrame(columns=["trade_date", "close"])


        start_date_period = company_max_date(company) - relativedelta(months=period_value)
        result = Stock_price.query.with_entities(Stock_price.trade_date, Stock_price.close, Stock_price.volume).filter(
        Stock_price.name == company, Stock_price.trade_date.between(start_date_period, company_max_date(company)))
        price_df["trade_date"] = [x[0] for x in result]
        price_df["close"] = [x[1] for x in result]
        price_df["volume"] = [x[2] for x in result]
        return price_df.to_json(date_format='iso', orient='split')

    @dashapp.callback(Output('candle_df_period', 'data'),
                      [Input('stock_dropdown', 'value'),
                       Input('period_dropdown', 'value')])
    def make_candle_df_period(company,period_value):
        candle_price_df = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        start_date_period = company_max_date(company) - relativedelta(months=period_value)
        candle_result = Stock_price.query.with_entities(Stock_price.trade_date, Stock_price.open,
                                                        Stock_price.high, Stock_price.low,
                                                        Stock_price.close, Stock_price.volume).filter(
            Stock_price.name == company,
            Stock_price.trade_date.between(start_date_period, company_max_date(company))
        ).all()
        for column, i in zip(candle_price_df.columns, range(len(candle_result))):
            candle_price_df[column] = [x[i] for x in candle_result]






        return candle_price_df.to_json(date_format='iso', orient='split')

    @dashapp.callback(Output('candle_df_date', 'data'),
                      [Input('stock_dropdown', 'value'),
                       Input('start_date', 'date'),
                       Input('end_date','date')])
    def make_candle_df_date(company,start_date,end_date):


        candle_price_df = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close','Volume'])
        candle_result = Stock_price.query.with_entities(Stock_price.trade_date, Stock_price.open,
                                                        Stock_price.high, Stock_price.low, Stock_price.close, Stock_price.volume).filter(
            Stock_price.name == company, Stock_price.trade_date.between(start_date, end_date)
        ).all()
        for column, i in zip(candle_price_df.columns, range(len(candle_result))):
            candle_price_df[column] = [x[i] for x in candle_result]

        return candle_price_df.to_json(date_format='iso', orient='split')

    @dashapp.callback(Output('period_dropdown', 'disabled'),
                      Input('disable_dropdown', 'value'))
    def disable_dropdown(disable_value):
        if disable_value == 'period':
            return False
        else:
            return True

    @dashapp.callback([Output('start_date', 'disabled'),
                       Output('end_date', 'disabled')],
                      Input('disable_dropdown', 'value'))
    def disable_dropdown(disable_value):
        if disable_value == 'stock_date':
            return False, False
        else:
            return True, True
    @dashapp.callback(Output('stock_graph','figure'),
                      [Input('date_df','data'),
                       Input('period_df','data'),
                       Input('candle_df_date','data'),
                       Input('candle_df_period','data'),
                       Input('stock_dropdown','value'),
                       Input('disable_dropdown','value'),
                       Input('chart_type_dropdown','value'),
                       Input('period_dropdown', 'value')],
                      State('stock_graph','figure'))
    def update_figure(date_df,period_df,candle_df_date,candle_df_period,company,enable_value,chart_type,period_value,figure):


        if enable_value=='period':
            interval=''
            df_candle = pd.read_json(candle_df_period, orient='split')
            if period_value > 12 and period_value <= 60:
                df_candle = candle_resample(df_candle, 'Date', 'W')
                interval='Week'
            elif period_value > 60:
                df_candle = candle_resample(df_candle, 'Date', 'M')
                interval='Month'
            else:
                interval='Day'
            if chart_type=='candle':


                df_candle['Date'] = pd.to_datetime(df_candle['Date'])
                date_list_all = list(datetime_range(min(df_candle['Date']), max(df_candle['Date'])))
                diff_date = set(date_list_all) - set(df_candle['Date'])
                diff_date_str=list(map(str,diff_date))
                figure = go.Figure(go.Candlestick(
                    x=df_candle['Date'],
                    open=df_candle['Open'],
                    high=df_candle['High'],
                    low=df_candle['Low'],
                    close=df_candle['Close']

                ))
                figure.update_xaxes(range=update_xaxes_range(df_candle,'Date'))
                if period_value<=12:
                    figure.update_xaxes(rangebreaks=[dict(values=diff_date_str)])
                    figure.update_layout(title=str(company)+' '+interval,xaxis_rangeslider_visible=False)
                else:
                    figure.update_layout(title=str(company)+' '+interval, xaxis_rangeslider_visible=False)



            else:

                df_period=pd.read_json(period_df, orient='split')
                figure = px.line(data_frame=df_period, x="trade_date", y="close", title=str(company))
                figure.update_xaxes(range=update_xaxes_range(df_period,'trade_date'))
                print(update_xaxes_range(df_period, 'trade_date'))
        elif enable_value=='stock_date':

            df_date = pd.read_json(candle_df_date, orient='split')
            df_date_line = pd.read_json(date_df, orient='split')
            interval=''

            if len(df_date['Date'].value_counts()) > 0:
                max_date = (max(df_date['Date']))
                min_date = (min(df_date['Date']))
                max_date_dt = datetime(max_date.year, max_date.month, max_date.day)
                min_date_dt = datetime(min_date.year, min_date.month, min_date.day)

                if abs(max_date_dt-min_date_dt).days > 365 and abs(max_date_dt-min_date_dt).days <=1825 :
                    df_date=candle_resample(df_date,'Date','W')
                    interval='Week'
                elif abs(max_date_dt-min_date_dt).days > 1825:
                    df_date = candle_resample(df_date, 'Date', 'M')
                    interval='Month'
                else:
                    interval='Day'

            if chart_type == 'candle' and len(df_date['Date'].value_counts())>0:

                print()

                df_date['Date']=pd.to_datetime(df_date['Date'])
                date_list_all = list(datetime_range(min(df_date['Date']), max(df_date['Date'])))
                diff_date = set(date_list_all) - set(df_date['Date'])

                diff_date_str = list(map(str, diff_date))
                figure = go.Figure(go.Candlestick(
                    x=df_date['Date'],
                    open=df_date['Open'],
                    high=df_date['High'],
                    low=df_date['Low'],
                    close=df_date['Close']

                ))
                figure.update_xaxes(range=update_xaxes_range(df_date, 'Date'))
                if abs(max_date_dt - min_date_dt).days <= 365:
                    figure.update_xaxes(rangebreaks=[dict(values=diff_date_str)])
                figure.update_layout(title=str(company)+' '+interval, xaxis_rangeslider_visible=False)

            elif chart_type=='line' and len(df_date_line['trade_date'].value_counts())>0:
                df_date_line['trade_date']=pd.to_datetime(df_date_line['trade_date'])
                if len(df_date_line['trade_date'].value_counts()) > 0:
                    max_date = (max(df_date_line['trade_date']))
                    min_date = (min(df_date_line['trade_date']))
                    max_date_dt = datetime(max_date.year, max_date.month, max_date.day)
                    min_date_dt = datetime(min_date.year, min_date.month, min_date.day)
                    interval = ''
                    if abs(max_date_dt - min_date_dt).days > 365 and abs(max_date_dt - min_date_dt).days <= 1825:
                        df_date_line = line_resample(df_date_line, 'trade_date', 'W')
                        interval = 'Week'
                    elif abs(max_date_dt - min_date_dt).days > 1825:
                        df_date_line = line_resample(df_date_line, 'trade_date', 'M')
                        interval = 'Month'
                    else:
                        interval = 'Day'

                figure = px.line(data_frame=df_date_line, x="trade_date", y="close", title=str(company)+' '+interval)
                figure.update_xaxes(range=update_xaxes_range(df_date_line, 'trade_date'))
                print(update_xaxes_range(df_date_line, 'trade_date'))
        else:
            raise PreventUpdate



        return figure





