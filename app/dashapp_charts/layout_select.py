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
meta = [
    html.Div(
        id="no-display",
        children=[
            # Store for user created masks
            # data is a list of dicts describing shapes
            dcc.Store(id="price_df"),
            dcc.Store(id="interval"),
            dcc.Store(id='click-data')


        ],
    )
]

sidebar = [
    dbc.Card(
        id="sidebar-card",
        children=[
            dbc.CardHeader("Tools"),
            dbc.CardBody(
                [

        html.H3("Stock price charts"),
        html.Div(className='div-for-dropdown',children=[dcc.Dropdown(companies_list(),value=companies_list()[0], id="stock_dropdown")]),
        html.Div(id='period_label',children=[html.Label('Choose period')], style={'width':'40%'}),

        html.Div(className='div-for-periods',children=[

        dcc.Dropdown(id='period_dropdown',options=[
            {'label':'1m','value':1},
            {'label':'3m','value':3},
            {'label':'6m','value':6},
            {'label':'1y','value':12},
            {'label':'3y','value':36},
            {'label':'5y','value':60},
            {'label':'10y','value':120},
            {'label':'20y', 'value': 240}
        ],value=1),

        ], style={'width':'50%','display':'inline-block'}),
        html.Div(id='additional_options',children=[
            html.Label("Choose chart type"),
            dcc.Dropdown(id='chart_type_dropdown',options=[
                {'label':'line','value':'line'},
                {'label':'candlestick','value':'candle'}
            ], value='candle'),
            html.Label('Choose indicator'),
        dcc.Dropdown(id='indicators',options=[
                {'label':'MACD','value':'macd'},
                {'label':'RSI','value':'rsi'},
            {'label':'ADX','value':'adx'},
            {'label':'BOP','value':'bop'}

            ])



        ],style={'padding-top':'30px','width':'40%'}),
            html.Div(id='fib-data', children=[])


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

                                                   config={
                                                       "modeBarButtonsToAdd": [
                                                           "drawrect",
                                                           "drawline",
                                                           "drawopenpath",
                                                           "eraseshape",
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
                children=[dbc.Col(sidebar, md=4), dbc.Col(chart, md=8)]),
        dbc.Row(dbc.Col(meta)),
    ], fluid=True
    ),



])