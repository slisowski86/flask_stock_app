import psycopg2

import app
from config import BaseConfig
from dash import dcc, html, Dash, dash
import plotly.express as px
from dash.dependencies import Input, Output
import pandas as pd


def register_callbacks(dashapp):
    @dashapp.callback(
        Output(component_id='stock_graph', component_property='figure'),
        Input(component_id='stock_dropdown', component_property='value')
    )

    def update_stock_graph(company):
        price_df = pd.DataFrame(columns=["trade_date", "close"])
        result = []
        date_1='2021-06-01'
        date_2='2022-03-08'
        try:
            conn = psycopg2.connect(BaseConfig.SQLALCHEMY_DATABASE_URI, sslmode='require')
            cursor = conn.cursor()
            cursor.execute(
            "SELECT trade_date, close FROM stock_price WHERE name=%s AND trade_date BETWEEN %s AND %s",[company,date_1,date_2])
            result = cursor.fetchall()


        except psycopg2.DatabaseError as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

        price_df["trade_date"] = [x[0] for x in result]
        price_df["close"] = [x[1] for x in result]
        fig = px.line(data_frame=price_df, x="trade_date", y="close", title=str(company))
        return fig
