import dash
import dash_mantine_components as dmc
from dash import html

from swarm_squad.utils.map_fetcher import read_map_html

dash.register_page(
    __name__,
    path="/map",
    order=1,
    title="Map | Swarm Squad",
    description="Interactive map for swarm intelligence",
)

# Load map content once when the module is imported
MAP_CONTENT = read_map_html()

layout = html.Div(
    [
        dmc.Container(
            [
                dmc.Stack(
                    [
                        dmc.Center(
                            dmc.Paper(
                                html.Iframe(
                                    srcDoc=MAP_CONTENT,  # Use pre-loaded content
                                    style={
                                        "width": "90vw",
                                        "height": "80vh",
                                        "border": "none",
                                        "borderRadius": "10px",
                                        "backgroundColor": "transparent",
                                    },
                                ),
                                shadow="lg",
                                radius="md",
                                withBorder=True,
                                style={
                                    "backgroundColor": "transparent",
                                    "width": "90vw",
                                    "height": "80vh",
                                },
                            ),
                        ),
                    ],
                    justify="center",
                    align="center",
                    gap="xl",
                ),
            ],
            fluid=True,
            size="100%",
            style={
                "height": "100vh",
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
            },
        ),
    ],
    style={
        "minHeight": "100vh",
        "position": "relative",
        "overflow": "hidden",
        "display": "flex",
        "alignItems": "center",
        "justifyContent": "center",
    },
)
