import dash_bootstrap_components
from dash import Dash, dcc, html, Input, Output, State
from datetime import date, datetime
from typing import List
from io import StringIO
from opa.process.technical_indicators import simple_mobile_average, exponential_mobile_average, \
    stochastic_relative_strength_index
from plotly import graph_objects as go
import dash_bootstrap_components as dbc
import requests
import pandas as pd
import json
import os

OPA_API_URL: str = os.getenv("OPA_API_URL")
SMA_VALUE = 1
EMA_VALUE = 2
STCH_RSI_VALUE = 3
gbl_df_candlesticks: pd.DataFrame = None
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
            html.Div(
                [
                    dbc.Label("Afficher des indicateurs"),
                    dbc.Checklist(
                        options=[
                            {"label": "Simple mobile average", "value": SMA_VALUE},
                            {"label": "Exponential mobile average", "value": EMA_VALUE},
                            {"label": "Stochastic RSI", "value": STCH_RSI_VALUE, "disabled": True},
                        ],
                        value=[1],
                        id="indicators-input"
                    )
                ]
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


def generate_figure_content(df: pd.DataFrame, indicators_value: List) -> List:
    fig_instances_list = []
    candlesticks_chart = go.Candlestick(
        x=df['CANDLESTICKS:close_time'],
        open=df['CANDLESTICKS:open'],
        high=df['CANDLESTICKS:high'],
        low=df['CANDLESTICKS:low'],
        close=df['CANDLESTICKS:close'],
        increasing_line_color='#6DE47A',
        decreasing_line_color='#FF4D4D')

    fig_instances_list.append(candlesticks_chart)

    if SMA_VALUE in indicators_value:
        sma_short_price = simple_mobile_average(df['CANDLESTICKS:close'].array, 20)
        sma_long_price = simple_mobile_average(df['CANDLESTICKS:close'].array, 60)

        sma_short_scatter = go.Scatter(x=df['CANDLESTICKS:close_time'],
                                       y=sma_short_price,
                                       mode="lines",
                                       line=go.scatter.Line(color="blue"),
                                       showlegend=True,
                                       name="sma_short")

        sma_long_scatter = go.Scatter(x=df['CANDLESTICKS:close_time'],
                                      y=sma_long_price,
                                      mode="lines",
                                      line=go.scatter.Line(color="yellow"),
                                      showlegend=True,
                                      name="sma_long")
        fig_instances_list.append(sma_long_scatter)
        fig_instances_list.append(sma_short_scatter)

    if EMA_VALUE in indicators_value:
        ema_short_price = exponential_mobile_average(df['CANDLESTICKS:close'].array, 20)
        ema_long_price = exponential_mobile_average(df['CANDLESTICKS:close'].array, 60)
        ema_short_scatter = go.Scatter(x=df['CANDLESTICKS:close_time'],
                                       y=ema_short_price,
                                       mode="lines",
                                       line=go.scatter.Line(color="red"),
                                       showlegend=True,
                                       name="ema_short")

        ema_long_scatter = go.Scatter(x=df['CANDLESTICKS:close_time'],
                                      y=ema_long_price,
                                      mode="lines",
                                      line=go.scatter.Line(color="pink"),
                                      showlegend=True,
                                      name="ema_long")

        fig_instances_list.append(ema_long_scatter)
        fig_instances_list.append(ema_short_scatter)

    if STCH_RSI_VALUE in indicators_value:
        stch_k, stch_d = stochastic_relative_strength_index(df['CANDLESTICKS:close'], 60, 30,20)
        stch_k_rsi_scatter = go.Scatter(x=df['CANDLESTICKS:close_time'],
                                        y=stch_k,
                                        yaxis="y2",
                                        mode="lines",
                                        line=go.scatter.Line(color="red"),
                                        showlegend=True,
                                        name="stch_k")
        stch_d_rsi_scatter = go.Scatter(x=df['CANDLESTICKS:close_time'],
                                        y=stch_d,
                                        yaxis="y2",
                                        mode="lines",
                                        line=go.scatter.Line(color="blue"),
                                        showlegend=True,
                                        name="stch_d")

        fig_instances_list.append(stch_d_rsi_scatter)
        fig_instances_list.append(stch_k_rsi_scatter)

    return fig_instances_list


@app.callback(
    Output('da-variable', 'options'),
    [Input('da-variable', 'id')]
)
def update_dropdown_options(_):
    response = requests.get(f'http://{OPA_API_URL}/assets')
    return extract_assets_from_response(response)


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
        State("alert-auto", "is_open"),
        Input("indicators-input", "value")
    ]
)
def display_candlestick(n_clicks, value: str, start_date: str, end_date: str, is_open: bool, indicator_value: bool):
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
            gbl_df_candlesticks = pd.read_json(StringIO(response.json()), orient='index')

            if gbl_df_candlesticks.empty:
                print("no data available")
                return fig, not is_open
            else:
                df = gbl_df_candlesticks.sort_index()
                fig_instances_list = generate_figure_content(df, indicator_value)
                fig = go.Figure(fig_instances_list)
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
