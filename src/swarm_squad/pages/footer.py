import dash_mantine_components as dmc
from dash_iconify import DashIconify

GITHUB = "https://github.com/Swarm-Squad/Swarm-Squad"
WEB = "https://swarm-squad.com/"
DOC = "https://docs.swarm-squad.com/"
CONTACT_ICON_WIDTH = 25

footer = dmc.Grid(
    [
        dmc.GridCol(
            [
                dmc.Container(
                    className="footer-container",
                    style={
                        "display": "flex",
                        "justifyContent": "center",
                        "alignItems": "center",
                        "backgroundColor": "rgba(0, 0, 0, 0.5)",
                        "position": "fixed",
                        "bottom": "0",
                        "left": "0",
                        "right": "0",
                        "width": "100vw",
                        "height": "50px",
                        "padding": "0",
                        "margin": "0",
                        "maxWidth": "100vw",
                    },
                    fluid=True,
                    children=[
                        dmc.Group(
                            children=[
                                dmc.Anchor(
                                    children=[
                                        DashIconify(
                                            icon="mdi:github",
                                            width=CONTACT_ICON_WIDTH,
                                            color="white",
                                        )
                                    ],
                                    href=GITHUB,
                                    target="_blank",
                                    className="footer-icon",
                                    style={"display": "flex", "alignItems": "center"},
                                ),
                                dmc.Anchor(
                                    children=[
                                        DashIconify(
                                            icon="mdi:web",
                                            width=CONTACT_ICON_WIDTH,
                                            color="white",
                                        )
                                    ],
                                    href=WEB,
                                    target="_blank",
                                    className="footer-icon",
                                    style={"display": "flex", "alignItems": "center"},
                                ),
                                dmc.Anchor(
                                    children=[
                                        DashIconify(
                                            icon="mdi:book-open-variant-outline",
                                            width=CONTACT_ICON_WIDTH,
                                            color="white",
                                        )
                                    ],
                                    href=DOC,
                                    target="_blank",
                                    className="footer-icon",
                                    style={"display": "flex", "alignItems": "center"},
                                ),
                            ],
                            className="footer-icons-group",
                            justify="center",
                            style={
                                "display": "flex",
                                "justifyContent": "center",
                                "alignItems": "center",
                                "width": "100%",
                                "gap": "40px",
                                "margin": "0",
                            },
                        )
                    ],
                )
            ],
            span="auto",
            style={"padding": "0", "margin": "0"},
        )
    ],
    className="footer-grid",
    style={
        "position": "fixed",
        "bottom": "0",
        "left": "0",
        "right": "0",
        "width": "100vw",
        "padding": "0",
        "margin": "0",
        "zIndex": "100",
    },
    justify="center",
    align="center",
    gutter=0,
)
