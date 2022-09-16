"""
Name:    app.py
Author:  kyh
Created: 9/11/2022 10:46 PM
"""
import dash
import dash_bootstrap_components as dbc

from data.shareholding import ShareHoldingDAO
from static import APP_NAME

dao = ShareHoldingDAO()

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)
app.title = APP_NAME