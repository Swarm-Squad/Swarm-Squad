import random
import sqlite3
import time

import pandas as pd

# Define the columns for the Telemetry Data table
telemetry_columns = [
    "Agent Name",
    "Location",
    "Destination",
    "Altitude",
    "Pitch",
    "Yaw",
    "Roll",
    "Airspeed/Velocity",
    "Acceleration",
    "Angular Velocity",
]
latitude = [random.uniform(29.187, 29.1940) for _ in range(10)]
longitude = [random.uniform(-81.044, -81.052) for _ in range(10)]
altitude = [round(random.uniform(0, 40), 3) for _ in range(10)]  # Altitude in meters
yaw = [0 for _ in range(10)]
roll = [0 for _ in range(10)]

while True:
    # Generate fake data for each column
    agent_name = range(1, 11)
    latitude = [
        lat + random.uniform(0.00001, 0.0001) for lat in latitude
    ]  # Moving North
    altitude = [
        alt + random.uniform(-0.1, 0.1) for alt in altitude
    ]  # Altitude in meters
    location = [
        f"{longitude[i]:.4f}, {latitude[i]:.4f}, {altitude[i]}" for i in range(10)
    ]
    destination = [
        f"{longitude[i]:.4f}, {latitude[i] + random.uniform(0.0001, 0.001):.4f}, 50"
        for i in range(10)
    ]  # Destination North
    pitch = [90 for _ in range(10)]
    yaw = [y + random.uniform(0, 0.001) for y in yaw]
    roll = [r + random.uniform(0, 0.001) for r in roll]
    airspeed_velocity = [
        round(random.uniform(50, 200), 3) for _ in range(10)
    ]  # Airspeed/Velocity in km/h
    acceleration = [
        round(random.uniform(0, 10), 3) for _ in range(10)
    ]  # Acceleration in m/s^2
    angular_velocity = [
        round(random.uniform(-3.14, 3.14), 3) for _ in range(10)
    ]  # Angular Velocity in rad/s

    # Create a dataframe
    telemetry_df = pd.DataFrame(
        list(
            zip(
                agent_name,
                location,
                destination,
                altitude,
                pitch,
                yaw,
                roll,
                airspeed_velocity,
                acceleration,
                angular_velocity,
            )
        ),
        columns=telemetry_columns,
    )

    # Create a connection to the SQLite database
    # If the database does not exist, it will be created
    conn = sqlite3.connect("./src/swarm_squad/data/swarm_squad.db")

    # Write the data to a table in the database
    telemetry_df.to_sql("telemetry", conn, if_exists="replace", index=False)

    # Print confirmation message
    print("Telemetry table updated in the database.")

    # Close the connection to the database
    conn.close()

    # Pause for half second before the next update
    time.sleep(0.5)
