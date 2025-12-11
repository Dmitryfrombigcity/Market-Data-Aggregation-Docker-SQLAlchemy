import asyncio
import logging
from datetime import date
from typing import Awaitable, Any

import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import Dash, Output, Input, callback, clientside_callback, html, dcc

from app.dash.data_processing import get_data
from project_settings import setting

logging.captureWarnings(True)
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

date_range: dict[int, date] = {}
for ind in range(157):
    year = 2013 + ind // 12
    month = ind % 12 + 1
    date_range[ind] = date(year, month, 1)

tickers = setting.BUNCH_OF_TICKERS

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
        dbc.Label("Select date range for analysis",
                  style={'height': '60px'}),
        dcc.RangeSlider(
            min=0,
            max=156,
            step=1,
            id="dates",
            value=[0, 156],
            marks={
                i: str(date_range[i].year) for i in range(0, 157, 12)
            },
            tooltip={"always_visible": True, "transform": "months"},
            className="p-0",
            included=False,
            allowCross=False,
        ),
    ],
    className="mb-4",
)

controls = dbc.Card(
    [dropdown, checklist],
    body=True,
)

new_slider = dbc.Card(
    [
        slider],
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
            dbc.Col([
                new_slider,
                tabs
            ], width=10),
        ]),
    ],
    fluid=True,
    className="dbc dbc-ag-grid",
)


def async_to_sync(awaitable: Awaitable) -> Any:
    loop = asyncio.new_event_loop()
    return loop.run_until_complete(awaitable)


@callback(
    Output("line-chart", "figure"),
    Output("grid", "rowData"),
    Output("grid", "columnDefs"),

    Input("tickers", "value"),
    Input("dates", "value"),
    Input("expenses", "value"),
    Input("aggregation", "value"),
)
def update(tickers, boundaries, tick_exp, tick_agg):
    dff = async_to_sync(get_data(tickers, date_range[boundaries[0]], date_range[boundaries[-1]]))
    dff_ = dff.groupby("date", as_index=False)[["capitalization", "expenses"]].aggregate("sum")
    dff_["expenses_"] = dff_["expenses"].cumsum()

    fig = px.line(
        dff,
        x="date",
        y="capitalization",
        color="ticker",
        render_mode="webgl",
    )

    if tick_exp:
        fig_exp = px.line(
            dff_, x="date", y="expenses_", color_discrete_sequence=("magenta",)
        ).update_traces(showlegend=True, name="expenses")
        # noinspection PyTypeChecker
        fig.add_traces(fig_exp.data)

    if tick_agg:
        dff["aggregation"] = dff_["capitalization"]
        fig_agg = px.line(
            dff_, x="date", y="capitalization", color_discrete_sequence=("maroon",)
        ).update_traces(showlegend=True, name="aggregation")
        # noinspection PyTypeChecker
        fig.add_traces(fig_agg.data)

    data = dff.to_dict("records")
    columns = [{"field": i} for i in dff.columns]
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


def main() -> None:
    app.run(host="0.0.0.0", port=8050, debug=False)


if __name__ == "__main__":
    main()
