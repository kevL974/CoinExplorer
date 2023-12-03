import dash
from dash import Dash, dcc, html, Input, Output, ctx, callback,State
import plotly.graph_objects as go
from datetime import  date
import dash_bootstrap_components as dbc
from opa.storage.connector import  HbaseTableConnector

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container(
    [
        dcc.Markdown('## **CryptoBot avec Binance** ',style={'textAlign': 'center','justification' : 'center', 'color': 'mediumturquoise','height':60,'background':' #4B5F63'}),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Markdown('Choix de la date ',style={'textAlign': 'center', 'color': 'mediumturquoise','width': '100%','background': '#4B5F63'}),
                    ],
                ),
                dbc.Col(
                    [
                        dcc.Markdown('Choix de la monnaie ',style={'textAlign': 'center', 'color': 'mediumturquoise','width': '100%','background': '#4B5F63'}),
                    ]
                ),
                dbc.Col(
                    [
                        dcc.Markdown('Choix de la périodicité' ,style={'textAlign': 'center', 'color': 'mediumturquoise','width': '100%','background': '#4B5F63'}),
                    ]
                ),

            ]),

        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Row(
                    [
                        dcc.DatePickerRange(
                            id='interval_date',
                            min_date_allowed=date(2017, 8, 1),
                            initial_visible_month=date(2023, 12, 1),
                            start_date=date(2023, 9, 1),
                            end_date=date(2023, 12, 1),
                            display_format='DD MMM YY',
                        ),
                        html.Div(id='output-container-date-picker-range'),
                    ],
                        ),
                    ],className="d-flex justify-content-center align-items-stretch"),
                dbc.Col(
                    [
                        dcc.RadioItems(['BTCUSDT', 'ETHBTC'], 'BTCUSDT',id='symbol_radio', inline=False),
                    ],className="d-flex justify-content-center align-items-stretch"
                ),
                dbc.Col(
                    [
                        dcc.RadioItems(options= {"1m":'1 minute', "3m":'3 minutes', "5m":'5 minutes', "15m":'15 minutes',"30m": '30 minutes'}, id='interval_radio',value='15m', inline=False),
                    ],className="d-flex justify-content-center align-items-stretch"
                ),

            ]),
        html.Div([
            dbc.Button("Lancer la requete","button", active='True', value=['True']),
            ],className="d-flex justify-content-center "),

        dbc.Row(
            [
                dcc.Graph(id='graph', style={'textAlign': 'center', 'color': 'mediumturquoise','width': '100%','background': '#4B5F63'}),
            ],className="d-flex justify-content-center bg-#4B5F63 "),
    dcc.Checklist(
        id="toggle-rangeslider",
        options=[{"label": "Include Rangeslider", "value": "slider"}],
        value=["slider"],
    ),


])

@app.callback(
    Output("graph", "figure"),
    Input('button', 'n_clicks'),
    State('interval_date', 'start_date'),
    State('interval_date', 'end_date'),
    State('symbol_radio', 'value'),
    State('interval_radio', 'value')
)
def display_candlestick(value,start_date,end_date, symbol,interval):
    print("grap update")
    print('Bouton cliqué')
    print("Symbol", symbol)
    print("Interval", interval)
    start_date = str(start_date[0:4]) + str(start_date[5:7])
    end_date = str(end_date[0:4]) + str(end_date[5:7])
    print("Start date", start_date)
    print("Stop date", end_date)
    df = HbaseTableConnector.read(symbol, interval, start_date, end_date)
    df = df.sort_index()
    validate = False
    col_title = []
    for x in df:
        col_title.append(x)
    fig = go.Figure(
        go.Candlestick(
            x=df[col_title[6]],
            open=df[col_title[4]],
            high=df[col_title[2]],
            low=df[col_title[3]],
            close=df[col_title[0]],
            increasing_line_color='#6DE47A', decreasing_line_color='#FF4D4D',

        ))
    fig.update_layout(
        title='Evolution de la monnaie',
        yaxis_title='Value',
        height = 800)

    fig.update_traces(visible=True,)
    return fig

@app.callback(
    Output('output-container-date-picker-range', 'children'),
    Input('interval_date', 'start_date'),
    Input('interval_date', 'end_date'))
def update_output(start_date, end_date):
    string_prefix = 'You have selected: '
    if start_date is not None:
        start_date_object = date.fromisoformat(start_date)
        start_date_string = start_date_object.strftime('%B %d, %Y')
        string_prefix = string_prefix + 'Start Date: ' + start_date_string + ' | '
    if end_date is not None:
        end_date_object = date.fromisoformat(end_date)
        end_date_string = end_date_object.strftime('%B %d, %Y')
        string_prefix = string_prefix + 'End Date: ' + end_date_string
    if len(string_prefix) == len('You have selected: '):
        return 'Select a date to see it displayed here'
    else:
        return string_prefix


if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0', port = 5000)
