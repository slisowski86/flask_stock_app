import psycopg2
from config import BaseConfig
from dash import dcc, html, Dash, dash
import plotly.express as px
from dash.dependencies import Input, Output
import pandas as pd
try:
    conn = psycopg2.connect(BaseConfig.SQLALCHEMY_DATABASE_URI, sslmode='require')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name From company")
    result_stock_list = cursor.fetchall()
except psycopg2.DatabaseError as error:
    print(error)
finally:
    if conn is not None:
        conn.close()



unzipped_list=[x[0] for x in result_stock_list]



print(unzipped_list)


layout=html.Div(
    children=[
        html.H3("Stock price charts"),
        dcc.Dropdown(unzipped_list, None, id="stock_dropdown"),

        dcc.Graph(id='stock_graph')],
    style={'height':800,'width':800})
