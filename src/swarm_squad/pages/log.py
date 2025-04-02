import dash
import dash_mantine_components as dmc
from dash import html

dash.register_page(
    __name__,
    path="/log",
    order=5,  # Last page
    title="Log | Swarm Squad",
    description="Information about Swarm Squad",
)

layout = html.Div(
    [
        html.Div(className="illumination-1"),
        html.Div(className="illumination-2"),
        html.Div(className="illumination-3"),
        html.Div(className="stars"),
        dmc.Container(
            [
                dmc.Title("Information", style={"color": "white"}, size="h1"),
                # Add your info content here
            ],
            fluid=True,
            style={"height": "100vh", "position": "relative"},
        ),
    ],
    style={"minHeight": "100vh", "position": "relative", "overflow": "hidden"},
)
