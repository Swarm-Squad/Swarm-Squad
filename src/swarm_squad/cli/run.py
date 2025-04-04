"""
Run a specific simulation script from Swarm Squad.
"""

import importlib
import sys

from swarm_squad.cli.list import get_simulation_scripts
from swarm_squad.utils.logger import get_logger

# Create module logger
logger = get_logger("cli.run")


def run_simulation(script_name):
    """
    Run a specific simulation script.

    Args:
        script_name (str): Name of the simulation script to run (without .py extension)

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    available_scripts = get_simulation_scripts()

    if script_name not in available_scripts:
        logger.error(f"Simulation '{script_name}' not found.")
        # Print error directly to stderr for user visibility
        print(f"Error: Simulation '{script_name}' not found.", file=sys.stderr)
        print("Available simulations:", file=sys.stderr)
        for script in available_scripts:
            print(f"  - {script}", file=sys.stderr)
        return 1

    try:
        # Import and run the simulation module
        module_path = f"swarm_squad.scripts.{script_name}"
        logger.info(f"Running simulation: {script_name}")
        # Pass any remaining sys.argv to the script (e.g., for its own argument parsing)
        # Note: sys.argv[0] will be the main app.py path
        importlib.import_module(module_path)
        logger.info(f"Simulation '{script_name}' completed successfully.")
        return 0
    except ModuleNotFoundError:
        logger.error(f"Could not find simulation module: {module_path}")
        print(
            f"Error: Could not find simulation module: {module_path}", file=sys.stderr
        )
        return 1
    except Exception as e:
        logger.error(f"Error running simulation '{script_name}': {e}", exc_info=True)
        # Print error directly to stderr for user visibility
        print(f"Error running simulation '{script_name}': {e}", file=sys.stderr)
        return 1


def main(script_name=None):
    """
    CLI entry point for running simulations.
    Expects script_name to be passed from the main command parser.

    Args:
        script_name (str, optional): The name of the script to run. Defaults to None.

    Returns:
        int: Exit code.
    """
    if not script_name:
        # This case should ideally be caught by the main parser, but handle defensively.
        logger.warning("No simulation script provided to run.main.")
        # Print usage help directly to stderr
        print(
            "Please specify a simulation to run using `... run <script_name>`.",
            file=sys.stderr,
        )
        print("Available simulations:", file=sys.stderr)
        for script in get_simulation_scripts():
            print(f"  - {script}", file=sys.stderr)
        return 1

    # Clear sys.argv except for the program name itself before running the script
    # This prevents the script from seeing the 'run' command or its own name as args
    # unless specific arguments were intended for it (which are not handled here yet).
    # A more robust solution might involve passing remaining args explicitly.
    original_argv_0 = sys.argv[0]
    sys.argv = [original_argv_0]

    return run_simulation(script_name)


if __name__ == "__main__":
    # Handle direct execution if needed, though unlikely with CLI structure
    print(
        "ERROR: run.py should not be run directly. Use `python -m swarm_squad.app run <script>`.",
        file=sys.stderr,
    )
    sys.exit(1)
