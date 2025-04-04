"""
Centralized logging configuration for Swarm Squad.
"""

import logging
import sys

# Global variable to store the root logger
_root_logger = None


def setup_logger(name="swarm_squad", level=logging.INFO):
    """
    Configure and return a logger instance with consistent formatting.

    Args:
        name (str): Logger name
        level (int): Initial logging level

    Returns:
        logging.Logger: Configured logger instance
    """
    global _root_logger

    # Get the root logger for the application
    logger = logging.getLogger(name)

    # Only configure if it hasn't been configured yet
    if not logger.handlers:
        logger.setLevel(level)  # Set the initial level

        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)  # Handler level should be permissive

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Add formatter to console handler
        console_handler.setFormatter(formatter)

        # Add console handler to logger
        logger.addHandler(console_handler)

        # Prevent messages from propagating to the root logger
        logger.propagate = False

        _root_logger = logger  # Store the configured root logger

    return logger


def set_log_level(level):
    """Set the logging level for the root application logger."""
    global _root_logger
    if _root_logger:
        _root_logger.setLevel(level)
        # Optionally log the level change at DEBUG level itself
        # _root_logger.debug(f"Set log level to {logging.getLevelName(level)}")
    else:
        # This case should ideally not happen if setup_logger is called first
        print(
            "[ERROR] Root logger not initialized before setting level!", file=sys.stderr
        )


# Create the main application logger with default INFO level
logger = setup_logger()


def get_logger(module_name=None):
    """
    Get a logger for a specific module.

    Args:
        module_name (str, optional): Module name to append to the base logger name

    Returns:
        logging.Logger: Logger instance for the module
    """
    base_name = "swarm_squad"
    if module_name:
        # Use hierarchical naming (e.g., swarm_squad.cli.run)
        logger_name = f"{base_name}.{module_name}"
    else:
        logger_name = base_name

    # Return the named logger instance (inherits level from root by default)
    return logging.getLogger(logger_name)
