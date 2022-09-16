"""
Name:    trend.py
Author:  kyh
Created: 9/15/2022 10:32 PM
"""
import datetime

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import Input, Output, State, dcc, html
from dash.dash_table.Format import Format, Scheme
from dateutil.relativedelta import relativedelta

from app import app, dao
from data.shareholding import ShareHolding


def layout():
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    children="Load Shareholding Trend",
                    id='load_trend_button',
                    n_clicks=0,
                    color="primary",
                    className="me-1"
                ),
            ]),
            dbc.Col([
                dbc.Alert(
                    children="",
                    id="trend_alert",
                    dismissable=True,
                    fade=False,
                    is_open=False,
                    color="danger",
                )
            ])
        ]),
        dcc.Graph(
            id='trend_plot',
            figure={
            }
        ),
        dash.dash_table.DataTable(
            id='trend_table',
            data=[],
            columns=[
                {'name': ShareHolding.Date, 'id': ShareHolding.Date, 'type': "datetime"},
                {'name': ShareHolding.ParticipantID, 'id': ShareHolding.ParticipantID},
                {'name': ShareHolding.ParticipantName, 'id': ShareHolding.ParticipantName},
                {'name': ShareHolding.Shareholding, 'id': ShareHolding.Shareholding, 'type': 'numeric',
                 'format': Format(scheme=Scheme.decimal_integer, group=True, groups=[3])}
            ],
            editable=False,
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            page_action="native",
            page_current=0,
            page_size=10,
        )
    ])


@app.callback(
    [Output('trend_table', 'data'),
     Output('trend_plot', 'figure'),
     Output('trend_alert', 'is_open'),
     Output('trend_alert', 'children'),
     Output('trend_alert', 'color'), ],
    [Input('load_trend_button', 'n_clicks')],
    [State('stockcode', 'value'),
     State('daterange', 'start_date'),
     State('daterange', 'end_date')], prevent_initial_call=True)
def load_trend(n_clicks, stockcode, start_date, end_date):
    if not stockcode:
        return dash.no_update, dash.no_update, True, "Stock Code cannot be empty", "danger"

    end_date = datetime.datetime.strptime(end_date[:10], '%Y-%m-%d').date()
    start_date = datetime.datetime.strptime(start_date[:10], '%Y-%m-%d').date()

    keys = [ShareHolding.ParticipantName, ShareHolding.ParticipantID]
    columns = [*keys, ShareHolding.Shareholding]
    top = dao.get_data_by_stock(stockcode, date=end_date, columns=columns, top_n=10)
    if top.empty:
        return dash.no_update, dash.no_update, True, f"None of the CCASS participants holds {stockcode} on {end_date}", "warning"

    data = [top]
    date = start_date
    while date < end_date:
        daily = dao.get_data_by_stock(stockcode, date=date, columns=columns)
        daily = pd.merge(daily, top[keys], how="inner")
        data.append(daily)

        date += relativedelta(days=1)
    data = pd.concat(data, ignore_index=True)

    data['Participant'] = data.apply(lambda r: f"{r[ShareHolding.ParticipantName]} ({r[ShareHolding.ParticipantID]})",
                                     axis=1)
    fig = px.line(data, x=ShareHolding.Date, y=ShareHolding.Shareholding, color='Participant',
                  title=f"Shareholding Trend for Top Holders of {stockcode} (as of {end_date}, from {start_date})")
    return data.to_dict('records'), fig, True, "Shareholding trend loaded", "success"
