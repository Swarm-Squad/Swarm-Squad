"""
List available simulation scripts in Swarm Squad.
"""

import os
import sys
from pathlib import Path

from swarm_squad.utils.logger import get_logger

# Create module logger
logger = get_logger("cli.list")


def get_simulation_scripts():
    """
    Get a list of available simulation scripts from the scripts directory.

    Returns:
        list: List of script names without the .py extension
    """
    # Get the path to the scripts directory
    scripts_dir = Path(__file__).resolve().parent.parent / "scripts"

    # Find all Python files in the scripts directory
    scripts = []
    try:
        for file in os.listdir(scripts_dir):
            if file.endswith(".py") and not file.startswith("__"):
                scripts.append(file[:-3])  # Remove .py extension
    except FileNotFoundError:
        logger.error(f"Scripts directory not found: {scripts_dir}")
        return []  # Return empty list if directory doesn't exist

    return sorted(scripts)


def main():
    """
    List available simulation scripts.
    """
    scripts = get_simulation_scripts()

    if not scripts:
        logger.warning("No simulation scripts found.")
        # No need to print here, logger handles it if level is WARNING or lower
        return 1

    logger.info(f"Found {len(scripts)} simulation scripts.")
    # Print the list directly to stdout, regardless of log level
    print("Available simulations:")
    for script in scripts:
        print(f"  - {script}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
