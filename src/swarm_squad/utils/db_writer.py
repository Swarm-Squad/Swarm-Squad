import sqlite3


def agent_tbl_writer(df):
    # Write the data to the SQLite database
    conn = sqlite3.connect("./src/swarm_squad/data/swarm_squad.db")
    df.to_sql("agent", conn, if_exists="replace", index=False)
    conn.close()

    print("Updated the agent table in the database")


def mission_tbl_writer(df):
    # Write the data to the SQLite database
    conn = sqlite3.connect("./src/swarm_squad/data/swarm_squad.db")
    df.to_sql("mission", conn, if_exists="replace", index=False)
    conn.close()

    print("Updated the mission table in the database")


def system_tbl_writer(df):
    # Write the data to the SQLite database
    conn = sqlite3.connect("./src/swarm_squad/data/swarm_squad.db")
    df.to_sql("system", conn, if_exists="replace", index=False)
    conn.close()

    print("Updated the system table in the database")


def telemetry_tbl_writer(df):
    # Write the data to the SQLite database
    conn = sqlite3.connect("./src/swarm_squad/data/swarm_squad.db")
    df.to_sql("telemetry", conn, if_exists="replace", index=False)
    conn.close()

    print("Updated the telemetry table in the database")
