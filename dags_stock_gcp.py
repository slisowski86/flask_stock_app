import requests
import pandas as pd
import csv

from datetime import datetime, date, timedelta
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from sqlalchemy import Column, Integer, String, Float, Date, BigInteger
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os

app = Flask(__name__)
DB_URL='postgresql://postgres:postgres@34.116.143.217:5432/wig20'
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
db = SQLAlchemy(app)



class Stock_price(db.Model):
    id=Column(Integer, autoincrement=True, primary_key=True)
    short_name=Column(String, primary_key=True)
    name=Column(String)
    trade_date=Column(Date, primary_key=True)
    open=Column(Float)
    high=Column(Float)
    low=Column(Float)
    close=Column(Float)
    volume=Column(Integer)

    def __repr__(self):
        return "<Stock_price(short_name=' %s', name=' %s', trade_date=' %s', open=' %f', high=' %f', low=' %f', close=' %f', volume= '%d')>"\
               % (self.short_name, self.name, self.trade_date, self.open, self.high, self.low, self.close, self.volume)

class Company(db.Model):
    id=Column(Integer, autoincrement=True, primary_key=True)
    short_name=Column(String)
    name=Column(String)

    def __repr(self):
        return "<Company(short_name=' %s', name=' %s')>"%(self.short_name, self.name)


STOCK_PRICES_URL = 'https://stooq.pl/q/d/l/'
WIG20_URL = 'https://www.biznesradar.pl/spolki-wskazniki-wartosci-rynkowej/indeks:WIG20'
STOCK_PRICES_URL = 'https://stooq.pl/q/d/l/'


DEFAULT_ARGS = {
    'owner': 'Airflow',
    'depends_on_past': False,

}

dag = DAG('etl_stock_price',
          default_args=DEFAULT_ARGS,
          start_date=datetime(2022, 4, 28),
          schedule_interval='0 16 * * *',
	  #schedule_interval=None
          
          )


def extract_names(df, colname):
    name_list = []
    for s in df[colname]:
        if str(s).endswith(")"):
            name_list.append(str(s).split(" ")[1].replace("(", "").replace(")", ""))
        else:
            name_list.append(str(s))
    return name_list


def extract(**kwargs):
    ti = kwargs['ti']
    companies_list = pd.read_html(WIG20_URL, attrs={'class': 'qTableFull'}, flavor='bs4')
    companies = pd.DataFrame(companies_list[0])
    names = extract_names(companies, "Profil")
    short_list = companies["Profil"].str.replace(r"\(.*\)", "").str.strip()
    company_names = dict(zip(short_list, names))
    ti.xcom_push('company_data', company_names)


def transform(**kwargs):
    start_date=db.session.execute("SELECT max(trade_date) FROM stock_price").fetchall()
    start_date=start_date[0][0]
    start_date=start_date+timedelta(days=1)
    ti = kwargs['ti']
    company_data = ti.xcom_pull(task_ids='extract', key='company_data')
    stock_df = pd.DataFrame()
    short_names, names = zip(*company_data.items())
    cols = ['trade_date', 'open', 'high', 'low', 'close', 'volume']
    for short_name, name in zip(short_names, names):
        params = {'s': str(short_name).lower(), 'd1': str(start_date).replace('-',''), 			'd2':str(date.today()).replace('-',''), 'i': 'd'}
        response = requests.get(STOCK_PRICES_URL, params=params)
        data = pd.read_csv(response.url, skiprows=[0], names=cols)

        data.insert(0, 'short_name', short_name)
        data.insert(1, 'name', name)
        stock_df = pd.concat([stock_df, data])
    stock_df.fillna(0)
    stock_df['volume'] = stock_df['volume'].astype('int')
    stock_prices = stock_df.to_dict('records')
    companies_dict={'short_name': short_names, 'name': names}
    companies_df=pd.DataFrame(companies_dict)
    companies_to_load=companies_df.to_dict('records')
    ti.xcom_push('companies_dataframe', companies_to_load)
    ti.xcom_push('stock_dataframe', stock_prices)


def load(**kwargs):
    ti = kwargs['ti']
    stock_data_to_load = ti.xcom_pull(task_ids='transform', key='stock_dataframe')
    companies_to_load = ti.xcom_pull(task_ids='transform', key='companies_dataframe')
    Company.__table__.drop(db.engine)
    Company.__table__.create(db.engine)
    companies_to_add=[]	
    prices_to_add = []
    
    for i in range(len(stock_data_to_load)):
        price = Stock_price(**stock_data_to_load[i])
        print(price.short_name)
        prices_to_add.append(price)
    for i in range(len(companies_to_load)):
        company= Company(**companies_to_load[i])
        companies_to_add.append(company)
    
    print(prices_to_add)	
    db.session.bulk_save_objects(prices_to_add)
    db.session.commit()
    db.session.bulk_save_objects(companies_to_add)
    db.session.commit()


extract_task = PythonOperator(
    task_id='extract',
    python_callable=extract,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='transform',
    python_callable=transform,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load',
    python_callable=load,
    dag=dag,
)

extract_task >> transform_task >> load_task
