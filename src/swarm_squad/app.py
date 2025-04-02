import atexit
import os
import signal
import sys

import dash
import dash_mantine_components as dmc
from dash import Dash, dcc, html
from flask_cors import CORS

from swarm_squad.pages.footer import footer
from swarm_squad.pages.nav import navbar
from swarm_squad.utils.websocket_manager import WebSocketManager

# Initialize WebSocket manager outside the app
# This ensures it's only initialized once, even if the app reloads in debug mode
ws_manager = WebSocketManager()


# Define a signal handler to ensure cleanup
def signal_handler(sig, frame):
    print(f"[INFO] Signal {sig} received, cleaning up resources...")
    if hasattr(app, "ws_manager"):
        app.ws_manager.cleanup_websocket(force=True)
    sys.exit(0)


# Register the signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

app = Dash(
    __name__,
    title="Swarm Squad",
    use_pages=True,
    update_title=False,
    suppress_callback_exceptions=True,
    prevent_initial_callbacks=True,
    meta_tags=[
        {
            "name": "description",
            "content": "A simulation framework for multi-agent systems.",
        },
        {
            "name": "keywords",
            "content": "Swarm Squad, Multi-agent systems, LLM, AI, Simulation, Dash",
        },
    ],
)

# Attach the WebSocket manager to the app
app.ws_manager = ws_manager

server = app.server
# Enable CORS for the Flask server
CORS(
    server,
    resources={
        r"/websocket/*": {
            "origins": ["http://localhost:8050", "http://127.0.0.1:8050"],
            "allow_headers": ["*"],
            "expose_headers": ["*"],
            "methods": ["GET", "POST", "OPTIONS"],
            "supports_credentials": True,
        }
    },
)

# Start the websocket server
# Only start if this is the main process, not a reloader process
if not os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    # Start the websocket server - port checking is handled within start_websocket
    app.ws_manager.start_websocket()

# Make sure the WebSocket server is cleaned up when the app exits
atexit.register(app.ws_manager.cleanup_websocket)

app.layout = dmc.MantineProvider(
    theme={
        "colorScheme": "dark",
        "primaryColor": "blue",
    },
    children=html.Div(
        [
            navbar(),
            html.Div(
                [
                    dash.page_container,
                    dcc.Store("past-launches-data"),
                    dcc.Store("next-launch-data"),
                    dcc.Store("last-update"),
                ],
                id="page-content",
                style={"minHeight": "100vh", "position": "relative"},
            ),
            footer,
        ]
    ),
)


# Add callback to blur content when nav modal is open
@app.callback(
    dash.Output("page-content", "className"), dash.Input("full-modal", "opened")
)
def toggle_content_blur(modal_opened):
    if modal_opened:
        return "content-blur"
    return ""


# Add a main function to serve as the entry point
def main():
    try:
        app.run(debug=True)
    except Exception as e:
        print(f"[ERROR] App error: {e}")
    finally:
        # Force cleanup the WebSocket server
        app.ws_manager.cleanup_websocket(force=True)
    return 0


if __name__ == "__main__":
    main()
