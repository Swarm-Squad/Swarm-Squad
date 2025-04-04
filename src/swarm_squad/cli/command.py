"""
Command parser for Swarm Squad CLI.
"""

import argparse
import logging
import os  # Needed for WERKZEUG_RUN_MAIN check
from importlib import import_module

from swarm_squad.utils.logger import get_logger, set_log_level

# Create module logger - Note: Level is inherited from root initially
logger = get_logger("cli.command")


def get_main_parser():
    """
    Create the main argument parser for the Swarm Squad CLI.

    Returns:
        argparse.ArgumentParser: The main argument parser
    """
    parser = argparse.ArgumentParser(
        description="Swarm Squad - A simulation framework for multi-agent systems",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="commands",
        description="valid commands",
        help="Use <command> --help for command-specific help",
        required=False,  # Make command optional for default behavior
    )

    # Add webui command
    webui_parser = subparsers.add_parser(
        "webui", help="Run the Swarm Squad web user interface"
    )
    webui_parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode (more verbose logging)"
    )

    # Add list command
    subparsers.add_parser(
        "list", help="List available simulation scripts (less verbose logging)"
    )

    # Add run command
    run_parser = subparsers.add_parser(
        "run", help="Run a specific simulation script (less verbose logging)"
    )
    run_parser.add_argument("script", help="Name of the simulation script to run")

    return parser


def execute_command(args):
    """
    Execute the specified command based on parsed arguments, setting log level first.

    Args:
        args (argparse.Namespace): Parsed command-line arguments

    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    command = args.command
    is_debug = getattr(args, "debug", False)  # Get debug flag if exists

    # --- Set Log Level FIRST ---
    if not command:
        # Default behavior (webui, debug ON)
        log_level = logging.DEBUG
    elif command == "webui":
        log_level = logging.DEBUG if is_debug else logging.INFO
    elif command in ["list", "run"]:
        log_level = logging.WARNING
    else:
        # Should not happen with argparse choices
        log_level = logging.ERROR

    set_log_level(log_level)
    logger.debug(
        f"Set log level to {logging.getLevelName(log_level)}"
    )  # Log level change itself at DEBUG
    # ---------------------------

    app = None
    ws_manager = None

    # --- Create App & Start WebSocket (if needed) ---
    if not command or command == "webui":
        from swarm_squad.core import create_app

        app, ws_manager = create_app()  # Create the app instance

        # Start WS only for webui/default, and only in main process
        if not os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            if ws_manager:
                ws_manager.start_websocket()
    # -----------------------------------------------

    # --- Execute Command ---
    if not command:
        # Default behavior: run webui with debug ON
        logger.info("No command specified, running default: webui with debug mode.")
        if app:
            # The log level was already set to DEBUG above
            return app.run(debug=True)
        else:
            logger.error("App instance not created for default command.")
            return 1

    elif command == "webui":
        logger.info(f"Running command: {command}")
        # App and ws_manager are already created above
        # The webui.main function will call app.run()
        module = import_module("swarm_squad.cli.webui")
        # We pass the created app instance to webui.main
        return module.main(app_instance=app)

    elif command in ["list", "run"]:
        logger.info(f"Running command: {command}")
        # These commands don't need the app instance directly
        try:
            module_name = f"swarm_squad.cli.{command}"
            logger.debug(f"Importing module: {module_name}")
            module = import_module(module_name)

            if command == "run":
                # Pass the script name to run.main
                if hasattr(args, "script") and args.script:
                    return module.main(script_name=args.script)
                else:
                    logger.error("Run command called without a script name argument.")
                    # Attempt to run main anyway, it should print its own error
                    return module.main()
            else:  # For list command
                return module.main()

        except ImportError:
            logger.error(f"Command module '{module_name}' could not be imported.")
            return 1
        except Exception as e:
            logger.error(f"Error executing command '{command}': {e}", exc_info=True)
            return 1

    else:
        # Should be caught by argparse, but log error if reached
        logger.error(f"Invalid command received after parsing: {command}")
        return 1
