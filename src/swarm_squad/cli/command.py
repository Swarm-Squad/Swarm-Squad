"""
Command parser for Swarm Squad CLI.
"""

import argparse
import logging
import os
import sys
from importlib import import_module

from swarm_squad.utils.db_init import initialize_database
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

    # Add global verbose flag
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging output (DEBUG level)",
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
        "--debug", action="store_true", help="Enable debug mode (for app reloading)"
    )
    webui_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging output (DEBUG level)",
    )

    # Add list command
    list_parser = subparsers.add_parser(
        "list", help="List available simulation scripts"
    )
    list_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging output (DEBUG level)",
    )

    # Add run command
    run_parser = subparsers.add_parser("run", help="Run a specific simulation script")
    run_parser.add_argument("script", help="Name of the simulation script to run")
    run_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging output (DEBUG level)",
    )

    return parser


def execute_command(args):
    """
    Execute the specified command based on parsed arguments.
    Handles log level setting and process-specific initialization.

    Args:
        args (argparse.Namespace): Parsed command-line arguments

    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    command = args.command
    is_debug = getattr(args, "debug", False)  # For app reloading (webui only)
    is_verbose = getattr(args, "verbose", False)  # For log level (all commands)

    # --- Set Log Level (Always) ---
    if is_verbose:
        # Verbose flag overrides all and sets DEBUG level
        log_level = logging.DEBUG
    elif not command:  # Default behavior
        # Default: Run webui with INFO level logs (not DEBUG)
        log_level = logging.INFO
    elif command == "webui":
        # Webui: INFO level by default
        log_level = logging.INFO
    elif command in ["list", "run"]:
        # List/Run: WARNING level by default
        log_level = logging.WARNING
    else:
        # Fallback: ERROR level for unknown commands
        log_level = logging.ERROR

    set_log_level(log_level)

    # Only log the level setting if verbose
    if is_verbose:
        logger.debug(
            f"Process ID {os.getpid()}: Set log level to {logging.getLevelName(log_level)}"
        )

    # --- Initialize Database (will self-guard) ---
    initialize_database()
    # ---------------------------------------------

    # --- Execute Non-Web Commands ---
    if command in ["list", "run"]:
        logger.info(f"Running command: {command}")
        try:
            module_name = f"swarm_squad.cli.{command}"
            if is_verbose:
                logger.debug(f"Importing module: {module_name}")
            module = import_module(module_name)
            if command == "run":
                if hasattr(args, "script") and args.script:
                    return module.main(script_name=args.script)
                else:
                    logger.error("Run command called without a script name argument.")
                    # Let run.main handle the error message
                    return module.main()
            else:  # list
                return module.main()
        except ImportError:
            logger.error(f"Command module '{module_name}' could not be imported.")
            return 1
        except Exception as e:
            logger.error(f"Error executing command '{command}': {e}", exc_info=True)
            return 1
    elif command and command != "webui":  # Invalid command
        logger.error(f"Invalid command received after parsing: {command}")
        get_main_parser().print_usage(file=sys.stderr)
        return 1
    # --------------------------------

    # --- Execute Web UI Command (Default or Explicit) ---
    # This part runs in both processes, but internal checks prevent duplication
    try:
        # Check which process we're in
        is_reloader = os.environ.get("WERKZEUG_RUN_MAIN") == "true"

        if is_verbose:
            logger.debug(f"Process ID {os.getpid()}: Preparing to run web UI...")
        elif is_reloader:
            # Only show the startup message in the reloader process (which actually serves requests)
            logger.info("Starting Swarm Squad web interface...")

        from swarm_squad.core import create_app

        # create_app handles internal check for signal/atexit registration
        app, ws_manager = create_app()

        # ws_manager.start_websocket() handles internal check
        if ws_manager:
            ws_manager.start_websocket()
        else:
            # This shouldn't happen if create_app succeeds
            logger.error("WebSocket Manager not available after create_app")
            return 1

        # Set debug mode for app.run based on the --debug flag (or default if no command)
        # Default behavior (no command) also enables app debugging
        use_debug_mode = is_debug or (not command)
        if is_verbose:
            logger.info(
                f"Process ID {os.getpid()}: Starting Dash server (debug={use_debug_mode})..."
            )
        app.run(debug=use_debug_mode)
        return 0  # Should typically not be reached if server runs indefinitely

    except Exception as e:
        logger.critical(f"Failed to start web UI: {e}", exc_info=True)
        return 1
    # ----------------------------------------------------
