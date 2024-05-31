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
color = '#303030'
color_text = '#fff'
an_options = [{"inconnu": "inconnu"}]

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])


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
                        style={'textAlign': 'center',
                               'color': 'black'}
                    ),
                ]
            ),
            html.Div(
                [
                    dbc.Label("Choix de la date : "),
                    dcc.DatePickerRange(
                        id='interval_date',
                        clearable=True,
                        style={'textAlign': 'center',
                               'color': 'mediumturquoise',
                               'background': color},
                        min_date_allowed=date(2017, 8, 1),
                        start_date=date(2023, 12, 1),
                        end_date=date(2023, 12, 10),
                        with_portal=True,
                        display_format='DD MMM YY',
                    ),
                    html.Div(id='output-container-date-picker-range',
                             style={'textAlign': 'center'}),
                ],
            ),
            html.Div(dbc.Button("Lancer la requete", "button"))
        ],
        body=True,

    )
    return controls


def serve_layout() -> Dash.layout:
    layout = dbc.Container(
        [
            html.H1("CoinExplorer"),
            html.Hr(),
            dbc.Row([
                dbc.Col(serve_controls(), md=4),
                dbc.Col(dcc.Graph(id='graph',
                                  figure={'layout': {'plot_bgcolor': color, 'paper_bgcolor': color, }}), md=8),
            ],
                align="start",
            ),
            dbc.Row(
                dbc.Alert("Data is unvailable.",
                          id="alert-auto",
                          dismissable=True,
                          is_open=False,
                          duration=2000))
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
                assets_options = [{'label': asset.replace("|", " "), 'value': asset} for asset in list_assets]

        except ValueError:
            assets_options = [{'label': 'Erreur interne'}]
        return assets_options


def configure_figure(figure: go.Figure):
    figure.update_layout(
        title_text='Evolution de la monnaie', title_x=0.5,
        yaxis_title='Value',
        plot_bgcolor=color, autosize=True, height=800, font_color=color_text, paper_bgcolor=color)
    figure.update_xaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor=color_text,
        gridcolor=color_text, color=color_text
    )
    figure.update_yaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor=color_text,
        gridcolor=color_text, color=color_text
    )


@app.callback(
    Output('da-variable', 'options'),
    [Input('da-variable', 'id')]
)
def update_dropdown_options(_):
    response = requests.get(f'http://{OPA_API_URL}/assets')
    return extract_assets_from_response(response)


# @app.callback(
#     Output("alert-auto", "is_open"),
#     [State("alert-auto", "is_open")],
# )
# def toggle_alert(is_open):
#     if id:
#         return not is_open
#     return is_open

@app.callback(
    [
        Output("graph", "figure"),
        Output("alert-auto", "is_open")
    ],
    Input('button', 'n_clicks'),
    [
        State('da-variable', 'value'),
        State('interval_date', 'start_date'),
        State('interval_date', 'end_date'),
        State("alert-auto", "is_open")
    ]
)
def display_candlestick(n_clicks, value: str, start_date: str, end_date: str, is_open: bool):
    fig = go.Figure()
    configure_figure(fig)
    if n_clicks:
        start_date = start_date.replace('-', '')
        end_date = end_date.replace('-', '')
        symbol = value.split("|")[0]
        interval = value.split("|")[1]
        response = requests.get(
            f'http://{OPA_API_URL}/candlesticks?symbol={symbol}&interval={interval}&start={start_date}&end={end_date}')

        if response.status_code == requests.codes.ok:
            df = pd.read_json(response.json(), orient='index')

            if df.empty:
                print("no data available")
                return fig, not is_open
            else:
                df = df.sort_index()
                fig = go.Figure(
                    go.Candlestick(
                        x=df['CANDLESTICKS:close_time'],
                        open=df['CANDLESTICKS:open'],
                        high=df['CANDLESTICKS:high'],
                        low=df['CANDLESTICKS:low'],
                        close=df['CANDLESTICKS:close'],
                        increasing_line_color='#6DE47A',
                        decreasing_line_color='#FF4D4D',

                    ))
                configure_figure(fig)
        else:
            if response.status_code == requests.codes.bad_request:
                print("Erreur 400")

            elif response.status_code == requests.codes.unprocessable_entity:
                print("Erreur 422")
                print(response.text)
            else:
                print(f"erreur {response.status_code}")
                print(response.content)

            return fig, not is_open

        fig.update_traces(visible=True, )
    return fig, is_open


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


app.layout = serve_layout()

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=5050)
