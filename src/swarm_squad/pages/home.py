import dash
import dash_mantine_components as dmc
from dash import dcc, html
from dash_iconify import DashIconify

dash.register_page(
    __name__,
    path="/",
    order=0,  # First page
    image="favicon.ico",
    title="Home | Swarm Squad",
    description="Explore the world of multi-agent systems and swarm intelligence through "
    "interactive simulations and visualizations",
)

layout = html.Div(
    [
        # Background elements (keep these)
        html.Div(className="illumination-1"),
        html.Div(className="illumination-2"),
        html.Div(className="illumination-3"),
        html.Div(className="stars"),
        # Text content - adjusted position
        dmc.Container(
            [
                dmc.Stack(
                    children=[
                        dmc.Title(
                            "Welcome to Swarm Squad",
                            style={"color": "white"},
                            size="h1",
                        ),
                        dmc.Text(
                            children=[
                                "Dive into the fascinating world of multi-agent systems and swarm intelligence. "
                                "Explore interactive simulations, visualize agent behaviors, and discover the "
                                "power of collective intelligence."
                            ],
                            style={"color": "white"},
                            size="lg",
                        ),
                        dmc.Stack(
                            [
                                html.Div(
                                    dcc.Link(
                                        dmc.Button(
                                            "Explore",
                                            variant="outline",
                                            color="blue",
                                            size="lg",
                                            rightSection=DashIconify(
                                                icon="mdi:rocket-launch-outline",
                                                width=30,
                                            ),
                                            style={
                                                "width": "fit-content",
                                                "display": "inline-flex",
                                            },
                                        ),
                                        href="/map",
                                        style={
                                            "text-decoration": "none",
                                            "width": "fit-content",
                                            "display": "block",
                                        },
                                    ),
                                    style={"width": "fit-content"},
                                ),
                            ],
                            align="flex-start",
                            style={"width": "fit-content"},
                        ),
                    ],
                    gap="xl",
                    style={
                        "position": "absolute",
                        "bottom": "40%",
                        "left": "20%",
                        "maxWidth": "600px",
                    },
                ),
            ],
            fluid=True,
            style={"height": "100vh", "position": "relative"},
        ),
        # Add the boids.js script here
        html.Script(src="/assets/js/p5.js"),
        html.Script(src="/assets/js/boids.js"),
    ],
    style={
        "minHeight": "100vh",
        "position": "relative",
        "overflow": "hidden",
    },  # Removed background color
)
