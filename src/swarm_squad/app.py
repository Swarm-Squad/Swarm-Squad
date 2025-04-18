"""
Swarm Squad Application Entry Point.

Handles command-line interface routing and application startup.
"""

import atexit
import signal
import sys

from swarm_squad.utils.logger import get_logger

# Initialize logger for the entry point
logger = get_logger("app_entry")


def main():
    """
    Main entry point function.
    Parses command-line arguments and executes the appropriate command.

    Command-line usage:
        python -m swarm_squad.app              # Run web UI with debug mode on
        python -m swarm_squad.app webui        # Run web UI with debug mode off
        python -m swarm_squad.app webui --debug # Run web UI with debug mode on
        python -m swarm_squad.app list         # List available simulations
        python -m swarm_squad.app run <sim>    # Run a specific simulation

    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    logger.debug("Application entry point reached.")
    exit_code = 1  # Default to error exit code

    # Register a cleanup function to ensure resources are released
    def cleanup_resources():
        try:
            from swarm_squad.core import force_release_port

            # Force release the Dash and WebSocket ports
            logger.debug("Final cleanup: Ensuring ports are released")
            force_release_port(8050)  # Dash port
            force_release_port(8051)  # WebSocket port
        except Exception as e:
            logger.error(f"Error during final cleanup: {e}")

    # Register cleanup with atexit
    atexit.register(cleanup_resources)

    # Register signal handlers for graceful termination
    def signal_handler(sig, frame):
        logger.info(f"Signal {sig} received, performing cleanup...")
        cleanup_resources()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # NOTE: create_app is implicitly called within cli.command for webui
        # It initializes the app and ws_manager needed by the commands.
        from swarm_squad.cli.command import execute_command, get_main_parser

        parser = get_main_parser()
        args = parser.parse_args()

        logger.debug(f"Parsed CLI arguments: {args}")
        exit_code = execute_command(args)

    except ImportError as e:
        logger.critical(f"Failed to import necessary modules: {e}", exc_info=True)
        print(
            f"Import Error: {e}. Please ensure dependencies are installed.",
            file=sys.stderr,
        )
        exit_code = 1

    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}", exc_info=True)
        print(f"Unexpected Error: {e}", file=sys.stderr)
        exit_code = 1

    finally:
        logger.debug(f"Application exiting with code {exit_code}.")
        # Perform cleanup explicitly before exiting
        cleanup_resources()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
