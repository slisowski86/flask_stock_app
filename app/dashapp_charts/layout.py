from dash import dcc, html, Dash, dash

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from config import BaseConfig
from ..models import Company, Stock_price
from sqlalchemy import func
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go



def companies_list():
    engine=create_engine(BaseConfig.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    result_stock_list = session.query(Company.name).all()
    companies_list = [x[0] for x in result_stock_list]
    return companies_list

def min_date():
    engine = create_engine(BaseConfig.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    min_date=session.query(func.min(Stock_price.trade_date)).first()
    min_date=min_date[0]
    return min_date

def max_date():
    engine = create_engine(BaseConfig.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    max_date=session.query(func.max(Stock_price.trade_date)).first()
    max_date=max_date[0]
    return max_date

def make_default_graph():
    fig=go.Figure()
    fig.update_xaxes(range=[0,18])
    fig.add_trace(
        go.Scatter(
            x=[1,2,3,4,5],
            y=[5,1,4,1,5],
            mode="lines",
            line=dict(color='royalblue', width=4),
            showlegend=False)
        )
    fig.add_trace(
        go.Scatter(
            x=[6,6],
            y=[1,5],
            mode="lines",
            line=dict(color='royalblue', width=4),
            showlegend=False)
    )
    fig.add_trace(
        go.Scatter(
            x=[8,9,9,7,7,9,9],
            y=[3,3,1,1,5,5,4],
            mode="lines",
            line=dict(color='royalblue', width=4),
            showlegend=False)
    )
    fig.add_trace(
        go.Scatter(
            x=[11,11,13,13,11,11,13],
            y=[4, 5, 5, 3, 2, 1, 1],
            mode="lines",
            line=dict(color='royalblue', width=4),
            showlegend=False)
    )
    fig.add_trace(
        go.Scatter(
            x=[14, 14, 16, 16, 14],
            y=[1, 5, 5, 1, 1],
            mode="lines",
            line=dict(color='royalblue', width=4),
            showlegend=False)
    )


    return fig




button_gitlab = dbc.Button(
    "View Code on gitlab",
    outline=True,
    color="primary",
    href="https://gitlab.com/slisowski/flask_stock_app",
    id="gh-link",
    style={"text-transform": "none"},
)

header=header = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [

                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.H3("WIG 20 Stock Poland"),
                                    html.P("Charts"),
                                ],
                                id="app-title",
                            )
                        ],
                        md=True,
                        align="center",
                    ),
                ],
                align="center",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.NavbarToggler(id="navbar-toggler"),
                            dbc.Collapse(
                                dbc.Nav(
                                    [

                                        dbc.NavItem(button_gitlab),
                                    ],
                                    navbar=True,
                                ),
                                id="navbar-collapse",
                                navbar=True,
                            ),

                        ],
                        md=2,
                    ),
                ],
                align="center",
            ),
        ],
        fluid=True,
    ),
    dark=True,
    color="dark",
    sticky="top",
)

sidebar = [
    dbc.Card(
        id="sidebar-card",
        children=[
            dbc.CardHeader("Tools"),
            dbc.CardBody(
                [
        dcc.Store(id='stock_memory'),
        html.H3("Stock price charts"),
        html.Div(className='div-for-dropdown',children=[dcc.Dropdown(companies_list(), None, id="stock_dropdown", style={'width':300})]),

        dcc.DatePickerSingle(id="start_date",
            min_date_allowed=min_date(),
            max_date_allowed=max_date(),
            initial_visible_month=min_date(),
            date=min_date()
        ),
        dcc.DatePickerSingle(id="end_date",
            min_date_allowed=min_date(),
            max_date_allowed=max_date(),
            initial_visible_month=max_date(),
            date=max_date()
        ),
        html.Button('Show chart', id='show', n_clicks=0)

                ])])]

chart = [
    dbc.Card(
        id="segmentation-card",
        children=[
            dbc.CardHeader("Viewer"),
            dbc.CardBody(
                [
                    html.Div(
                        id="transparent-loader-wrapper",
                        children=[
                            dcc.Loading(
                                id="chart-loading",
                                type="default",
                                children=dcc.Graph(id='stock_graph',
                                                   figure=make_default_graph(),
                                                   config={
                                                       "modeBarButtonsToAdd": [
                                                           "drawrect",
                                                           "drawline",
                                                           "drawopenpath",
                                                           "eraseshape",
                                                       ],
                                                       "modeBarButtonsToRemove":[
                                                           "resetScale"
                                                       ],
                                                       'displaylogo':False
                                                   },
                                                   )
                            )
                        ]
                    )
                ])])]


layout=html.Div(children=[
    header,
    dbc.Container(
    [
        dbc.Row(id="app-content",
                children=[dbc.Col(sidebar, md=4), dbc.Col(chart, md=8)])
    ], fluid=True
    ),



])