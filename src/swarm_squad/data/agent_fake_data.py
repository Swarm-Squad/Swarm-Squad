import random
import sqlite3
import time

import pandas as pd

# Define the columns for the Agent List table
agent_columns = ["Agent Name", "Agent Type", "Status", "Mode", "Alert Count"]

counter = 10

while True:
    # Generate fake data for each column
    agent_name = list(range(1, counter + 1))
    k = len(agent_name)
    agent_type = random.choices(["quadcopter", "fixed-wing", "vehicle", "robots"], k=k)
    status = random.choices(["Connected", "Disconnected"], k=k)
    mode = random.choices(["Manual", "Autonomous"], k=k)
    error_count = random.choices(range(1, 10), k=k)

    # Create a dataframe
    agent_df = pd.DataFrame(
        list(zip(agent_name, agent_type, status, mode, error_count)),
        columns=agent_columns,
    )

    # Create a connection to the SQLite database
    # If the database does not exist, it will be created
    conn = sqlite3.connect("./src/swarm_squad/data/swarm_squad.db")

    # Write the data to a table in the database
    agent_df.to_sql("agent", conn, if_exists="replace", index=False)

    # Print confirmation message
    print("Agent table updated in the database.")

    # Close the connection to the database
    conn.close()

    # counter += 1

    # Pause for half second before the next update
    time.sleep(0.5)
