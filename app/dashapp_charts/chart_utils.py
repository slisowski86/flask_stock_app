from sqlalchemy import func

from app.extensions import db
import psycopg2
from config import BaseConfig
from ..models import Stock_price, Company




def companies_list():
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

    unzipped_list = [x[0] for x in result_stock_list]
    return unzipped_list
