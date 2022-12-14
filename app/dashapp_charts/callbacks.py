import json

from dash import dash_table
from dash.dependencies import Input, Output, State
from datetime import datetime
from dateutil.relativedelta import relativedelta
from .chart_utils import *
from ..models import Stock_price

from dash.exceptions import PreventUpdate
from talib import *
def register_callbacks(dashapp):
    # function to find days with stock market sessions
    def diff_dates(df, col_date):
        date_list_all = list(datetime_range(min(df[col_date]), max(df[col_date])))
        diff_date = set(date_list_all) - set(df[col_date])
        diff_date_str = list(map(str, diff_date))
        return diff_date_str

    # find latest date with stock quotes for company
    def company_max_date(company):
        company_date = Stock_price.query.with_entities(func.max(Stock_price.trade_date)).filter(
            Stock_price.name == company).first()
        return company_date[0]

    # range between two dates
    def datetime_range(start=None, end=None):
        span = end - start
        for i in range(span.days + 1):
            yield start + timedelta(days=i)
    #resample stock quotes to week or month depend on chosen period
    def period_resample(df, col_date, period):
        df[col_date] = pd.to_datetime(df[col_date])
        df.set_index(col_date, inplace=True)
        df.sort_index(inplace=True)

        logic = {'Open': 'first',
                 'High': 'max',
                 'Low': 'min',
                 'Close': 'last',
                 'Volume': 'sum'}

        dfw = df.resample(period).apply(logic)

        dfw = dfw.reset_index()

        return dfw



    @dashapp.callback([Output('price_df', 'data'),
                       Output('interval','value')],
                        [Input('stock_dropdown', 'value'),
                         Input('indicators','value'),

                       Input('period_dropdown', 'value')])
    #create df with price and optional indicator values
    def make_price_df(company, indicator, period_value):
        price_df = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        start_date_period = company_max_date(company) - relativedelta(months=period_value)

        #dictionary with indicator features needed to calculate indicator column
        if indicator is not None:
            with open('app/dashapp_charts/func_dict.json') as json_file:
                indicators_dict = json.load(json_file)

            print(indicators_dict[indicator]['name'])

            #check period from dropdown and adjust lookback time to calculate indicator without Nan values in chosen period
            if period_value > 12 and period_value <= 60:
                indicators_period_value = indicators_dict[indicator]['period'] * 7
            elif period_value > 60:
                indicators_period_value = indicators_dict[indicator]['period'] * 31
            else:
                indicators_period_value = indicators_dict[indicator]['period']
            #find quotes according to lookback
            indicator_start_id = session.execute(
                "WITH CTE AS (SELECT id, trade_date FROM stock_price WHERE name=:company AND trade_date BETWEEN :start_date AND :end_date FETCH FIRST ROW ONLY ) SELECT id-:ind_period FROM CTE",
                {'company': company, 'ind_period': int(indicators_period_value), 'start_date': start_date_period,
                 'end_date': company_max_date(company)}).fetchall()
            back_date_id = indicator_start_id[0][0]
            if back_date_id <= 0:
                back_date_id = 1
            start_date_indicator = Stock_price.query.with_entities(Stock_price.trade_date).filter(
                Stock_price.id == back_date_id).all()

            result_for_indicator = Stock_price.query.with_entities(Stock_price.trade_date, Stock_price.open,
                                                                   Stock_price.high, Stock_price.low,
                                                                   Stock_price.close,
                                                                   Stock_price.volume).filter(
                Stock_price.name == company,
                Stock_price.trade_date.between(start_date_indicator[0][0], company_max_date(company))).all()
            # fill df from query result to db
            for column, i in zip(price_df.columns, range(len(result_for_indicator))):
                price_df[column] = [x[i] for x in result_for_indicator]
            max_date = (max(price_df['Date']))
            min_date = (min(price_df['Date']))
            max_date_dt = datetime(max_date.year, max_date.month, max_date.day)
            min_date_dt = datetime(min_date.year, min_date.month, min_date.day)
            if (period_value > 12 and period_value <= 60):
                price_df = period_resample(price_df, 'Date', 'W')
                interval = 'Week'
            elif period_value > 60:
                price_df = period_resample(price_df, 'Date', 'M')
                interval = 'Month'

            else:
                interval = 'Day'

            for value, i in zip(indicators_dict[indicator]['cols'], range(len(indicators_dict[indicator]['cols']))):

                cols_to_calc=[]
                # choose df columns to calculate indicator
                for dfcol in indicators_dict[indicator]['args']:
                    col_to_calc=price_df[str(dfcol).capitalize()]
                    cols_to_calc.append(col_to_calc)
                #calculate indicator from talib library
                for j in indicators_dict[indicator]['cols']:
                    if len(indicators_dict[indicator]['cols']) == 1:
                        price_df[str(value).upper()] = globals()[indicators_dict[indicator]['name']](*cols_to_calc)
                    else:
                        price_df[str(value).upper()] = globals()[indicators_dict[indicator]['name']](*cols_to_calc)[i]
            price_df['Date'] = pd.to_datetime(price_df['Date'])
            price_df = price_df[price_df['Date'] >= datetime.strptime(str(start_date_period), '%Y-%m-%d')]
            print(price_df.head())
        else:
            result = Stock_price.query.with_entities(Stock_price.trade_date, Stock_price.open,
                                                     Stock_price.high, Stock_price.low, Stock_price.close,
                                                     Stock_price.volume).filter(
                Stock_price.name == company, Stock_price.trade_date.between(start_date_period, company_max_date(company))
            ).all()
            for column, i in zip(price_df.columns, range(len(result))):
                price_df[column] = [x[i] for x in result]
            max_date = (max(price_df['Date']))
            min_date = (min(price_df['Date']))
            max_date_dt = datetime(max_date.year, max_date.month, max_date.day)
            min_date_dt = datetime(min_date.year, min_date.month, min_date.day)
            if (abs(max_date_dt - min_date_dt).days > 365 and abs(max_date_dt - min_date_dt).days <= 1825) \
                    or (period_value > 12 and period_value <= 60):
                price_df = period_resample(price_df, 'Date', 'W')
                interval = 'Week'
            elif abs(max_date_dt - min_date_dt).days > 1825 or period_value > 60:
                price_df = period_resample(price_df, 'Date', 'M')
                interval = 'Month'

            else:
                interval = 'Day'


        return price_df.to_json(date_format='iso', orient='split'), interval

    @dashapp.callback(Output('stock_graph', 'figure'),
                      [
                          Input('price_df', 'data'),
                          Input('indicators','value'),
                          Input('interval','value'),
                          Input('stock_dropdown', 'value'),
                        Input('chart_type_dropdown', 'value'),
                        Input('period_dropdown', 'value'),
                          Input('memory-table', 'data'),
                          Input('stock_graph', 'clickData'),
                          Input('fibo_dropdown','value')
                      ])

    def update_figure(price_df, indicator, interval_df,company,
                      chart_type,
                      period_value, data, clicked, fibo_value):


        price_df = pd.read_json(price_df, orient='split')
        interval=interval_df

        max_date = (max(price_df['Date']))
        min_date = (min(price_df['Date']))
        max_date_dt = datetime(max_date.year, max_date.month, max_date.day)
        min_date_dt = datetime(min_date.year, min_date.month, min_date.day)



        if chart_type=='candle':

            figure=make_subplot_candle(price_df,company,interval,indicator)

            fibo_levels=[0.236,0.382,0.5,0.618,0.786]
            #create fibonacci retracements
            if len(data)==1:


                if fibo_value=='fibo_retr':
                    figure.add_hline(y=data[0]['y_high'], row=1, col='all', annotation_text='0%')

            elif len(data)==2:

                if fibo_value== 'fibo_retr':
                    figure.add_hline(y=data[0]['y_high'], row=1, col='all',annotation_text='0%')
                    figure.add_hline(y=data[1]['y_low'], row=1, col='all', annotation_text='100%')
                    fib_diff=data[0]['y_high']-data[1]['y_low']
                    for y_line in fibo_levels:
                        figure.add_hline(y=data[0]['y_high']-(fib_diff*y_line),line_dash='dot', row=1, col='all',annotation_text=str(round(y_line*100,1))+"%",

  annotation_position="bottom right")
                    figure.add_scatter(y=[data[0]['y_high'], data[1]['y_low']], x=[data[0]['x'],data[1]['x']], mode='lines', showlegend=False)

            if indicator is not None:
                add_indicator_subplot(figure,price_df)
        else:

            figure = make_subplot_line(price_df,company,interval)
            if indicator is not None:
                add_indicator_subplot(figure, price_df)
        if period_value <= 12:
            figure.update_xaxes(rangebreaks=[dict(values=diff_dates(price_df, 'Date'))])

        return figure

    #capture clicked candles to create fibonacci retracements
    @dashapp.callback(
        Output('click-data','data'),
        Input('stock_graph','clickData'),
        State('click-data','data')
    )
    def on_click(clickedData, points):
        if clickedData is None:
            raise PreventUpdate
        points = points or {'clicks': 0, 'y_high':0, 'y_low':0,'x':0}
        points['clicks'] = points['clicks'] + 1
        points['y_high']= clickedData['points'][0]['high']
        points['y_low'] = clickedData['points'][0]['low']
        points['x'] = clickedData['points'][0]['x']
        print(clickedData)


        return points
    #create dash data table to store clicked candles
    @dashapp.callback(
        Output('memory-table', 'data'),
        Output('stock_graph','clickData'),
        Input('stock_graph', 'clickData'),
        Input('click-data','data'),
        State('memory-table', 'data'),
        State('memory-table', 'columns'),
        Input('fibo_dropdown','value'))

    def add_row(n_clicks, data, rows, columns, fibo_value):

        if n_clicks is not None:

            if fibo_value=='fibo_retr':
                print(fibo_value)
                rows.append({c['id']: data[c['name']] for c in columns})
                if len(rows)>2:
                    rows.clear()
        if fibo_value is None:
            rows.clear()
        return rows, None
    #clear dash table if other company or period is chosen
    @dashapp.callback(Output('fibo_dropdown','value'),
                      Output('count-data', 'children'),

                      Input('stock_dropdown','value'),
                      Input('period_dropdown','value')
                      )

    def clear_fibo(company, period):
        points_df = pd.DataFrame(columns=['clicks', 'y_low', 'y_high', 'x'])
        return "", [dash_table.DataTable(
                        id='memory-table',
                        columns=[{
                            'name': i,
                            'id': i,
                            'deletable': True,
                            'renamable': True
                        } for i in points_df.columns],
                        data=[
                        ],
                        editable=True,
                        row_deletable=True,


                    )]
    #not use fibonacci retracements features with line chart
    @dashapp.callback(Output('fibo_div','hidden'),
                      Input('chart_type_dropdown','value'))
    def hide_fibo_line_chart(chart_type):
        if chart_type=='line':
            return True

    # show hint to create fibonacci retracements
    @dashapp.callback(Output('fibo_low_desc', 'hidden'),
                      Output('fibo_high_desc', 'hidden'),
                        Input('fibo_dropdown', 'value'),
                      Input('memory-table','data'))
    def show_fibo_low_desc(fibo_value,data):
        if fibo_value=='fibo_retr' and len(data)==0:
            return False, True

        elif fibo_value == 'fibo_retr' and len(data) == 1:
            return True,False
        else:
            return True, True















