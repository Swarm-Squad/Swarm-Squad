# Data Management Guide

This guide explains how to interact with the Swarm-Squad database and WebSocket system.

## Database Structure

The system uses SQLite with four main tables:

### 1. Agent Table
```
agent_columns = [
    "Agent Name",     # int: Unique identifier (1, 2, 3, ...)
    "Agent Type",     # str: "quadcopter", "fixed-wing", "vehicle", "robots"
    "Status",         # str: "Connected", "Disconnected"
    "Mode",           # str: "Manual", "Autonomous"
    "Alert Count"     # int: Number of alerts (1-10)
]
```

### 2. Mission Table
```
mission_columns = [
    "Agent Name",     # int: Unique identifier (1, 2, 3, ...)
    "Status",         # str: "In Progress", "Completed", "Pending"
    "Mission",        # str: "Reaching to Destination", "Avoiding", "Stopped", "Idling", "Take-off", "Land"
    "Completion",     # int: Percentage (0-100)
    "Duration"        # int: Seconds
]
```

### 3. System Table
```
system_health_columns = [
    "Agent Name",                 # int: Unique identifier (1, 2, 3, ...)
    "Battery Level",             # int: Percentage (0-100)
    "GPS Accuracy",              # int: Percentage (0-100)
    "Connection Strength/Quality",# int: dBm (-100 to 0)
    "Communication Status"       # str: "Stable", "Unstable", "Lost"
]
```

### 4. Telemetry Table
```
telemetry_columns = [
    "Agent Name",          # int: Unique identifier (1, 2, 3, ...)
    "Location",           # str: "longitude, latitude, altitude" (e.g., "-81.050, 29.189, 50")
    "Destination",        # str: "longitude, latitude, altitude"
    "Altitude",           # float: Meters
    "Pitch",             # float: Degrees
    "Yaw",               # float: Degrees
    "Roll",              # float: Degrees
    "Airspeed/Velocity", # float: km/h
    "Acceleration",      # float: m/s²
    "Angular Velocity"   # float: rad/s
]
```

## Writing Data

### Method 1: Using Database Writers
```python
from utils.db_writer import agent_tbl_writer, mission_tbl_writer, system_tbl_writer, telemetry_tbl_writer
import pandas as pd

# Create a DataFrame with your data
data = {
    "Agent Name": [1, 2, 3],
    "Location": ["-81.050, 29.189, 50", "-81.051, 29.188, 51", "-81.049, 29.187, 52"],
    # ... add other required columns
}
df = pd.DataFrame(data)

# Write to specific table
telemetry_tbl_writer(df)  # For telemetry data
agent_tbl_writer(df)      # For agent data
mission_tbl_writer(df)    # For mission data
system_tbl_writer(df)     # For system data
```

### Method 2: Using WebSocket Writer
```python
from utils.websocket_writer import ws_writer

# Prepare your data dictionary
data = {
    "Agent Name": [1, 2, 3],
    "Location": ["-81.050, 29.189, 50", "-81.051, 29.188, 51", "-81.049, 29.187, 52"],
    "Pitch": [45, 45, 45],
    "Yaw": [0, 0, 0],
    "Roll": [0, 0, 0]
}

# Send data through WebSocket
ws_writer(data)
```

## Example Usage

Here's a complete example of updating both database and WebSocket:

```python
import pandas as pd
from utils.db_writer import telemetry_tbl_writer
from utils.websocket_writer import ws_writer

# Prepare data
data = {
    "Agent Name": [1, 2, 3],
    "Location": ["-81.050, 29.189, 50", "-81.051, 29.188, 51", "-81.049, 29.187, 52"],
    "Destination": ["-81.048, 29.190, 50", "-81.049, 29.189, 51", "-81.047, 29.188, 52"],
    "Altitude": [50.0, 51.0, 52.0],
    "Pitch": [45.0, 45.0, 45.0],
    "Yaw": [0.0, 0.0, 0.0],
    "Roll": [0.0, 0.0, 0.0],
    "Airspeed/Velocity": [10.0, 11.0, 12.0],
    "Acceleration": [0.0, 0.0, 0.0],
    "Angular Velocity": [0.0, 0.0, 0.0]
}

# Create DataFrame
df = pd.DataFrame(data)

# Update database
telemetry_tbl_writer(df)

# Update WebSocket
ws_writer(data)
```

## Important Notes

1. The WebSocket server automatically starts when you use `ws_writer`
2. Location format must be "longitude, latitude, altitude" (in that order)
3. All numeric values should be within their specified ranges
4. The database is located at `./src/swarm_squad/data/swarm_squad.db`
5. WebSocket updates are broadcast to all connected clients
6. The WebSocket server runs on `localhost:8051`

## Example Scripts

Check these example scripts for implementation details:
- `src/scripts/boids.py`: Flocking simulation
- `src/scripts/formation.py`: Formation control
