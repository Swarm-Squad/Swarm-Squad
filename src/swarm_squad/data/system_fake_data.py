import random
import sqlite3
import time

import pandas as pd

# Define the columns for the Mission Details table
mission_columns = ["Agent Name", "Status", "Mission", "Completion", "Duration"]

# Define the columns for the System Health and Alert table
system_health_columns = [
    "Agent Name",
    "Battery Level",
    "GPS Accuracy",
    "Connection Strength/Quality",
    "Communication Status",
]

while True:
    # Generate fake data for each column
    agent_name = [str(i) for i in range(1, 11)]

    # Generate fake data for System Health and Alert
    battery_level = [
        random.randint(0, 100) for _ in range(10)
    ]  # Battery Level in percentage
    gps_accuracy = [
        random.randint(0, 100) for _ in range(10)
    ]  # GPS Accuracy in percentage
    connection_strength = [
        random.randint(-100, 0) for _ in range(10)
    ]  # Connection Strength/Quality in dBm
    communication_status = random.choices(["Stable", "Unstable", "Lost"], k=10)

    # Create a dataframe for System Health and Alert
    system_health_df = pd.DataFrame(
        list(
            zip(
                agent_name,
                battery_level,
                gps_accuracy,
                connection_strength,
                communication_status,
            )
        ),
        columns=system_health_columns,
    )

    # Create a connection to the SQLite database
    # If the database does not exist, it will be created
    conn = sqlite3.connect("./src/swarm_squad/data/swarm_squad.db")

    # Write the data to a table in the database
    system_health_df.to_sql("system", conn, if_exists="replace", index=False)

    # Print confirmation message
    print("System table updated in the database.")

    # Close the connection to the database
    conn.close()

    # Pause for half second before the next update
    time.sleep(0.5)
