import dash
import dash_mantine_components as dmc
from dash import html

dash.register_page(
    __name__,
    path="/chat",
    order=4,  # Fifth page
    title="Chat | Swarm Squad",
    description="Interactive chat interface",
)

layout = html.Div(
    [
        html.Div(className="illumination-1"),
        html.Div(className="illumination-2"),
        html.Div(className="illumination-3"),
        html.Div(className="stars"),
        dmc.Container(
            [
                dmc.Title("Chat", style={"color": "white"}, size="h1"),
                # Add your chat content here
            ],
            fluid=True,
            style={"height": "100vh", "position": "relative"},
        ),
    ],
    style={"minHeight": "100vh", "position": "relative", "overflow": "hidden"},
)
