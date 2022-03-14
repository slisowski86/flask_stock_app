import dash
from flask import Flask
from flask.helpers import get_root_path

from app.dashapp_charts.callbacks import register_callbacks
from config import BaseConfig
from flask_sqlalchemy import SQLAlchemy
from app.extensions import db



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

    dashapp_charts = dash.Dash(__name__,
                         server=app_name,
                         url_base_pathname='/dashboard/',
                         meta_tags=[meta_viewport])

    with app_name.app_context():
        dashapp_charts.title = 'WIG20 Charts'
        dashapp_charts.layout = layout
        register_callbacks(dashapp_charts)

