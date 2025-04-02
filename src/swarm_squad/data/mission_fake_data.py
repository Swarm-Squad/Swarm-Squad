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
    status = random.choices(["In Progress", "Completed", "Pending"], k=10)
    mission = random.choices(
        [
            "Reaching to Destination",
            "Avoiding",
            "Stopped",
            "Idling",
            "Take-off",
            "Land",
        ],
        k=10,
    )
    completion = [random.randint(0, 100) for _ in range(10)]  # Completion in percentage
    duration = [random.randint(0, 3600) for _ in range(10)]  # Duration in seconds

    # Create a dataframe for Mission Details
    mission_df = pd.DataFrame(
        list(zip(agent_name, status, mission, completion, duration)),
        columns=mission_columns,
    )

    # Create a connection to the SQLite database
    # If the database does not exist, it will be created
    conn = sqlite3.connect("./src/swarm_squad/data/swarm_squad.db")

    # Write the data to a table in the database
    mission_df.to_sql("mission", conn, if_exists="replace", index=False)

    # Print confirmation message
    print("Mission table updated in the database.")

    # Close the connection to the database
    conn.close()

    # Pause for half second before the next update
    time.sleep(0.5)
