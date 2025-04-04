import dash
import dash_mantine_components as dmc
import pandas as pd
from dash import Input, Output, callback, dcc, html
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from swarm_squad.components.table_component import (
    create_data_table,
    fetch_agent_data,
    fetch_mission_data,
    fetch_system_data,
    fetch_telemetry_data,
)

dash.register_page(
    __name__,
    path="/data",
    order=2,
    title="Data | Swarm Squad",
    description="Data analysis and visualization",
)

# Fetch initial data
agent_df = fetch_agent_data()
mission_df = fetch_mission_data()
telemetry_df = fetch_telemetry_data()
system_df = fetch_system_data()

# Get initial columns
agent_columns = (
    [{"label": col, "value": col} for col in agent_df.columns]
    if agent_df is not None and not agent_df.empty
    else []
)
mission_columns = (
    [{"label": col, "value": col} for col in mission_df.columns]
    if mission_df is not None and not mission_df.empty
    else []
)
telemetry_columns = (
    [{"label": col, "value": col} for col in telemetry_df.columns]
    if telemetry_df is not None and not telemetry_df.empty
    else []
)
system_columns = (
    [{"label": col, "value": col} for col in system_df.columns]
    if system_df is not None and not system_df.empty
    else []
)

layout = html.Div(
    [
        dcc.Interval(
            id="interval-component",
            interval=500,  # in milliseconds (0.5 second)
            n_intervals=0,
        ),
        html.Div(className="illumination-4"),
        html.Div(className="illumination-5"),
        html.Div(className="stars"),
        dmc.Container(
            [
                dmc.SimpleGrid(
                    cols=2,
                    spacing="lg",
                    className="tables-grid",
                    children=[
                        # Agent Table
                        dmc.Card(
                            children=[
                                dmc.Title(
                                    [
                                        DashIconify(
                                            icon="carbon:events",
                                            width=24,
                                            className="table-icon",
                                        ),
                                        "Agent Details",
                                    ],
                                    order=3,
                                    mb="md",
                                    c="blue",
                                    className="table-title",
                                ),
                                dmc.MultiSelect(
                                    id="agent-column-select",
                                    label="Choose columns to display",
                                    description="",
                                    placeholder="Select columns...",
                                    searchable=True,
                                    clearable=True,
                                    nothingFoundMessage="No options found",
                                    style={"width": "100%", "zIndex": 1200},
                                    className="column-select",
                                    data=agent_columns,
                                    value=[col["value"] for col in agent_columns],
                                ),
                                html.Div(
                                    id="agent-table-container",
                                    className="table-container",
                                ),
                            ],
                            withBorder=True,
                            shadow="sm",
                            radius="md",
                            className="table-card",
                        ),
                        # Mission Table
                        dmc.Card(
                            children=[
                                dmc.Title(
                                    [
                                        DashIconify(
                                            icon="carbon:center-circle",
                                            width=24,
                                            className="table-icon",
                                        ),
                                        "Mission Status",
                                    ],
                                    order=3,
                                    mb="md",
                                    c="green",
                                    className="table-title",
                                ),
                                dmc.MultiSelect(
                                    id="mission-column-select",
                                    label="Choose columns to display",
                                    description="",
                                    placeholder="Select columns...",
                                    searchable=True,
                                    clearable=True,
                                    nothingFoundMessage="No options found",
                                    style={"width": "100%", "zIndex": 1200},
                                    className="column-select",
                                    data=mission_columns,
                                    value=[col["value"] for col in mission_columns],
                                ),
                                html.Div(
                                    id="mission-table-container",
                                    className="table-container",
                                ),
                            ],
                            withBorder=True,
                            shadow="sm",
                            radius="md",
                            className="table-card",
                        ),
                        # Telemetry Table
                        dmc.Card(
                            children=[
                                dmc.Title(
                                    [
                                        DashIconify(
                                            icon="carbon:network-4",
                                            width=24,
                                            className="table-icon",
                                        ),
                                        "Telemetry Data",
                                    ],
                                    order=3,
                                    mb="md",
                                    c="yellow",
                                    className="table-title",
                                ),
                                dmc.MultiSelect(
                                    id="telemetry-column-select",
                                    label="Choose columns to display",
                                    description="",
                                    placeholder="Select columns...",
                                    searchable=True,
                                    clearable=True,
                                    nothingFoundMessage="No options found",
                                    style={"width": "100%", "zIndex": 1200},
                                    className="column-select",
                                    data=telemetry_columns,
                                    value=[col["value"] for col in telemetry_columns],
                                ),
                                html.Div(
                                    id="telemetry-table-container",
                                    className="table-container",
                                ),
                            ],
                            withBorder=True,
                            shadow="sm",
                            radius="md",
                            className="table-card",
                        ),
                        # System Table
                        dmc.Card(
                            children=[
                                dmc.Title(
                                    [
                                        DashIconify(
                                            icon="carbon:activity",
                                            width=24,
                                            className="table-icon",
                                        ),
                                        "System Health",
                                    ],
                                    order=3,
                                    mb="md",
                                    c="red",
                                    className="table-title",
                                ),
                                dmc.MultiSelect(
                                    id="system-column-select",
                                    label="Choose columns to display",
                                    description="",
                                    placeholder="Select columns...",
                                    searchable=True,
                                    clearable=True,
                                    nothingFoundMessage="No options found",
                                    style={"width": "100%", "zIndex": 1200},
                                    className="column-select",
                                    data=system_columns,
                                    value=[col["value"] for col in system_columns],
                                ),
                                html.Div(
                                    id="system-table-container",
                                    className="table-container",
                                ),
                            ],
                            withBorder=True,
                            shadow="sm",
                            radius="md",
                            className="table-card",
                        ),
                    ],
                )
            ],
            fluid=True,
            className="data-container",
        ),
    ],
    className="data-page",
)


