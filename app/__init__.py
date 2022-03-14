import dash
from flask import Flask
from flask.helpers import get_root_path

from app.dashapp_charts.callbacks import register_callbacks
from config import BaseConfig
from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

def create_app():
    app=Flask(__name__)

    @app.route("/")
    def hello_world():
        return "<p>Hello, World!</p>"
    app.config.from_object(BaseConfig)
    db.init_app(app)
    register_dashapps(app)


    return app




def register_dashapps(app_name):
    from app.dashapp_charts.layout import layout



    meta_viewport = {
        "name": "viewport",
        "content": "width=device-width, initial-scale=1, shrink-to-fit=no"}

    dashapp1 = dash.Dash(__name__,
                         server=app_name,
                         url_base_pathname='/dashboard/',
                         assets_folder=get_root_path(__name__) + '/dashboard/assets/',
                         meta_tags=[meta_viewport])

    with app_name.app_context():
        dashapp1.title = 'Dashapp 1'
        dashapp1.layout = layout
        register_callbacks(dashapp1)

