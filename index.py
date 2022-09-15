"""
Name:    index.py
Author:  kyh
Created: 9/15/2022 10:32 PM
"""
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dateutil.relativedelta import relativedelta

import pages
from app import app
from static import CONTENT_STYLE, SIDEBAR_STYLE
from utils import today

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


@app.callback(Output("card-content", "children"), [Input("tab", "active_tab")])
def display_tab_content(active_tab):
    if active_tab == "trend":
        return pages.trend.layout()
    elif active_tab == "transactions":
        return pages.transaction.layout()
    else:
        return "404"


if __name__ == '__main__':
    app.run_server(debug=True)
