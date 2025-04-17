import logging

import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import Dash, Output, Input, callback, clientside_callback, html, dcc
from sqlalchemy import select

from app.db.db_connection import db_dependency
from app.db.models.models import ProcessedData

logging.captureWarnings(True)
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

df = pd.read_sql(
    select(ProcessedData.date, ProcessedData.ticker)
    .order_by(ProcessedData.date)
    , db_dependency.engine_)

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
            options=[
                {"label": "Show expenses", "value": 1},
            ],
            value=[],
        ),
        dbc.Checklist(
            id="aggregation",
            options=[
                {"label": "Data aggregation", "value": 1},
            ],
            value=[],
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
    # Output("expenses", "options"),

    Input("tickers", "value"),
    Input("dates", "value"),
    Input("expenses", "value"),
    Input("aggregation", "value"),
)
def update(tickers, boundaries, tick, tick_):
    df = pd.read_sql(
        select(ProcessedData.date, ProcessedData.ticker, ProcessedData.expenses, ProcessedData.shares,
               ProcessedData.capitalization, ProcessedData.price)
        .filter(ProcessedData.ticker.in_(tickers))
        .order_by(ProcessedData.date)
        , db_dependency.engine_
    )
    df["date_int"] = pd.to_datetime(df["date"]).dt.strftime("%Y%m%d").astype(int)
    dff = df[df.date_int.between(boundaries[0], boundaries[1])]
    dff_ = dff.groupby("date", as_index=False)[["capitalization", "expenses"]].aggregate("sum")
    fig = px.line(
        dff,
        x="date",
        y="capitalization",
        color="ticker",
        render_mode="webgl",
    )

    if tick:

        fig_exp = px.line(
            dff_, x="date", y="expenses", color_discrete_sequence=("magenta",)
        ).update_traces(showlegend=True, name="expenses")
        # noinspection PyTypeChecker
        fig.add_traces(fig_exp.data)

    if tick_:
        fig_agg = px.line(
            dff_, x="date", y="capitalization", color_discrete_sequence=("maroon",)
        ).update_traces(showlegend=True, name="aggregation")
        # noinspection PyTypeChecker
        fig.add_traces(fig_agg.data)

    data = dff.to_dict("records")
    columns = [{"field": i} for i in dff.columns if i != "date_int"]
    return fig, data, columns


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


# @app.server.route("/shutdown", methods=["POST"])
# def shutdown():
#     os.kill(os.getpid(), signal.SIGINT)  # Send a signal to the process to terminate
#     return json.dumps('')


def main() -> None:
    app.run(host="0.0.0.0", port=8050, debug=False)


if __name__ == "__main__":
    main()
