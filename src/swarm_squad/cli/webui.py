"""
Run the Swarm Squad web user interface.
"""

import argparse
import logging
import sys

# Removed direct import of app from swarm_squad.app
# The app instance will be passed in from command.py
from swarm_squad.utils.logger import get_logger

# Create module logger
logger = get_logger("cli.webui")


def main(app_instance=None):
    """
    Run the Swarm Squad web user interface.
    Expects the app instance to be passed in and log level to be set.

    Args:
        app_instance (Dash, optional): The created Dash app instance. Defaults to None.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    if not app_instance:
        logger.critical("Web UI command called without an app instance.")
        print(
            "Error: Web UI cannot start without an application instance.",
            file=sys.stderr,
        )
        return 1

    parser = argparse.ArgumentParser(
        description="Run the Swarm Squad web user interface"
    )
    # Define --debug arg for help text, but value is determined by log level set upstream
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode (more verbose logging)"
    )

    # Parse args known to webui
    args, _ = parser.parse_known_args()

    try:
        # Determine debug mode based on the root logger's level
        is_debug_mode = logger.root.level == logging.DEBUG
        debug_log_msg = "enabled" if is_debug_mode else "disabled"
        logger.info(f"Starting web UI with debug mode {debug_log_msg}")

        # Use the passed-in app instance to run the server
        app_instance.run(debug=is_debug_mode)
        return 0

    except Exception as e:
        logger.error(f"Error running web UI: {e}", exc_info=True)
        print(f"Critical Error running web UI: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    # This direct execution path is less likely now with the CLI structure
    # but handle it defensively.
    print(
        "ERROR: webui.py should not be run directly. Use `python -m swarm_squad.app webui`.",
        file=sys.stderr,
    )
    # Attempt to create a default app instance for direct run (might lack proper context)
    try:
        from swarm_squad.core import create_app
        from swarm_squad.utils.logger import set_log_level

        set_log_level(logging.INFO)  # Default to INFO if run directly
        app, _ = create_app()
        sys.exit(main(app_instance=app))
    except Exception as e:
        print(f"Failed to run webui directly: {e}", file=sys.stderr)
        sys.exit(1)
