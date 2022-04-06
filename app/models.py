from sqlalchemy import Column, Integer, String, Float, Date
from app.extensions import db

class Stock_price(db.Model):
    id = Column(Integer, autoincrement=True, primary_key=True)
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
