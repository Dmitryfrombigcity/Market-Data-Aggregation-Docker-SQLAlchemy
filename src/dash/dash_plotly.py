import json
import logging
import os
import signal
import sys
import threading
import webbrowser

import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import Dash, Output, Input, callback, clientside_callback, html, dcc

sys.path.append(os.getcwd())  # https://shorturl.at/KqU2Q
from connection import conn
from queries import get_info, get_tickers
from settings import setting

logging.captureWarnings(True)
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

df = pd.read_sql(get_tickers, conn)
df["date_int"] = pd.to_datetime(df["date"]).dt.strftime("%Y%m%d").astype(int)
dates = df.date_int.unique()
tickers = df.ticker.unique()

app = Dash(__name__, external_stylesheets=[dbc.themes.LITERA, dbc.icons.FONT_AWESOME])

color_mode_switch = html.Span(
    [
        dbc.Label(className="fa fa-moon", html_for="switch"),
        dbc.Switch(id="switch", value=True, className="d-inline-block ms-1", persistence=True),
        dbc.Label(className="fa fa-sun", html_for="switch"),
    ]
)

theme_controls = html.Div(
    color_mode_switch,
    className="hstack gap-3 mt-2"
)

header = html.H4(
    "Stock price analysis", className="bg-primary p-2 mb-2 text-center"
)

grid = dag.AgGrid(
    id="grid",
    style={"height": 750},
    defaultColDef={"flex": 1, "minWidth": 120, "sortable": True, "resizable": True, "filter": True},
    dashGridOptions={"rowSelection": "multiple", "pagination": True},

)

dropdown = html.Div(
    [
        dcc.Dropdown(
            id="tickers",
            value=[],
            options=tickers,
            placeholder="Select a ticker",
            clearable=False,
            multi=True,
        ),
    ],
    className="mb-4",
)

checklist = html.Div(
    [
        dbc.Checklist(
            id="expenses",
            value=[],
            inline=True,
        ),
    ],
    className="mb-4",
)

slider = html.Div(
    [
        dbc.Label("Select dates"),
        dcc.RangeSlider(
            dates.min(),
            dates.max(),
            1,
            id="dates",
            value=[dates.min(), dates.max()],
            marks={
                20130500: "2013",
                20250000: "2025"
            },
            className="p-0",
            included=False,
        ),
    ],
    className="mb-4",
)

controls = dbc.Card(
    [dropdown, checklist, slider],
    body=True,
)

tab1 = dbc.Tab([
    dcc.Graph(
        id="line-chart",
        figure={},
        style={"height": 750}
    )
], label="Line Chart"
)
tab2 = dbc.Tab([
    grid
],
    label="Grid",
    className="p-4"
)
tabs = dbc.Card(
    dbc.Tabs(
        [tab1, tab2]
    ), style={"height": 850}
)
app.layout = dbc.Container(
    [
        header,
        dbc.Row([
            dbc.Col([
                controls,
                theme_controls
            ], width=2),
            dbc.Col(tabs, width=10),
        ]),
    ],
    fluid=True,
    className="dbc dbc-ag-grid",
)


@callback(
    Output("line-chart", "figure"),
    Output("grid", "rowData"),
    Output("grid", "columnDefs"),
    Output("expenses", "options"),
    Input("tickers", "value"),
    Input("dates", "value"),
    Input("expenses", "value"),
)
def update(tickers, boundaries, tick):
    df = pd.read_sql(get_info, conn, params={"t": tickers})
    df["date_int"] = pd.to_datetime(df["date"]).dt.strftime("%Y%m%d").astype(int)
    dff = df[df.date_int.between(boundaries[0], boundaries[1])]
    fig = px.line(
        dff,
        x="date",
        y="capitalization",
        color="ticker",
        render_mode="webgl",
    )
    if len(tickers) == 1:
        expanses_opt = "Show expenses"
        if tick:
            # noinspection PyTypeChecker
            fig.add_traces(
                px.line(dff, x="date", y="expenses", color_discrete_sequence=("red",)
                        ).data)
    else:
        expanses_opt = {"disabled": True}

    data = dff.to_dict("records")
    columns = [{"field": i} for i in dff.columns if i != "date_int"]
    return fig, data, columns, [expanses_opt]


clientside_callback(
    """
    switchOn => {       
       document.documentElement.setAttribute("data-bs-theme", switchOn ? "light" : "dark");  
       return window.dash_clientside.no_update
    }
    """,
    Output("switch", "id"),
    Input("switch", "value"),
)


@app.server.route("/shutdown", methods=["POST"])
def shutdown():
    os.kill(os.getpid(), signal.SIGINT)  # Send a signal to the process to terminate
    return json.dumps('')


def main() -> None:
    threading.Timer(
        interval=1,
        function=webbrowser.open_new_tab,
        args=(f"http://localhost:{setting.SERVER_PORT}",)
    ).start()

    app.run(port=setting.SERVER_PORT, debug=False)


if __name__ == "__main__":
    main()
