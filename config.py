import os

class BaseConfig:
    SQLALCHEMY_DATABASE_URI='postgresql://postgres:postgres@localhost:5432/stock'
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    SECRET_KEY='_Zm9ke_XdcuJ3_qP2VEe1wc0AljgrI3YJVnafjqKPFI='