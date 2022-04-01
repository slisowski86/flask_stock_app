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




def register_callbacks(dashapp):
    @dashapp.callback(
        Output(component_id='stock_graph', component_property='figure'),

        [Input('stock_dropdown','value'),
        Input(component_id='start_date', component_property='date'),
        Input(component_id='end_date', component_property='date'),
        Input('disable_dropdown','value'),
        Input('period_dropdown','value'),
         Input('chart_type_dropdown','value')],
         State('stock_graph','figure')


    )

    def update_stock_graph( company, start_date, end_date, radio_value, period_value, chart_type, figure):

        if radio_value=='stock_date':
            candle_price_df=pd.DataFrame(columns=['Date','Open','High','Low','Close'])
            if chart_type=='candle':
                candle_result=Stock_price.query.with_entities(Stock_price.trade_date,Stock_price.open,
                                                              Stock_price.high,Stock_price.low,Stock_price.close).filter(
                    Stock_price.name==company, Stock_price.trade_date.between(start_date,end_date)
                ).all()
                for column, i in zip(candle_price_df.columns, range(len(candle_result))):
                    candle_price_df[column] = [x[i] for x in candle_result]

                figure=go.Figure(go.Candlestick(
                    x=candle_price_df['Date'],
                    open=candle_price_df['Open'],
                    high=candle_price_df['High'],
                    low=candle_price_df['Low'],
                    close=candle_price_df['Close']
                ))
                company_min_date = Stock_price.query.with_entities(func.min(Stock_price.trade_date)).filter(
                    Stock_price.name == company).first()
                company_min_date = company_min_date[0]
                xaxis_start_date = company_min_date

                if datetime.strptime(start_date, '%Y-%m-%d') > datetime.strptime(str(company_min_date), '%Y-%m-%d'):
                    xaxis_start_date = start_date
                delta_days = (datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(str(xaxis_start_date),
                                                                                          '%Y-%m-%d')).days
                xaxis_end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=delta_days / 20)

                figure.update_layout(xaxis=dict(range=[xaxis_start_date, xaxis_end_date]))
                return figure

            price_df = pd.DataFrame(columns=["trade_date", "close"])
            result = Stock_price.query.with_entities(Stock_price.trade_date, Stock_price.close).filter(
            Stock_price.name == company, Stock_price.trade_date.between(start_date, end_date))
            price_df["trade_date"] = [x[0] for x in result]
            price_df["close"] = [x[1] for x in result]
            figure = px.line(data_frame=price_df, x="trade_date", y="close", title=str(company))
            company_min_date=Stock_price.query.with_entities(func.min(Stock_price.trade_date)).filter(Stock_price.name==company).first()
            company_min_date=company_min_date[0]
            xaxis_start_date=company_min_date


            if datetime.strptime(start_date,'%Y-%m-%d')>datetime.strptime(str(company_min_date),'%Y-%m-%d'):
                xaxis_start_date=start_date
            delta_days = (datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(str(xaxis_start_date), '%Y-%m-%d')).days
            xaxis_end_date=datetime.strptime(end_date, '%Y-%m-%d')+timedelta(days=delta_days/20)

            figure.update_layout(xaxis=dict(range=[xaxis_start_date,xaxis_end_date]))
            return figure


        elif radio_value == 'period':
            if period_value=='max':
                candle_price_df = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close'])
                if chart_type == 'candle':
                    candle_result = Stock_price.query.with_entities(Stock_price.trade_date, Stock_price.open,
                                                                    Stock_price.high, Stock_price.low,
                                                                    Stock_price.close).filter(
                        Stock_price.name == company, Stock_price.trade_date.between(start_date, end_date)
                    ).all()
                    for column, i in zip(candle_price_df.columns, range(len(candle_result))):
                        candle_price_df[column] = [x[i] for x in candle_result]

                    figure = go.Figure(go.Candlestick(
                        x=candle_price_df['Date'],
                        open=candle_price_df['Open'],
                        high=candle_price_df['High'],
                        low=candle_price_df['Low'],
                        close=candle_price_df['Close']
                    ))
                    company_max_date = Stock_price.query.with_entities(func.max(Stock_price.trade_date)).filter(
                        Stock_price.name == company).first()
                    company_min_date = Stock_price.query.with_entities(func.min(Stock_price.trade_date)).filter(
                        Stock_price.name == company).first()
                    delta_days = (company_max_date[0] - company_min_date[0]).days

                    xaxis_end_date = company_max_date[0] + timedelta(days=delta_days / 20)
                    figure.update_layout(xaxis=dict(range=[company_min_date[0], xaxis_end_date]))
                    return figure

                price_df = pd.DataFrame(columns=["trade_date", "close"])
                company_max_date = Stock_price.query.with_entities(func.max(Stock_price.trade_date)).filter(
                    Stock_price.name == company).first()
                company_min_date = Stock_price.query.with_entities(func.min(Stock_price.trade_date)).filter(
                    Stock_price.name == company).first()
                result = Stock_price.query.with_entities(Stock_price.trade_date, Stock_price.close).filter(
                    Stock_price.name == company, Stock_price.trade_date.between(company_min_date[0], company_max_date[0]))
                price_df["trade_date"] = [x[0] for x in result]
                price_df["close"] = [x[1] for x in result]
                delta_days = (company_max_date[0] - company_min_date[0]).days

                xaxis_end_date = company_max_date[0] + timedelta(days=delta_days / 20)

                figure = px.line(data_frame=price_df, x="trade_date", y="close", title=str(company))
                figure.update_layout(xaxis=dict(range=[company_min_date[0], xaxis_end_date]))
                return figure

            else:
                candle_price_df = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close'])
                if chart_type == 'candle':
                    candle_result = Stock_price.query.with_entities(Stock_price.trade_date, Stock_price.open,
                                                                    Stock_price.high, Stock_price.low,
                                                                    Stock_price.close).filter(
                        Stock_price.name == company, Stock_price.trade_date.between(start_date, end_date)
                    ).all()
                    for column, i in zip(candle_price_df.columns, range(len(candle_result))):
                        candle_price_df[column] = [x[i] for x in candle_result]

                    figure = go.Figure(go.Candlestick(
                        x=candle_price_df['Date'],
                        open=candle_price_df['Open'],
                        high=candle_price_df['High'],
                        low=candle_price_df['Low'],
                        close=candle_price_df['Close']
                    ))
                    company_max_date = Stock_price.query.with_entities(func.max(Stock_price.trade_date)).filter(
                        Stock_price.name == company).first()
                    start_date_period = company_max_date[0] - relativedelta(months=period_value)
                    company_min_date = Stock_price.query.with_entities(func.min(Stock_price.trade_date)).filter(
                        Stock_price.name == company).first()
                    delta_days = (company_max_date[0] - start_date_period).days

                    xaxis_end_date = company_max_date[0] + timedelta(days=delta_days / 20)
                    if start_date_period < company_min_date[0]:
                        figure.update_layout(xaxis=dict(range=[company_min_date[0], xaxis_end_date]))
                    else:
                        figure.update_layout(xaxis=dict(range=[start_date_period, xaxis_end_date]))
                    return figure
                price_df = pd.DataFrame(columns=["trade_date", "close"])
                company_max_date=Stock_price.query.with_entities(func.max(Stock_price.trade_date)).filter(Stock_price.name==company).first()
                start_date_period=company_max_date[0]-relativedelta(months=period_value)
                company_min_date=Stock_price.query.with_entities(func.min(Stock_price.trade_date)).filter(Stock_price.name==company).first()
                result = Stock_price.query.with_entities(Stock_price.trade_date, Stock_price.close).filter(
                Stock_price.name == company, Stock_price.trade_date.between(start_date_period,company_max_date[0]))
                price_df["trade_date"] = [x[0] for x in result]
                price_df["close"] = [x[1] for x in result]
                delta_days=(company_max_date[0]-start_date_period).days

                xaxis_end_date=company_max_date[0]+timedelta(days=delta_days/20)

                figure = px.line(data_frame=price_df, x="trade_date", y="close", title=str(company))
                if start_date_period<company_min_date[0]:
                    figure.update_layout(xaxis=dict(range=[company_min_date[0], xaxis_end_date]))
                else:
                    figure.update_layout(xaxis=dict(range=[start_date_period, xaxis_end_date]))
                return figure
        else:
            raise dash.exceptions.PreventUpdate




    @dashapp.callback(Output('period_dropdown','disabled'),
                      Input('disable_dropdown','value'))
    def disable_dropdown(disable_value):
        if disable_value=='period':
            return False
        else:
            return True

    @dashapp.callback([Output('start_date', 'disabled'),
                       Output('end_date','disabled')],
                    Input('disable_dropdown', 'value'))
    def disable_dropdown(disable_value):
        if disable_value == 'stock_date':
            return False, False
        else:
            return True, True



                #children.append(dcc.Graph(figure=fig))