@callback(
    [
        Output("agent-table-container", "children"),
        Output("mission-table-container", "children"),
        Output("telemetry-table-container", "children"),
        Output("system-table-container", "children"),
        Output("agent-column-select", "value", allow_duplicate=True),
        Output("mission-column-select", "value", allow_duplicate=True),
        Output("telemetry-column-select", "value", allow_duplicate=True),
        Output("system-column-select", "value", allow_duplicate=True),
    ],
    [
        Input("agent-column-select", "value"),
        Input("mission-column-select", "value"),
        Input("telemetry-column-select", "value"),
        Input("system-column-select", "value"),
        Input("interval-component", "n_intervals"),
    ],
    prevent_initial_call=True,
)
def update_tables(agent_cols, mission_cols, telemetry_cols, system_cols, n_intervals):
    try:
        # Fetch data from database
        agent_df = fetch_agent_data()
        mission_df = fetch_mission_data()
        telemetry_df = fetch_telemetry_data()
        system_df = fetch_system_data()

        # Create empty DataFrames if no columns selected
        if not agent_cols:
            agent_df = pd.DataFrame()
        else:
            agent_df = agent_df[agent_cols]

        if not mission_cols:
            mission_df = pd.DataFrame()
        else:
            mission_df = mission_df[mission_cols]

        if not telemetry_cols:
            telemetry_df = pd.DataFrame()
        else:
            telemetry_df = telemetry_df[telemetry_cols]

        if not system_cols:
            system_df = pd.DataFrame()
        else:
            system_df = system_df[system_cols]

        # Create tables
        agent_table = create_data_table(agent_df, "agent")
        mission_table = create_data_table(mission_df, "mission")
        telemetry_table = create_data_table(telemetry_df, "telemetry")
        system_table = create_data_table(system_df, "system")

        return (
            agent_table,
            mission_table,
            telemetry_table,
            system_table,
            agent_cols if agent_cols else [],
            mission_cols if mission_cols else [],
            telemetry_cols if telemetry_cols else [],
            system_cols if system_cols else [],
        )

    except Exception as e:
        print(f"Error updating tables: {e}")
        raise PreventUpdate
