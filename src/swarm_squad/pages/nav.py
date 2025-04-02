import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import ALL, Input, Output, State, callback
from dash_iconify import DashIconify

all_icons = [
    "mdi:home-outline",  # Home
    "mdi:map-search-outline",  # Map
    "mdi:database-outline",  # Data
    "mdi:message-processing-outline",  # Chat
    "mdi:chart-line",  # Plot
    "mdi:information-outline",  # Log
]


def navbar():
    return dmc.Grid(
        [
            dmc.ActionIcon(
                DashIconify(
                    icon="zondicons:menu", width=20, style={"display": "block"}
                ),
                c="white",
                variant="transparent",
                id="nav-btn",
                style={
                    "margin": "0 0 0 25px",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "position": "relative",
                    "top": "0",
                    "bottom": "0",
                },
                className="nav-container",
            ),
            dmc.Modal(
                [
                    *[  # Use unpacking to combine regular nav links
                        dbc.NavLink(
                            children=[
                                dmc.Group(
                                    [
                                        dmc.ActionIcon(
                                            DashIconify(
                                                icon=all_icons[idx],
                                                width=35,
                                                color="white",
                                            ),
                                            variant="transparent",
                                        ),
                                        page["name"],
                                    ],
                                    mt=15,
                                    gap="sm",
                                )
                            ],
                            href=page["path"],
                            style={
                                "color": "white",
                                "text-decoration": "none",
                                "font-family": "Arial, sans-serif",
                                "font-size": 15,
                            },
                            className="nav-link",
                            id={"type": "dynamic-link", "index": idx},
                        )
                        for idx, page in enumerate(dash.page_registry.values())
                        if page["module"] != "pages.not_found_404"
                    ],
                    # Add author link right after the navigation links
                    dbc.NavLink(
                        children=[
                            dmc.Group(
                                [
                                    dmc.Text(
                                        "Created by ",
                                        c="white",
                                        size="sm",
                                        style={
                                            "font-family": "Arial, sans-serif",
                                        },
                                    ),
                                    "Sang-Buster",
                                ],
                                mt=20,
                                justify="left",
                                gap="xs",
                            )
                        ],
                        href="https://github.com/Sang-Buster",
                        target="_blank",
                        style={
                            "color": "white",
                            "text-decoration": "none",
                            "font-family": "Arial, sans-serif",
                            "font-size": 15,
                            "margin-top": "15px",
                            "border-top": "1px solid rgba(255, 255, 255, 0.1)",
                            "padding-top": "15px",
                        },
                        className="nav-link",
                        id={"type": "dynamic-link", "index": "author"},
                    ),
                ],
                size="xs",
                fullScreen=False,
                id="full-modal",
                zIndex=10000,
                centered=True,
                withCloseButton=False,
                className="custom-nav-menu",
                transitionProps={"transition": "fade", "duration": 200},
                overlayProps={"opacity": 0, "blur": 0},
                styles={
                    "modal": {
                        "backgroundColor": "transparent",
                        "color": "white",
                        "minWidth": "280px",
                        "maxWidth": "300px",
                        "height": "100vh",
                        "position": "fixed",
                        "top": "50%",
                        "transform": "translateY(-50%)",
                        "left": "0",
                        "margin": "0",
                        "borderRadius": "0 10px 10px 0",
                        "borderRight": "1px solid rgba(255, 255, 255, 0.1)",
                        "boxShadow": "none",
                    },
                    "header": {
                        "backgroundColor": "transparent",
                        "color": "white",
                        "padding": "20px 20px 10px 20px",
                        "borderBottom": "1px solid rgba(255, 255, 255, 0.1)",
                    },
                    "title": {
                        "color": "white",
                        "fontWeight": "bold",
                    },
                    "body": {
                        "padding": "10px 10px 10px 20px",
                    },
                    "overlay": {
                        "backgroundColor": "rgba(0, 0, 0, 0.5)",
                    },
                    "inner": {
                        "justifyContent": "flex-start",
                        "alignItems": "flex-start",
                    },
                },
            ),
        ],
        className="navbar-grid",
        style={
            "background": "transparent",
            "border": "none",
            "boxShadow": "none",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "flex-start",
            "height": "60px",
            "padding": "0",
        },
    )


@callback(
    Output("full-modal", "opened"),
    Input("nav-btn", "n_clicks"),
    State("full-modal", "opened"),
    prevent_initial_call=True,
)
def toggle_modal(_, opened):
    return not opened


@callback(
    Output("full-modal", "opened", allow_duplicate=True),
    Input({"type": "dynamic-link", "index": ALL}, "n_clicks"),
    State("full-modal", "opened"),
    prevent_initial_call=True,
)
def update_modal(n, opened):
    if True in n:
        return not opened
    return opened
