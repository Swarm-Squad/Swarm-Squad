"""
Utility to initialize the Swarm Squad SQLite database.
"""

import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

from swarm_squad.utils.logger import get_logger

logger = get_logger("db_init")


# Define multiple possible database locations to check
# This ensures the database works in both development and installed modes
def get_db_path():
    """Get the appropriate database path based on environment"""
    # Try to load .env file from several possible locations
    possible_env_locations = [
        Path.cwd() / ".env",
        Path.cwd().parent / ".env",
        Path.home() / ".swarm_squad" / ".env",
        Path(__file__).parent.parent.parent.parent / ".env",  # project root
        Path(__file__).parent.parent / ".env",  # src/swarm_squad
    ]

    for env_path in possible_env_locations:
        if env_path.exists():
            logger.debug(f"Loading environment from {env_path}")
            load_dotenv(dotenv_path=env_path)
            break

    # Check for DATABASE_PATH in environment variables
    env_db_path = os.environ.get("DATABASE_PATH")
    if env_db_path:
        db_path = Path(env_db_path)
        logger.debug(f"Using database path from environment: {db_path}")
        return db_path

    # Option 1: Relative to this file (development mode)
    script_dir_db_path = Path(__file__).parent.parent / "data" / "swarm_squad.db"

    # Option 2: User's home directory
    home_db_path = Path.home() / ".swarm_squad" / "swarm_squad.db"

    # Try the options in order and use the first one that exists
    # If none exist, default to the home_db_path
    if script_dir_db_path.exists():
        logger.debug(f"Using existing database at {script_dir_db_path}")
        return script_dir_db_path

    # Create home directory if it doesn't exist
    if not home_db_path.parent.exists():
        home_db_path.parent.mkdir(parents=True, exist_ok=True)

    logger.debug(f"Creating/using database at {home_db_path}")
    return home_db_path


# Get the DB path
DB_PATH = get_db_path()
DB_DIR = DB_PATH.parent

TABLE_SCHEMAS = {
    "agent": """
        CREATE TABLE IF NOT EXISTS agent (
            "Agent Name" TEXT PRIMARY KEY,
            "Model" TEXT,
            "Status" TEXT,
            "Current Task" TEXT,
            "Timestamp" DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """,
    "mission": """
        CREATE TABLE IF NOT EXISTS mission (
            "Mission ID" TEXT PRIMARY KEY,
            "Status" TEXT,
            "Objective" TEXT,
            "Assigned Agents" TEXT, -- Storing as comma-separated text for simplicity
            "Timestamp" DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """,
    "telemetry": """
        CREATE TABLE IF NOT EXISTS telemetry (
            "Agent Name" TEXT PRIMARY KEY,
            "Location" TEXT,      -- e.g., "lat, lon, alt"
            "Destination" TEXT,   -- e.g., "lat, lon, alt"
            "Altitude" REAL,
            "Pitch" REAL,
            "Yaw" REAL,
            "Roll" REAL,
            "Airspeed/Velocity" REAL,
            "Acceleration" REAL,
            "Angular Velocity" REAL,
            "Timestamp" DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """,
    "system": """
        CREATE TABLE IF NOT EXISTS system (
            "Component" TEXT PRIMARY KEY,
            "Status" TEXT,
            "Metric" TEXT, -- Using TEXT for flexibility (e.g., "55%", "OK")
            "Timestamp" DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """,
}


def initialize_database():
    """
    Check if the database and tables exist, create them if they don't.
    Only performs actions in the main Werkzeug process.
    """
    # Prevent execution in the reloader process
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        logger.debug(
            f"Process ID {os.getpid()}: Skipping database initialization in reloader process."
        )
        return

    logger.debug(f"Process ID {os.getpid()}: Running database initialization check.")
    conn = None  # Ensure conn is defined for finally block
    try:
        # Ensure the data directory exists
        DB_DIR.mkdir(parents=True, exist_ok=True)

        logger.debug(f"Checking database at: {DB_PATH}")  # Downgraded from INFO
        # Connect to the database (creates the file if it doesn't exist)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Create each table if it doesn't exist
        for table, schema in TABLE_SCHEMAS.items():
            logger.debug(f"Ensuring table '{table}' exists...")
            cursor.execute(schema)

        conn.commit()
        logger.info("Database initialized successfully.")  # Simplified message

    except sqlite3.Error as e:
        logger.error(f"Database error during initialization: {e}", exc_info=True)
    except Exception as e:
        logger.error(
            f"Unexpected error during database initialization: {e}", exc_info=True
        )
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed.")
