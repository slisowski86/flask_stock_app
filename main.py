import os
from cryptography.fernet import Fernet
from sqlalchemy import func
import base64
from app.extensions import db
from app.models import Stock_price
from app import create_app
key=Fernet.generate_key()
print(key)
for x in os.environ:
    print((x, os.getenv(x)))
app=create_app()
date_min=None
#with app.app_context():
    #date_min=Stock_price.query.with_entities(func.max(Stock_price.trade_date)).first()
basedir=os.path.abspath(os.path.dirname(__file__))
print(basedir)
environment=os.environ.get('SECRET_KEY')
print(environment)

print(date_min[0])