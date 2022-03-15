from sqlalchemy import func
from flask import Blueprint
from app.extensions import db
import psycopg2
from config import BaseConfig
from ..models import Stock_price, Company
import plotly.express as px
from config import BaseConfig
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import create_app, db
import pandas as pd




engine=create_engine(BaseConfig.SQLALCHEMY_DATABASE_URI)

def companies_list():


    #try:
        #conn = psycopg2.connect(BaseConfig.SQLALCHEMY_DATABASE_URI, sslmode='require')
        #cursor = conn.cursor()
        #cursor.execute(
            #"SELECT name From company")
        #result_stock_list = cursor.fetchall()
    #except psycopg2.DatabaseError as error:
        #print(error)
    #finally:
        #if conn is not None:
            #conn.close()
    Session = sessionmaker(bind=engine)
    session = Session()
    result_stock_list = session.query(Company.name).all()

    unzipped_list = [x[0] for x in result_stock_list]
    return unzipped_list

def start_graph():
    price_df = pd.DataFrame(columns=["trade_date", "close"])
    Session = sessionmaker(bind=engine)
    session = Session()
    result_graph= session.query(Stock_price.trade_date, Stock_price.close).filter(Stock_price.name=='wig20').all()
    price_df["trade_date"] = [x[0] for x in result_graph]
    price_df["close"] = [x[1] for x in result_graph]
    fig = px.line(data_frame=price_df, x="trade_date", y="close", title='WIG 20')
    return fig