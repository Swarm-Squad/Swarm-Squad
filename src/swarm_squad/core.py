"""
Core application setup for Swarm Squad Dash app.
"""

import atexit
import os
import signal
import sys

import dash
import dash_mantine_components as dmc
from dash import Dash, Input, Output, dcc, html
from flask_cors import CORS

from swarm_squad.pages.footer import footer
from swarm_squad.pages.nav import navbar
from swarm_squad.utils.logger import get_logger
from swarm_squad.utils.websocket_manager import WebSocketManager

# Module logger
logger = get_logger("core")

# Global references (to be initialized by create_app)
app = None
ws_manager = None


def create_app():
    """
    Factory function to create and configure the Dash application instance.
    """
    global app, ws_manager

    # Initialize WebSocket manager (singleton)
    ws_manager = WebSocketManager()

    # --- Signal Handling and Cleanup Registration (Main Process Only) ---
    # Prevents duplicate registration/logging in Werkzeug reloader process
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        logger.debug("Registering signal handlers and atexit cleanup in main process.")

        # Define a signal handler to ensure cleanup
        def signal_handler(sig, frame):
            # Use logger defined outside the handler
            logger.info(f"Signal {sig} received, cleaning up resources...")
            if ws_manager:
                ws_manager.cleanup_websocket(force=True)
            sys.exit(0)

        # Register the signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Register WebSocket cleanup via atexit
        atexit.register(ws_manager.cleanup_websocket)
    else:
        logger.debug("Skipping signal/atexit registration in reloader process.")
    # -------------------------------------------------------------------

    # --- Dash App Initialization ---
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

    # Attach the WebSocket manager to the app instance for potential access elsewhere
    # Although direct access might be less common now with the manager being a singleton
    app.ws_manager = ws_manager

    # --- Flask Server Configuration (CORS) ---
    server = app.server
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

    # --- App Layout Definition ---
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
                        dcc.Store(id="past-launches-data"),
                        dcc.Store(id="next-launch-data"),
                        dcc.Store(id="last-update"),
                    ],
                    id="page-content",
                    style={"minHeight": "100vh", "position": "relative"},
                ),
                footer,
            ]
        ),
    )

    # --- App Callbacks ---
    register_callbacks(app)

    logger.debug("Dash application created successfully.")
    return app, ws_manager


def register_callbacks(app_instance):
    """
    Register application-level callbacks.
    """

    @app_instance.callback(
        Output("page-content", "className", allow_duplicate=True),
        Input("full-modal", "opened"),
        prevent_initial_call=True,
    )
    def toggle_content_blur(modal_opened):
        logger.debug(f"toggle_content_blur triggered. modal_opened: {modal_opened}")
        if modal_opened:
            return "content-blur"
        return ""
