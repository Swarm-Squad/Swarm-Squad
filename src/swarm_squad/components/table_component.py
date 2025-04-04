import sqlite3

import dash_mantine_components as dmc
import pandas as pd
from dash import dash_table

from swarm_squad.utils.db_init import get_db_path

# Get the database path
DB_PATH = get_db_path()


def create_data_table(df, id_prefix):
    """Create a styled DataTable component"""
    if df is None or df.empty or len(df.columns) == 0:
        return dmc.Alert(
            "No columns selected",
            title="Empty Dataset",
            color="dark",
            variant="filled",
            className="empty-dataset-alert",
        )

    return dash_table.DataTable(
        id=f"{id_prefix}-table",
        columns=[{"name": i, "id": i, "selectable": True} for i in df.columns],
        data=df.to_dict("records"),
        style_table={
            "overflowX": "auto",
            "overflowY": "auto",
            "maxHeight": "calc(100vh - 200px)",
            "backgroundColor": "transparent",
            "height": "100%",
            "width": "100%",
        },
        style_header={
            "backgroundColor": "rgba(30, 30, 30, 0.7)",
            "color": "white",
            "fontWeight": "bold",
            "position": "sticky",
            "top": 0,
            "zIndex": 1000,
            "textAlign": "center",
        },
        style_data={
            "backgroundColor": "rgba(50, 50, 50, 0.5)",
            "color": "white",
            "whiteSpace": "normal",
            "height": "auto",
            "textAlign": "center",
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "rgba(40, 40, 40, 0.5)"}
        ],
        style_cell={
            "textAlign": "center",
            "padding": "10px",
        },
        filter_action="native",  # Enable filtering
        sort_action="native",
        sort_mode="multi",
        page_action="none",  # Disable pagination
    )


def fetch_agent_data():
    """Fetch agent data from database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        query = "SELECT * FROM agent"
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            print("Agent table is empty.")
            return pd.DataFrame()  # Return an empty DataFrame

        return df
    except Exception as e:
        print(f"Error fetching agent data: {e}")
        return None


def fetch_mission_data():
    """Fetch mission data from database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        query = "SELECT * FROM mission"
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            print("Mission table is empty.")
            return pd.DataFrame()  # Return an empty DataFrame

        return df
    except Exception as e:
        print(f"Error fetching mission data: {e}")
        return None


def fetch_telemetry_data():
    """Fetch telemetry data from database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        query = "SELECT * FROM telemetry"
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            print("Telemetry table is empty.")
            return pd.DataFrame()  # Return an empty DataFrame

        return df
    except Exception as e:
        print(f"Error fetching telemetry data: {e}")
        return None


def fetch_system_data():
    """Fetch system data from database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        query = "SELECT * FROM system"
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            print("System table is empty.")
            return pd.DataFrame()  # Return an empty DataFrame

        return df
    except Exception as e:
        print(f"Error fetching system data: {e}")
        return None
