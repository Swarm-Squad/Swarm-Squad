import sqlite3

from swarm_squad.utils.logger import get_logger

# Create module logger
logger = get_logger("db_writer")


def agent_tbl_writer(df):
    # Write the data to the SQLite database
    conn = sqlite3.connect("./src/swarm_squad/data/swarm_squad.db")
    df.to_sql("agent", conn, if_exists="replace", index=False)
    conn.close()

    logger.info("Updated the agent table in the database")


def mission_tbl_writer(df):
    # Write the data to the SQLite database
    conn = sqlite3.connect("./src/swarm_squad/data/swarm_squad.db")
    df.to_sql("mission", conn, if_exists="replace", index=False)
    conn.close()

    logger.info("Updated the mission table in the database")


def system_tbl_writer(df):
    # Write the data to the SQLite database
    conn = sqlite3.connect("./src/swarm_squad/data/swarm_squad.db")
    df.to_sql("system", conn, if_exists="replace", index=False)
    conn.close()

    logger.info("Updated the system table in the database")


def telemetry_tbl_writer(df):
    # Write the data to the SQLite database
    conn = sqlite3.connect("./src/swarm_squad/data/swarm_squad.db")
    df.to_sql("telemetry", conn, if_exists="replace", index=False)
    conn.close()

    logger.info("Updated the telemetry table in the database")
