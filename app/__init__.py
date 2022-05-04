import dash
from flask import Flask
from app.config import BaseConfig
import dash_bootstrap_components as dbc

from app.extensions import db
import os
#assets_path = os.getcwd() +'/dashapp_charts/assets'
assets_path = 'app/dashapp_charts/assets'
print(assets_path)


def create_app():
    server=Flask(__name__)


    server.config.from_object(BaseConfig)
    db.init_app(server)
    register_dashapps(server)
    register_blueprints(server)


    return server




def register_dashapps(server):
    from app.dashapp_charts.layout import layout
    from app.dashapp_charts.callbacks import register_callbacks




    meta_viewport = {
        "name": "viewport",
        "content": "width=device-width, initial-scale=1, shrink-to-fit=no"}
    external_stylesheets = [dbc.themes.BOOTSTRAP, "/home/slisowski/PycharmProjects/flask_stock_app/app/dashapp_charts/assets/style.css"]
    dashapp_charts = dash.Dash(__name__,
                         server=server,
                        external_stylesheets=external_stylesheets,
                        assets_folder='/home/slisowski/PycharmProjects/flask_stock_app/app/dashapp_charts/assets',
                         url_base_pathname='/',
                         meta_tags=[meta_viewport])

    with server.app_context():
        dashapp_charts.title = 'WIG20 Charts'
        dashapp_charts.layout = layout
        register_callbacks(dashapp_charts)




def register_blueprints(server):
    from app.views import server_bp
    server.register_blueprint(server_bp)