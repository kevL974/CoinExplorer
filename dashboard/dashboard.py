import dash_bootstrap_components
from dash import Dash, dcc, html, Input, Output, State
from datetime import date, datetime
from typing import List
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import requests
import pandas as pd
import json
import os

OPA_API_URL: str = os.getenv("OPA_API_URL")
color = '#161d22'
color_text = 'mediumturquoise'
an_options = [{"inconnu":"inconnu"}]

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


def serve_controls() -> dash_bootstrap_components.Card:
    controls = dbc.Card(
        [
            html.Div(
                [
                    dbc.Label("Actif Numérique"),
                    dcc.Dropdown(
                        id="da-variable",
                        options=[],
                        value="",
                    ),
                ]
            ),
            html.Div(
                [
                    dbc.Label("Période"),
                    dcc.Dropdown(
                        id="dp-variable",
                        options=[],
                        value="",
                    ),
                ]
            ),
            html.Div(
                [
                    dbc.Label("Cluster count"),
                    dbc.Input(id="cluster-count", type="number", value=3),
                ]
            ),
        ],
        body=True,
    )
    return controls


def serve_layout() -> Dash.layout:
    layout = dbc.Container(
        [
            html.H1("Iris k-means clustering"),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(serve_controls(), md=4),
                    dbc.Col(dcc.Graph(id="cluster-graph"), md=8),
                ],
                align="center",
            ),
        ],
        fluid=True,
    )
    return layout


def extract_assets_from_response(response: requests.Response) -> List:
    if response.status_code == requests.codes.ok:
        try:
            list_assets = json.loads(response.content)
            if len(list_assets) == 0:
                assets_options = [{'label': 'pas d\'actifs numériques disponible'}]
            else:
                assets_options = [{'label': asset, 'value': asset} for asset in list_assets]

        except ValueError:
            assets_options = [{'label': 'Erreur interne'}]
        return assets_options


@app.callback(
    Output('da-variable', 'options'),
    [Input('da-variable', 'id')]
)
def update_dropdown_options(_):
    response = requests.get(f'http://{OPA_API_URL}/assets')
    return extract_assets_from_response(response)


app.layout = serve_layout()

#def set_da_options():

