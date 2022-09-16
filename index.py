"""
Name:    index.py
Author:  kyh
Created: 9/16/2022 10:28 PM
"""
from dash.dependencies import Input, Output

import pages
from app import app


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
