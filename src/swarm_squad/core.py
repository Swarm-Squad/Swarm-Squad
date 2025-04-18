"""
Core application setup for Swarm Squad Dash app.
"""

import atexit
import os
import signal
import socket
import subprocess
import sys
import time

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


def is_port_in_use(port, host="localhost"):
    """Check if the port is already in use"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((host, port))
    sock.close()

    if result == 0:
        # Connection succeeded, port is in use
        return True
    else:
        # Connection failed, port is free
        return False


def force_release_port(port, host="localhost"):
    """Force release a port by finding and killing the process using it"""
    # First try to connect to check if something is listening
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((host, port))
    sock.close()

    if result == 0:  # Port is in use
        logger.debug(f"Port {port} is confirmed to be in use")
        try:
            # Try multiple methods to kill the process using the port (Linux only)
            try:
                # First try fuser (commonly available)
                try:
                    logger.info(
                        f"Attempting to kill process using port {port} with fuser"
                    )
                    os.system(f"fuser -k {port}/tcp >/dev/null 2>&1")
                except Exception:
                    pass

                # Try lsof as an alternative
                try:
                    logger.info(
                        f"Attempting to find and kill process using port {port} with lsof"
                    )
                    process = subprocess.run(
                        ["lsof", "-i", f":{port}", "-t"],
                        capture_output=True,
                        text=True,
                    )
                    if process.stdout.strip():
                        for pid in process.stdout.strip().split("\n"):
                            if pid:
                                os.system(f"kill -9 {pid} >/dev/null 2>&1")
                                logger.info(f"Killed process {pid} using port {port}")
                except Exception:
                    pass

                # Try netstat as another alternative
                try:
                    logger.info(
                        f"Attempting to find and kill process using port {port} with netstat"
                    )
                    process = subprocess.run(
                        ["netstat", "-tlnp"], capture_output=True, text=True
                    )
                    for line in process.stdout.split("\n"):
                        if f":{port}" in line and "LISTEN" in line:
                            parts = line.split()
                            for part in parts:
                                if "/" in part:
                                    pid = part.split("/")[0]
                                    os.system(f"kill -9 {pid} >/dev/null 2>&1")
                                    logger.info(
                                        f"Killed process {pid} using port {port}"
                                    )
                except Exception:
                    pass

            except Exception as e:
                logger.warning(f"Could not kill process using port {port}: {e}")

            # Wait a moment to allow the port to be released
            time.sleep(1)

            # Check again if the port is in use
            check_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            check_sock.settimeout(1)
            check_result = check_sock.connect_ex((host, port))
            check_sock.close()

            if check_result == 0:
                logger.warning(f"Port {port} is still in use after kill attempts")
                return False
            else:
                logger.info(f"Successfully released port {port}")
                return True

        except Exception as e:
            logger.error(f"Could not release port {port}: {e}")
            return False
    else:
        logger.debug(f"Port {port} is already free")
        return True


def create_app():
    """
    Factory function to create and configure the Dash application instance.
    """
    global app, ws_manager

    # Check if Dash port is already in use and attempt to release it
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        if is_port_in_use(8050):
            logger.warning("Dash port 8050 is already in use, attempting to release it")
            if not force_release_port(8050):
                logger.error(
                    "Failed to release port 8050. The application may fail to start."
                )

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
            # Also ensure the Dash port is released
            force_release_port(8050)
            sys.exit(0)

        # Register the signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Register WebSocket cleanup via atexit
        atexit.register(ws_manager.cleanup_websocket)
        # Register Dash port cleanup via atexit
        atexit.register(lambda: force_release_port(8050))
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
