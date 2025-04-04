"""
Utility to initialize the Swarm Squad SQLite database.
"""

import os
import sqlite3
from pathlib import Path

from swarm_squad.utils.logger import get_logger

logger = get_logger("db_init")

# Define the path to the database file relative to this script's location
# Assuming this file is in utils/, data/ is ../data/
DB_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DB_DIR / "swarm_squad.db"

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
