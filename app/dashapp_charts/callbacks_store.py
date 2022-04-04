

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
                       Input(component_id='start_date', component_property='date'),
                       Input(component_id='end_date', component_property='date'),

                       Input('period_dropdown', 'value'),
                       Input('disable_dropdown', 'value')])
    def make_price_df(company, start_date, end_date, period_value, enable_value):
        price_df = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        interval=''
        if enable_value == 'stock_date':


                candle_result = Stock_price.query.with_entities(Stock_price.trade_date, Stock_price.open,
                                                            Stock_price.high, Stock_price.low, Stock_price.close,
                                                            Stock_price.volume).filter(
                Stock_price.name == company, Stock_price.trade_date.between(start_date, end_date)
            ).all()
                for column, i in zip(price_df.columns, range(len(candle_result))):
                    price_df[column] = [x[i] for x in candle_result]

        else:
            price_df = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
            start_date_period = company_max_date(company) - relativedelta(months=period_value)
            candle_result = Stock_price.query.with_entities(Stock_price.trade_date, Stock_price.open,
                                                            Stock_price.high, Stock_price.low,
                                                            Stock_price.close, Stock_price.volume).filter(
                Stock_price.name == company,
                Stock_price.trade_date.between(start_date_period, company_max_date(company))
            ).all()
            for column, i in zip(price_df.columns, range(len(candle_result))):
                price_df[column] = [x[i] for x in candle_result]


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

                          Input('interval','value'),
                          Input('stock_dropdown', 'value'),
                          Input('disable_dropdown', 'value'),
                          Input('chart_type_dropdown', 'value'),
                        Input('period_dropdown', 'value')],
                      State('stock_graph', 'figure'))
    def update_figure(price_df, interval_df, company, enable_value, chart_type,
                      period_value, figure):
        price_df = pd.read_json(price_df, orient='split')
        interval=interval_df
        date_list_all = list(datetime_range(min(price_df['Date']), max(price_df['Date'])))
        diff_date = set(date_list_all) - set(price_df['Date'])
        diff_date_str = list(map(str, diff_date))
        max_date = (max(price_df['Date']))
        min_date = (min(price_df['Date']))
        max_date_dt = datetime(max_date.year, max_date.month, max_date.day)
        min_date_dt = datetime(min_date.year, min_date.month, min_date.day)


        if enable_value == 'period':


            if chart_type == 'candle':



                figure = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                       vertical_spacing=0.1,
                                       subplot_titles=(str(company) + ' ' + interval, 'Volume'),
                                       row_width=[0.2, 0.7])
                figure.add_trace(go.Candlestick(
                    x=price_df['Date'],
                    open=price_df['Open'],
                    high=price_df['High'],
                    low=price_df['Low'],
                    close=price_df['Close']

                ))
                figure.add_trace(go.Bar(x=price_df['Date'], y=price_df['Volume'], showlegend=False), row=2,
                                 col=1)
                figure.update_xaxes(range=update_xaxes_range(price_df, 'Date'))
                if period_value <= 12:
                    figure.update_xaxes(rangebreaks=[dict(values=diff_date_str)])
                    figure.update_layout(title=str(company) + ' ' + interval, xaxis_rangeslider_visible=False)
                else:
                    figure.update_layout(title=str(company) + ' ' + interval, xaxis_rangeslider_visible=False)






            else:

                figure = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                       vertical_spacing=0.1,
                                       subplot_titles=(str(company) + ' ' + interval, 'Volume'),
                                       row_width=[0.2, 0.7])

                figure.add_trace(go.Scatter(
                    x=price_df['Date'],
                    y=price_df['Close']

                ))
                figure.add_trace(go.Bar(x=price_df['Date'], y=price_df['Volume'], showlegend=False), row=2,
                                 col=1)
                if period_value<=12:
                    figure.update_xaxes(rangebreaks=[dict(values=diff_date_str)])
                figure.update_xaxes(range=update_xaxes_range(price_df, 'Date'))
                print(update_xaxes_range(price_df, 'Date'))
        elif enable_value == 'stock_date':

            if chart_type == 'candle':

                price_df['Date'] = pd.to_datetime(price_df['Date'])

                figure = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                       vertical_spacing=0.1,
                                       subplot_titles=(str(company) + ' ' + interval, 'Volume'),
                                       row_width=[0.2, 0.7])
                figure.add_trace(go.Candlestick(
                    x=price_df['Date'],
                    open=price_df['Open'],
                    high=price_df['High'],
                    low=price_df['Low'],
                    close=price_df['Close']

                ))
                figure.add_trace(go.Bar(x=price_df['Date'], y=price_df['Volume'], showlegend=False), row=2,
                                 col=1)
                figure.update_xaxes(range=update_xaxes_range(price_df, 'Date'))
                if abs(max_date_dt - min_date_dt).days <= 365:
                    figure.update_xaxes(rangebreaks=[dict(values=diff_date_str)])
                figure.update_layout(title=str(company) + ' ' + interval, xaxis_rangeslider_visible=False)

            elif chart_type == 'line':
                price_df['Date'] = pd.to_datetime(price_df['Date'])

                figure = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                       vertical_spacing=0.1,
                                       subplot_titles=(str(company) + ' ' + interval, 'Volume'),
                                       row_width=[0.2, 0.7])

                figure.add_trace(go.Scatter(
                    x=price_df['Date'],
                    y=price_df['Close']

                ))
                figure.add_trace(go.Bar(x=price_df['Date'], y=price_df['Volume'], showlegend=False), row=2,
                                 col=1)
                if abs(max_date_dt - min_date_dt).days <= 365:
                    figure.update_xaxes(rangebreaks=[dict(values=diff_date_str)])
                figure.update_xaxes(range=update_xaxes_range(price_df, 'Date'))
                print(update_xaxes_range(price_df, 'Date'))
        else:
            raise PreventUpdate

        return figure