# app.layout = html.Div(
#     [
#         dbc.Row(
#             dbc.Col(
#                 html.Div(dcc.Markdown('## **CryptoBot avec Binance** ',
#                                       style={"position": "fixed",
#                                              "top": 0,
#                                              "left": 0,
#                                              "bottom": 0,
#                                              "padding": "1rem",
#                                              'textAlign': 'center',
#                                              'color': color_text,
#                                              'background': color})),
#                 width={"size": 6, "offset": 3},
#             )
#         ),
#         dbc.Row(
#             [
#                 dbc.Col(
#                     [
#                         dbc.Row(
#                             [
#                                 dcc.Markdown('Choix de la date ',
#                                              style={'textAlign': 'center',
#                                                     'color': 'mediumturquoise',
#                                                     'width': '100%',
#                                                     'background': color}),
#                                 dcc.DatePickerRange(
#                                     id='interval_date',
#                                     clearable=True,
#                                     style={'textAlign': 'center',
#                                            'color': 'mediumturquoise',
#                                            'background': color},
#                                     min_date_allowed=date(2017, 8, 1),
#                                     start_date=date(2023, 9, 1),
#                                     end_date=date(2023, 12, 1),
#                                     with_portal=True,
#                                     display_format='DD MMM YY',
#                                 ),
#                                 html.Div(id='output-container-date-picker-range',
#                                          style={'textAlign': 'center',
#                                                 'color': 'mediumturquoise',
#                                                 'background': color}),
#                             ],
#                         ),
#                     ], className="d-flex justify-content-center align-items-stretch"),
#                 dbc.Col(
#                     [
#                         dbc.Row(
#                             [
#                                 dcc.Markdown('Choix de la monnaie ',
#                                              style={'textAlign': 'center',
#                                                     'color': 'mediumturquoise',
#                                                     'width': '100%',
#                                                     'background': color}),
#                                 dcc.RadioItems(['BTCUSDT', 'ETHUSDT'],
#                                                'BTCUSDT',
#                                                id='symbol_radio',
#                                                inline=False,
#                                                style={'textAlign': 'center',
#                                                       'color': 'mediumturquoise',
#                                                       'width': '100%',
#                                                       'background': color}),
#                             ],
#                         ),
#                     ], className="d-flex justify-content-center align-items-stretch"
#                 ),
#                 dbc.Col(
#                     [
#                         dbc.Row(
#                             [
#                                 dcc.Markdown('Choix de la périodicité',
#                                              style={'textAlign': 'center',
#                                                     'color': 'mediumturquoise',
#                                                     'width': '100%',
#                                                     'background': color}),
#                                 dcc.RadioItems(options={"1m": '1 minute',
#                                                         "3m": '3 minutes',
#                                                         "5m": '5 minutes',
#                                                         "15m": '15 minutes',
#                                                         "30m": '30 minutes'},
#                                                id='interval_radio',
#                                                value='15m',
#                                                inline=False,
#                                                style={'textAlign': 'center',
#                                                       'color': 'mediumturquoise',
#                                                       'width': '100%',
#                                                       'background': color}),
#                             ],
#                         ),
#                     ], className="d-flex justify-content-center align-items-stretch"
#                 ),
#
#             ], style={"position": "fixed",
#                       "top": 100,
#                       "left": 0,
#                       "width": "100%",
#                       'textAlign': 'center',
#                       'justification': 'center',
#                       'color': 'mediumturquoise',
#                       'background': color}),
#         dbc.Row(
#             dbc.Col(
#                 html.Div(dbc.Button("Lancer la requete", "button")),
#                 style={"position": "fixed",
#                    "top": 300,
#                    "left": 0,
#                    "width": {"size": 6, "offset": 3},
#                    "padding": "1rem",
#                    'textAlign': 'center',
#                    'justification': 'center'},
#                 className="d-flex justify-content-center "
#             )
#         ),
#         dbc.Row(dcc.Graph(id='graph',
#                           figure={'layout': {'plot_bgcolor': color,'paper_bgcolor': color, }}),
#                 style={"position": "fixed",
#                        "top": 380,
#                        "left": 0,
#                        "high": "100%",
#                        "width": "100%",
#                        "padding": "1rem",
#                        'textAlign': 'center',
#                        'justification': 'center',
#                        'color': 'mediumturquoise',
#                        'background': color}, #"overflow": "scroll"
#                 className="d-flex justify-content-center bg-#4B5F63 "),
#     ]
# )
# @app.callback(
#     Output("graph", "figure"),
#     Input('button', 'n_clicks'),
#     State('symbol_radio', 'value'),
#     State('interval_radio', 'value'),
#     State('interval_date', 'start_date'),
#     State('interval_date', 'end_date')
# )
# def display_candlestick(value, symbol: str, interval: str, start_date: str, end_date: str):
#     start_date = start_date.replace('-', '')
#     end_date = end_date.replace('-', '')
#     response = requests.get(
#         f'http://{OPA_API_URL}/candlesticks?symbol={symbol}&interval={interval}&start={start_date}&end={end_date}')
#     fig = go.Figure()
#     if response.status_code == requests.codes.ok:
#         df = pd.read_json(response.json(), orient='index')
#         df = df.sort_index()
#         fig = go.Figure(
#             go.Candlestick(
#                 x=df['CANDLESTICKES:close_time'],
#                 open=df['CANDLESTICKES:open'],
#                 high=df['CANDLESTICKES:high'],
#                 low=df['CANDLESTICKES:low'],
#                 close=df['CANDLESTICKES:close'],
#                 increasing_line_color='#6DE47A',
#                 decreasing_line_color='#FF4D4D',
#
#             ))
#
#     elif response.status_code == requests.codes.bad_request:
#         print("Erreur 400")
#
#     elif response.status_code == requests.codes.unprocessable_entity:
#         print("Erreur 422")
#         print(response.text)
#     else:
#         print(f"erreur {response.status_code}")
#
#     fig.update_layout(
#         title_text='Evolution de la monnaie', title_x=0.5,
#         yaxis_title='Value',
#         plot_bgcolor=color, autosize=True, height=800, font_color='mediumturquoise', paper_bgcolor=color)
#     fig.update_xaxes(
#         mirror=True,
#         ticks='outside',
#         showline=True,
#         linecolor='mediumturquoise',
#         gridcolor='mediumturquoise', color="mediumturquoise"
#     )
#     fig.update_yaxes(
#         mirror=True,
#         ticks='outside',
#         showline=True,
#         linecolor='mediumturquoise',
#         gridcolor='mediumturquoise', color="mediumturquoise"
#     )
#     fig.update_traces(visible=True, )
#     return fig
#
#
# @app.callback(
#     Output('output-container-date-picker-range', 'children'),
#     Input('interval_date', 'start_date'),
#     Input('interval_date', 'end_date'))
# def update_output(start_date, end_date):
#     string_prefix = 'You have selected: '
#     if start_date is not None:
#         start_date_object = date.fromisoformat(start_date)
#         start_date_string = start_date_object.strftime('%B %d, %Y')
#         string_prefix = string_prefix + 'Start Date: ' + start_date_string + ' | '
#     if end_date is not None:
#         end_date_object = date.fromisoformat(end_date)
#         end_date_string = end_date_object.strftime('%B %d, %Y')
#         string_prefix = string_prefix + 'End Date: ' + end_date_string
#     if len(string_prefix) == len('You have selected: '):
#         return 'Select a date to see it displayed here'
#     else:
#         return string_prefix


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=5050)
