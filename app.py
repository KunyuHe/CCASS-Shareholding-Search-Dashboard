"""
Name:    app.py
Author:  kyh
Created: 9/11/2022 10:46 PM
"""
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dateutil.relativedelta import relativedelta

from data.shareholding import ShareHoldingDAO
from static import APP_NAME, CONTENT_STYLE, SIDEBAR_STYLE
from utils import today

dao = ShareHoldingDAO()

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)
app.title = APP_NAME
server = app.server
app.layout = html.Div(
    [
        # Left column
        html.Div(
            children=[
                html.P("Input Stock Code:"),
                dcc.Input(
                    id='stockcode',
                    type="text",
                ),
                html.Br(),
                html.Br(),
                html.P(children="Select Date Range:"),
                dcc.DatePickerRange(
                    id='daterange',
                    min_date_allowed=today() + relativedelta(years=-1),
                    max_date_allowed=today() + relativedelta(days=-1),
                    start_date=today() + relativedelta(days=-7),
                    end_date=today() + relativedelta(days=-1)
                )
            ],
            style=SIDEBAR_STYLE
        ),
        html.Div(
            [
                dbc.CardHeader(
                    dbc.Tabs(
                        [
                            dbc.Tab(label="Trend", tab_id="trend"),
                            dbc.Tab(label="Transactions", tab_id="transactions")
                        ],
                        id="tab",
                        active_tab="trend"
                    )
                ),
                dbc.CardBody(html.Div(id="card-content", className="card-text")),
            ],
            style=CONTENT_STYLE
        )
    ]
)
