import json

import psycopg2
from plotly.subplots import make_subplots

import app
from config import BaseConfig
from dash import dcc, html, Dash, dash
import dash
import plotly.express as px
from dash.dependencies import Input, Output, State
import pandas as pd
from datetime import timedelta, datetime
from sqlalchemy import func, create_engine
from sqlalchemy.orm import sessionmaker
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go
from .chart_utils import *
from ..models import Stock_price
from .indicators import *
from dash.exceptions import PreventUpdate
from ..extensions import db
from .functions_dict import func_dict
from talib import *
def register_callbacks(dashapp):



    def diff_dates(df, col_date):
        date_list_all = list(datetime_range(min(df[col_date]), max(df[col_date])))
        diff_date = set(date_list_all) - set(df[col_date])
        diff_date_str = list(map(str, diff_date))
        return diff_date_str


    def company_max_date(company):
        company_date = Stock_price.query.with_entities(func.max(Stock_price.trade_date)).filter(
            Stock_price.name == company).first()
        return company_date[0]


    def datetime_range(start=None, end=None):
        span = end - start
        for i in range(span.days + 1):
            yield start + timedelta(days=i)

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

    @dashapp.callback([Output('price_df', 'data'),
                       Output('interval','value')],
                        [Input('stock_dropdown', 'value'),
                         Input('indicators_2','value'),

                       Input('period_dropdown', 'value')])
    def make_price_df(company, indicator, period_value):
        price_df = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        start_date_period = company_max_date(company) - relativedelta(months=period_value)


        if indicator is not None:
            with open('func_dict.json') as json_file:
                indicators_dict = json.load(json_file)
            #indicators_period = {'macd': 33,
                                 #'rsi': 14,
                                 #'adx':27,
                                 #'bop':0}
            print(indicators_dict[indicator]['name'])


            if period_value > 12 and period_value <= 60:
                indicators_period_value = indicators_dict[indicator]['period'] * 7
            elif period_value > 60:
                indicators_period_value = indicators_dict[indicator]['period'] * 31
            else:
                indicators_period_value = indicators_dict[indicator]['period']
            indicator_start_id = session.execute(
                "WITH CTE AS (SELECT id, trade_date FROM stock_price WHERE name=:company AND trade_date BETWEEN :start_date AND :end_date FETCH FIRST ROW ONLY ) SELECT id-:ind_period FROM CTE",
                {'company': company, 'ind_period': int(indicators_period_value), 'start_date': start_date_period,
                 'end_date': company_max_date(company)}).all()
            back_date_id = indicator_start_id[0][0]
            if back_date_id <= 0:
                back_date_id = 1
            start_date_indicator = Stock_price.query.with_entities(Stock_price.trade_date).filter(
                Stock_price.id == back_date_id).all()

            result_for_indicator = Stock_price.query.with_entities(Stock_price.trade_date, Stock_price.open,
                                                                   Stock_price.high, Stock_price.low,
                                                                   Stock_price.close,
                                                                   Stock_price.volume).filter(
                Stock_price.name == company,
                Stock_price.trade_date.between(start_date_indicator[0][0], company_max_date(company))).all()

            for column, i in zip(price_df.columns, range(len(result_for_indicator))):
                price_df[column] = [x[i] for x in result_for_indicator]
            max_date = (max(price_df['Date']))
            min_date = (min(price_df['Date']))
            max_date_dt = datetime(max_date.year, max_date.month, max_date.day)
            min_date_dt = datetime(min_date.year, min_date.month, min_date.day)
            if (period_value > 12 and period_value <= 60):
                price_df = period_resample(price_df, 'Date', 'W')
                interval = 'Week'
            elif period_value > 60:
                price_df = period_resample(price_df, 'Date', 'M')
                interval = 'Month'

            else:
                interval = 'Day'

            #indicators_args={
                #'macd':[price_df['Close']],
                #'rsi':[price_df['Close']],
                #'adx':[price_df['High'],price_df['Low'],price_df['Close']],
                #'bop':[price_df['Open'],price_df['High'],price_df['Low'],price_df['Close']]
            #}
            #if indicator=='macd':
                #price_df[indicator] = indicators_dict[indicator](price_df['Close'])[0]
                #price_df['macd_sig']=indicators_dict[indicator](price_df['Close'])[1]
                #price_df['macd_hist'] = indicators_dict[indicator](price_df['Close'])[2]
            #else:

                #price_df[indicator] = indicators_dict[indicator](*indicators_args[indicator])
            for value, i in zip(indicators_dict[indicator]['cols'], range(len(indicators_dict[indicator]['cols']))):
                print(indicator)
                cols_to_calc=[]
                for dfcol in indicators_dict[indicator]['args']:
                    col_to_calc=price_df[str(dfcol).capitalize()]
                    cols_to_calc.append(col_to_calc)
                for j in indicators_dict[indicator]['cols']:
                    if len(indicators_dict[indicator]['cols']) == 1:
                        price_df[str(value).upper()] = globals()[indicators_dict[indicator]['name']](*cols_to_calc)
                    else:
                        price_df[str(value).upper()] = globals()[indicators_dict[indicator]['name']](*cols_to_calc)[i]
            price_df['Date'] = pd.to_datetime(price_df['Date'])
            price_df = price_df[price_df['Date'] >= datetime.strptime(str(start_date_period), '%Y-%m-%d')]
            print(price_df.head())
        else:
            result = Stock_price.query.with_entities(Stock_price.trade_date, Stock_price.open,
                                                     Stock_price.high, Stock_price.low, Stock_price.close,
                                                     Stock_price.volume).filter(
                Stock_price.name == company, Stock_price.trade_date.between(start_date_period, company_max_date(company))
            ).all()
            for column, i in zip(price_df.columns, range(len(result))):
                price_df[column] = [x[i] for x in result]
            max_date = (max(price_df['Date']))
            min_date = (min(price_df['Date']))
            max_date_dt = datetime(max_date.year, max_date.month, max_date.day)
            min_date_dt = datetime(min_date.year, min_date.month, min_date.day)
            if (abs(max_date_dt - min_date_dt).days > 365 and abs(max_date_dt - min_date_dt).days <= 1825) \
                    or (period_value > 12 and period_value <= 60):
                price_df = period_resample(price_df, 'Date', 'W')
                interval = 'Week'
            elif abs(max_date_dt - min_date_dt).days > 1825 or period_value > 60:
                price_df = period_resample(price_df, 'Date', 'M')
                interval = 'Month'

            else:
                interval = 'Day'


        return price_df.to_json(date_format='iso', orient='split'), interval




    @dashapp.callback(Output('stock_graph', 'figure'),
                      [
                          Input('price_df', 'data'),
                          Input('indicators_2','value'),
                          Input('interval','value'),
                          Input('stock_dropdown', 'value'),

                          Input('chart_type_dropdown', 'value'),
                        Input('period_dropdown', 'value')],
                      State('stock_graph', 'figure'))
    def update_figure(price_df, indicator, interval_df,company,
                      chart_type,
                      period_value, figure):
        indicators_dict_fig = {'MACD': macd_figure,
                           'RSI': rsi_figure,
                           'ADX': adx_figure,
                           'BOP': bop_figure}

        price_df = pd.read_json(price_df, orient='split')
        interval=interval_df

        max_date = (max(price_df['Date']))
        min_date = (min(price_df['Date']))
        max_date_dt = datetime(max_date.year, max_date.month, max_date.day)
        min_date_dt = datetime(min_date.year, min_date.month, min_date.day)



        if chart_type=='candle':

            figure=make_subplot_candle(price_df,company,interval)


            if indicator is not None:
                make_figure(figure,price_df,indicator)





        else:

            figure = make_subplot_line(price_df,company,interval)
            if indicator is not None:
                make_figure(figure, price_df, indicator)

        if period_value <= 12:
            figure.update_xaxes(rangebreaks=[dict(values=diff_dates(price_df, 'Date'))])





        return figure






