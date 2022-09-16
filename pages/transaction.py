"""
Name:    transaction.py
Author:  kyh
Created: 9/15/2022 10:33 PM
"""
import datetime

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, State, dcc, html
from dash.dash_table.Format import Format, Scheme, Sign
from dateutil.relativedelta import relativedelta

from app import app, dao
from data.shareholding import ShareHolding

PREV_COL = f"Previous {ShareHolding.ShareholdingPct}"
CURR_COL = f"Current {ShareHolding.ShareholdingPct}"
CHANGE_COL = f"Change in {ShareHolding.ShareholdingPct}"
PCT_FMT = Format(scheme=Scheme.percentage, precision=2)


def layout():
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    html.P("Set Threshold (%):"),
                    dcc.Input(
                        id='transaction_threshold',
                        type="number",
                        value=1
                    ),
                ])
            ]),
            dbc.Col([
                dbc.Button(
                    children="",
                    id='load_transaction_button',
                    n_clicks=0,
                    color="primary",
                    className="me-1"
                ),
            ]),
            dbc.Col([
                dbc.Alert(
                    children="",
                    id="transaction_alert",
                    dismissable=True,
                    fade=False,
                    is_open=False,
                    color="danger",
                )
            ])
        ]),
        dash.dash_table.DataTable(
            id='transaction_table',
            data=[],
            columns=[
                {'name': ShareHolding.Date, 'id': ShareHolding.Date, 'type': "datetime"},
                {'name': ShareHolding.ParticipantID, 'id': ShareHolding.ParticipantID},
                {'name': ShareHolding.ParticipantName, 'id': ShareHolding.ParticipantName},
                {'name': PREV_COL, 'id': PREV_COL, 'type': 'numeric', 'format': PCT_FMT},
                {'name': CURR_COL, 'id': CURR_COL, 'type': 'numeric', 'format': PCT_FMT},
                {'name': CHANGE_COL, 'id': CHANGE_COL, 'type': 'numeric', 'format': PCT_FMT.sign(Sign.parantheses)}
            ],
            editable=False,
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
        )
    ])


@app.callback(
    Output('load_transaction_button', 'children'),
    Input('transaction_threshold', 'value'))
def update_load_transaction_button(value):
    return f"Load Transactions Above {value:.2f}%"


@app.callback(
    [Output('transaction_table', 'data'),
     Output('transaction_alert', 'is_open'),
     Output('transaction_alert', 'children'),
     Output('transaction_alert', 'color'), ],
    [Input('load_transaction_button', 'n_clicks')],
    [State('stockcode', 'value'),
     State('daterange', 'start_date'),
     State('daterange', 'end_date'),
     State('transaction_threshold', 'value')], prevent_initial_call=True)
def load_transactions(n_clicks, stockcode, start_date, end_date, threshold):
    if not stockcode:
        return dash.no_update, True, "Stock Code cannot be empty", "danger"

    threshold = threshold / 100.0
    end_date = datetime.datetime.strptime(end_date[:10], '%Y-%m-%d').date()
    start_date = datetime.datetime.strptime(start_date[:10], '%Y-%m-%d').date()

    keys = [ShareHolding.ParticipantName, ShareHolding.ParticipantID]
    columns = [*keys, ShareHolding.ShareholdingPct]
    data = []
    date = start_date

    prev = dao.get_data_by_stock(stockcode, date=date + relativedelta(days=-1), columns=columns)
    while date <= end_date:
        curr = dao.get_data_by_stock(stockcode, date=date, columns=columns)
        diff = pd.merge(curr, prev, how="outer", on=keys).rename({
            f'{ShareHolding.Date}_x': ShareHolding.Date,
            f'{ShareHolding.ShareholdingPct}_x': CURR_COL,
            f'{ShareHolding.ShareholdingPct}_y': PREV_COL
        }, axis=1).fillna({
            CURR_COL: 0.0,
            PREV_COL: 0.0
        })
        diff[CHANGE_COL] = diff[CURR_COL] - diff[PREV_COL]
        diff = diff[diff[CHANGE_COL].abs() > threshold]
        data.append(diff[[ShareHolding.Date, *keys, PREV_COL, CURR_COL, CHANGE_COL]])

        prev = curr
        date += relativedelta(days=1)

    data = pd.concat(data, ignore_index=True)
    return data.to_dict('records'), True, "Transactions loaded", "success"
