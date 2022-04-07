

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

    def period_resample_indicator(df, col_date, period,indicator):
        df[col_date] = pd.to_datetime(df[col_date])
        df.set_index(col_date, inplace=True)
        df.sort_index(inplace=True)

        logic = {'Open': 'first',
                 'High': 'max',
                 'Low': 'min',
                 'Close': 'last',
                 'Volume': 'sum',
                 }

        dfw = df.resample(period).apply(logic)

        dfw = dfw.reset_index()

        return dfw

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

    @dashapp.callback([Output('price_df', 'data'),
                       Output('interval','value')],
                        [Input('stock_dropdown', 'value'),
                         Input('indicators','value'),
                       Input(component_id='start_date', component_property='date'),
                       Input(component_id='end_date', component_property='date'),
                       Input('period_dropdown', 'value'),
                       Input('disable_dropdown', 'value')])
    def make_price_df(company, indicator,start_date, end_date, period_value, enable_value):
        price_df = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])

        #max_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
        #min_date_dt = datetime.strptime(start_date, '%Y-%m-%d')


        if enable_value == 'stock_date':
            start_date=start_date


        else:
            start_date=start_date_period
        if indicator is not None:
            price_df = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
            start_date_period = company_max_date(company) - relativedelta(months=period_value)
            indicators_period = {'macd': 33,
                                 'rsi': 14}
            indicators_period_value=0
            if enable_value == 'stock_date':
                start_date = start_date
                max_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
                min_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
                if (abs(max_date_dt - min_date_dt).days > 365 and abs(max_date_dt - min_date_dt).days <= 1825):
                    indicators_period_value = indicators_period[indicator] * 7
                elif period_value > 1825:
                    indicators_period_value = indicators_period[indicator] * 31
                else:
                    indicators_period_value = indicators_period[indicator]


            else:
                start_date = start_date_period
                if (period_value > 12 and period_value <= 60):
                    indicators_period_value = indicators_period[indicator] * 7
                elif period_value > 60:
                    indicators_period_value = indicators_period[indicator] * 31
                else:
                    indicators_period_value = indicators_period[indicator]


            print(indicators_period_value)

            indicator_start_id = session.execute(
                "WITH CTE AS (SELECT id, trade_date FROM stock_price WHERE name=:company AND trade_date BETWEEN :start_date AND :end_date FETCH FIRST ROW ONLY ) SELECT id-:ind_period FROM CTE",
                {'company': company, 'ind_period': indicators_period_value, 'start_date': start_date,
                 'end_date': company_max_date(company)}).all()
            back_date_id = indicator_start_id[0][0]
            if back_date_id <= 0:
                back_date_id = 1
            start_date_indicator = Stock_price.query.with_entities(Stock_price.trade_date).filter(
                Stock_price.id == back_date_id).all()
            print(start_date_indicator[0][0])
            result_for_indicator = Stock_price.query.with_entities(Stock_price.trade_date, Stock_price.open,
                                                                   Stock_price.high, Stock_price.low,
                                                                   Stock_price.close,
                                                                   Stock_price.volume).filter(
                Stock_price.name == company,
                Stock_price.trade_date.between(start_date_indicator[0][0], end_date)).all()
            print(len(result_for_indicator))
            for column, i in zip(price_df.columns, range(len(result_for_indicator))):
                price_df[column] = [x[i] for x in result_for_indicator]
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

            indicators_dict = {'macd': macd_all(price_df, 'Close')}
            price_df[indicator] = indicators_dict[indicator]
            price_df['Date'] = pd.to_datetime(price_df['Date'])
            price_df = price_df[price_df['Date'] >= datetime.strptime(str(start_date), '%Y-%m-%d')]
        else:
            result = Stock_price.query.with_entities(Stock_price.trade_date, Stock_price.open,
                                                Stock_price.high, Stock_price.low, Stock_price.close,
                                                Stock_price.volume).filter(
                Stock_price.name == company, Stock_price.trade_date.between(start_date, end_date)
            ).all()
            for column, i in zip(price_df.columns, range(len(result))):
                price_df[column] = [x[i] for x in result]
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
        print(price_df)
        return price_df.to_json(date_format='iso', orient='split'), interval




    @dashapp.callback(Output('stock_graph', 'figure'),
                      [
                          Input('price_df', 'data'),
                          Input('indicators','value'),
                          Input('interval','value'),
                          Input('stock_dropdown', 'value'),
                          Input('disable_dropdown', 'value'),
                          Input('chart_type_dropdown', 'value'),
                        Input('period_dropdown', 'value')],
                      State('stock_graph', 'figure'))
    def update_figure(price_df, indicator, interval_df, company, enable_value, chart_type,
                      period_value, figure):
        price_df = pd.read_json(price_df, orient='split')
        interval=interval_df

        max_date = (max(price_df['Date']))
        min_date = (min(price_df['Date']))
        max_date_dt = datetime(max_date.year, max_date.month, max_date.day)
        min_date_dt = datetime(min_date.year, min_date.month, min_date.day)


        if enable_value == 'period':
            if chart_type=='candle':

                figure=make_subplot_candle(price_df,company,interval)
                if indicator is not None:
                    figure=make_subplot_candle_indicator(price_df,company,interval,indicator)
                    print(price_df.head())


            else:

                figure = make_subplot_line(price_df,company,interval)

            if period_value <= 12:
                figure.update_xaxes(rangebreaks=[dict(values=diff_dates(price_df, 'Date'))])




        elif enable_value == 'stock_date':

            if chart_type == 'candle':
                figure=make_subplot_candle(price_df,company,interval)
                if indicator is not None:
                    figure=make_subplot_candle_indicator(price_df,company,interval,indicator)


            else:
                figure=make_subplot_line(price_df,company,interval)

            if abs(max_date_dt - min_date_dt).days <= 365:
                figure.update_xaxes(rangebreaks=[dict(values=diff_dates(price_df, 'Date'))])


        else:
            raise PreventUpdate

        return figure






