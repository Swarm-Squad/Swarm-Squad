import matplotlib
import numpy as np

try:
    matplotlib.use("Qt5Agg")  # Try Qt5Agg first
except ImportError:
    try:
        matplotlib.use("TkAgg")  # Try TkAgg second
    except ImportError:
        matplotlib.use("Agg")  # Fall back to Agg if others fail
import time

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.widgets import Button

from swarm_squad.utils.db_writer import telemetry_tbl_writer
from swarm_squad.utils.websocket_writer import ws_writer


class CoordinateConverter:
    def __init__(self):
        # Reference coordinates (center of the area)
        self.ref_lat = 29.189  # center latitude
        self.ref_lon = -81.050  # center longitude

        # Define the simulation bounds
        self.sim_x_min, self.sim_x_max = -40, 25
        self.sim_y_min, self.sim_y_max = -25, 75

        # Calculate the conversion factors
        self.lon_span = -81.048 - (-81.052)  # 0.004 degrees
        self.lat_span = 29.191 - 29.187  # 0.004 degrees

        self.x_span = self.sim_x_max - self.sim_x_min  # 65 units
        self.y_span = self.sim_y_max - self.sim_y_min  # 100 units

    def sim_to_geo(self, x, y):
        """Convert simulation coordinates to geographic coordinates"""
        # Normalize the position to 0-1 range
        x_norm = (x - self.sim_x_min) / self.x_span
        y_norm = (y - self.sim_y_min) / self.y_span

        # Convert to lat/lon
        lon = -81.052 + (x_norm * self.lon_span)
        lat = 29.187 + (y_norm * self.lat_span)

        return lat, lon


def calculate_distance(agent_i, agent_j):
    """
    Calculate the distance between two agents

    Parameters:
        agent_i (list): The position of agent i
        agent_j (list): The position of agent j

    Returns:
        float: The distance between agent i and agent j
    """
    return np.sqrt((agent_i[0] - agent_j[0]) ** 2 + (agent_i[1] - agent_j[1]) ** 2)


def calculate_aij(alpha, delta, rij, r0, v):
    """
    Calculate the aij value

    Parameters:
        alpha (float): System parameter about antenna characteristics
        delta (float): The required application data rate
        rij (float): The distance between two agents
        r0 (float): Reference distance value
        v (float): Path loss exponent

    Returns:
        float: The calculated aij (communication quality in antenna far-field) value
    """
    return np.exp(-alpha * (2**delta - 1) * (rij / r0) ** v)


def calculate_gij(rij, r0):
    """
    Calculate the gij value

    Parameters:
        rij (float): The distance between two agents
        r0 (float): Reference distance value

    Returns:
        float: The calculated gij (communication quality in antenna near-field) value
    """
    return rij / np.sqrt(rij**2 + r0**2)


def calculate_rho_ij(beta, v, rij, r0):
    """
    Calculate the rho_ij (the derivative of phi_ij) value

    Parameters:
        beta (float): alpha * (2**delta - 1)
        v (float): Path loss exponent
        rij (float): The distance between two agents
        r0 (float): Reference distance value

    Returns:
        float: The calculated rho_ij value
    """
    return (
        (-beta * v * rij ** (v + 2) - beta * v * (r0**2) * (rij**v) + r0 ** (v + 2))
        * np.exp(-beta * (rij / r0) ** v)
        / np.sqrt((rij**2 + r0**2) ** 3)
    )


def calculate_Jn(communication_qualities_matrix, neighbor_agent_matrix, PT):
    """
    Calculate the Jn (average communication performance indicator) value

    Parameters:
        communication_qualities_matrix (numpy.ndarray): The communication qualities matrix among agents
        neighbor_agent_matrix (numpy.ndarray): The neighbor_agent matrix which is adjacency matrix of aij value
        PT (float): The reception probability threshold

    Returns:
        float: The calculated Jn value
    """
    total_communication_quality = 0
    total_neighbors = 0
    swarm_size = communication_qualities_matrix.shape[0]
    for i in range(swarm_size):
        for j in [x for x in range(swarm_size) if x != i]:
            if neighbor_agent_matrix[i, j] > PT:
                total_communication_quality += communication_qualities_matrix[i, j]
                total_neighbors += 1
    return total_communication_quality / total_neighbors


def calculate_rn(distances_matrix, neighbor_agent_matrix, PT):
    """
    Calculate the rn (average neighboring distance performance indicator) value

    Parameters:
        distances_matrix (numpy.ndarray): The distances matrix among agents
        neighbor_agent_matrix (numpy.ndarray): The neighbor_agent matrix which is adjacency matrix of aij value
        PT (float): The reception probability threshold

    Returns:
        float: The calculated rn value
    """
    total_distance = 0
    total_neighbors = 0
    swarm_size = distances_matrix.shape[0]
    for i in range(swarm_size):
        for j in [x for x in range(swarm_size) if x != i]:
            if neighbor_agent_matrix[i, j] > PT:
                total_distance += distances_matrix[i, j]
                total_neighbors += 1
    return total_distance / total_neighbors


def find_closest_agent(swarm_position, swarm_centroid):
    """
    Find the index of the agent with the minimum distance to the destination

    Parameters:
        swarm_position (numpy.ndarray): The positions of the swarm
        swarm_centroid (numpy.ndarray): The centroid of the swarm

    Returns:
        int: The index of the agent with the minimum distance to the destination
    """
    # Calculate the Euclidean distance from each agent to the destination
    distances_matrix = np.sqrt(np.sum((swarm_position - swarm_centroid) ** 2, axis=1))

    # Find the index of the agent with the minimum distance
    closest_agent_index = np.argmin(distances_matrix)

    return closest_agent_index


def plot_figures_task1(
    axs,
    t_elapsed,
    Jn,
    rn,
    swarm_position,
    PT,
    communication_qualities_matrix,
    swarm_size,
    swarm_paths,
    node_colors,
    line_colors,
    converter,
):
    """
    Plot 4 figures (Formation Scene, Swarm Trajectories, Jn Performance, rn Performance)

    Parameters:
        axs (numpy.ndarray): The axes of the figure
        t_elapsed (list): The elapsed time
        Jn (list): The Jn values
        rn (list): The rn values
        swarm_position (numpy.ndarray): The positions of the swarm
        PT (float): The reception probability threshold
        communication_qualities_matrix (numpy.ndarray): The communication qualities matrix among agents
        swarm_size (int): The number of agents in the swarm
        swarm_paths (list): The paths of the swarm
        node_colors (list): The colors of the nodes
        line_colors (list): The colors of the lines
        converter (CoordinateConverter): The coordinate converter

    Returns:
        None
    """
    for ax in axs.flatten():
        ax.clear()

    ########################
    # Plot formation scene #
    ########################
    axs[0, 0].set_title("Formation Scene")
    axs[0, 0].set_xlabel("Longitude")
    axs[0, 0].set_ylabel("Latitude")

    # Convert and plot the nodes
    for i in range(swarm_position.shape[0]):
        lat, lon = converter.sim_to_geo(swarm_position[i, 0], swarm_position[i, 1])
        axs[0, 0].scatter(lon, lat, color=node_colors[i])

    # Plot the edges
    for i in range(swarm_position.shape[0]):
        for j in range(i + 1, swarm_position.shape[0]):
            if communication_qualities_matrix[i, j] > PT:
                lat1, lon1 = converter.sim_to_geo(
                    swarm_position[i, 0], swarm_position[i, 1]
                )
                lat2, lon2 = converter.sim_to_geo(
                    swarm_position[j, 0], swarm_position[j, 1]
                )
                axs[0, 0].plot(
                    [lon1, lon2], [lat1, lat2], color=line_colors[i, j], linestyle="--"
                )

    # Adjust the plot limits to center around -81.05, 29.19
    # Using a span of 0.004 degrees for both lat and lon
    lon_center = -81.0475
    lat_center = 29.1880
    span = 0.003  # Half of 0.004 to create the full range

    axs[0, 0].set_xlim(lon_center - span, lon_center + span)  # -81.052 to -81.048
    axs[0, 0].set_ylim(lat_center - span, lat_center + span)  # 29.188 to 29.192

    ###########################
    # Plot swarm trajectories #
    ###########################
    axs[0, 1].set_title("Swarm Trajectories")
    axs[0, 1].set_xlabel("Longitude")
    axs[0, 1].set_ylabel("Latitude")

    # Store the current swarm positions
    swarm_paths.append(swarm_position.copy())

    # Convert the list of positions to a numpy array
    trajectory_array = np.array(swarm_paths)

    # Plot the trajectories
    for i in range(swarm_position.shape[0]):
        # Convert trajectory points
        lats, lons = zip(
            *[converter.sim_to_geo(pos[0], pos[1]) for pos in trajectory_array[:, i]]
        )

        axs[0, 1].plot(lons, lats, color=node_colors[i])

        # Calculate and plot arrows (if needed)
        if len(trajectory_array) > swarm_size:
            for j in range(0, len(lons) - 1, swarm_size):
                dx = lons[j + 1] - lons[j]
                dy = lats[j + 1] - lats[j]
                if dx != 0 or dy != 0:
                    norm = np.sqrt(dx**2 + dy**2)
                    dx, dy = dx / norm, dy / norm
                    scale_factor = 0.0001  # Adjust this value as needed
                    axs[0, 1].quiver(
                        lons[j],
                        lats[j],
                        dx * scale_factor,
                        dy * scale_factor,
                        color=node_colors[i],
                        scale_units="xy",
                        angles="xy",
                        scale=1,
                        headlength=10,
                        headaxislength=9,
                        headwidth=8,
                    )

    # Use the same limits for the trajectory plot
    axs[0, 1].set_xlim(lon_center - span, lon_center + span)
    axs[0, 1].set_ylim(lat_center - span, lat_center + span)

    # Add margins and ensure equal aspect ratio
    for ax in [axs[0, 0], axs[0, 1]]:
        ax.margins(0.1)
        ax.set_aspect("equal")
        ax.grid(True, linestyle="--", alpha=0.6)

    #######################
    # Plot Jn performance #
    #######################
    axs[1, 0].set_title("Average Communication Performance Indicator")
    axs[1, 0].plot(t_elapsed, Jn)
    axs[1, 0].set_xlabel("$t(s)$")
    axs[1, 0].set_ylabel("$J_n$", rotation=0, labelpad=20)
    axs[1, 0].text(
        t_elapsed[-1], Jn[-1], "Jn={:.4f}".format(Jn[-1]), ha="right", va="top"
    )

    #######################
    # Plot rn performance #
    #######################
    axs[1, 1].set_title("Average Distance Performance Indicator")
    axs[1, 1].plot(t_elapsed, rn)
    axs[1, 1].set_xlabel("$t(s)$")
    axs[1, 1].set_ylabel("$r_n$", rotation=0, labelpad=20)
    axs[1, 1].text(
        t_elapsed[-1], rn[-1], "$r_n$={:.4f}".format(rn[-1]), ha="right", va="top"
    )

    plt.tight_layout()
    plt.draw()
    plt.pause(0.01)


def plot_figures_task2(
    axs,
    t_elapsed,
    Jn,
    rn,
    swarm_position,
    swarm_destination,
    PT,
    communication_qualities_matrix,
    swarm_size,
    swarm_paths,
    node_colors,
    line_colors,
    converter,
):
    """
    Plot 4 figures (Formation Scene, Swarm Trajectories, Jn Performance, rn Performance)

    Parameters:
        axs (numpy.ndarray): The axes of the figure
        t_elapsed (list): The elapsed time
        Jn (list): The Jn values
        rn (list): The rn values
        swarm_position (numpy.ndarray): The positions of the swarm
        swarm_destination (list): The destination of the swarm
        PT (float): The reception probability threshold
        communication_qualities_matrix (numpy.ndarray): The communication qualities matrix among agents
        swarm_size (int): The number of agents in the swarm
        swarm_paths (list): The paths of the swarm
        node_colors (list): The colors of the nodes
        line_colors (list): The colors of the lines
        converter (CoordinateConverter): The coordinate converter

    Returns:
        None
    """
    for ax in axs.flatten():
        ax.clear()

    ########################
    # Plot formation scene #
    ########################
    axs[0, 0].set_title("Formation Scene")
    axs[0, 0].set_xlabel("Longitude")
    axs[0, 0].set_ylabel("Latitude")

    # Convert and plot the nodes
    for i in range(swarm_position.shape[0]):
        lat, lon = converter.sim_to_geo(swarm_position[i, 0], swarm_position[i, 1])
        axs[0, 0].scatter(lon, lat, color=node_colors[i])

    # Plot the destination
    axs[0, 0].plot(
        *converter.sim_to_geo(swarm_destination[0], swarm_destination[1]),
        marker="s",
        markersize=10,
        color="none",
        mec="black",
    )
    axs[0, 0].text(
        converter.sim_to_geo(swarm_destination[0], swarm_destination[1])[1],
        converter.sim_to_geo(swarm_destination[0], swarm_destination[1])[0] + 3,
        "Destination",
        ha="center",
        va="bottom",
    )

    # Plot the edges
    for i in range(swarm_position.shape[0]):
        for j in range(i + 1, swarm_position.shape[0]):
            if communication_qualities_matrix[i, j] > PT:
                lat1, lon1 = converter.sim_to_geo(
                    swarm_position[i, 0], swarm_position[i, 1]
                )
                lat2, lon2 = converter.sim_to_geo(
                    swarm_position[j, 0], swarm_position[j, 1]
                )
                axs[0, 0].plot(
                    [lon1, lon2], [lat1, lat2], color=line_colors[i, j], linestyle="--"
                )

    axs[0, 0].set_xlim(-81.052, -81.048)
    axs[0, 0].set_ylim(29.187, 29.191)

    ###########################
    # Plot swarm trajectories #
    ###########################
    axs[0, 1].set_title("Swarm Trajectories")
    axs[0, 1].set_xlabel("Longitude")
    axs[0, 1].set_ylabel("Latitude")

    # Store the current swarm positions
    swarm_paths.append(swarm_position.copy())

    # Convert the list of positions to a numpy array
    trajectory_array = np.array(swarm_paths)

    # Plot the trajectories
    for i in range(swarm_position.shape[0]):
        # Convert trajectory points
        lats, lons = zip(
            *[converter.sim_to_geo(pos[0], pos[1]) for pos in trajectory_array[:, i]]
        )

        axs[0, 1].plot(lons, lats, color=node_colors[i])

        # Calculate and plot arrows (if needed)
        if len(trajectory_array) > swarm_size:
            for j in range(0, len(lons) - 1, swarm_size):
                dx = lons[j + 1] - lons[j]
                dy = lats[j + 1] - lats[j]
                if dx != 0 or dy != 0:
                    norm = np.sqrt(dx**2 + dy**2)
                    dx, dy = dx / norm, dy / norm
                    scale_factor = 0.0001  # Adjust this value as needed
                    axs[0, 1].quiver(
                        lons[j],
                        lats[j],
                        dx * scale_factor,
                        dy * scale_factor,
                        color=node_colors[i],
                        scale_units="xy",
                        angles="xy",
                        scale=1,
                        headlength=10,
                        headaxislength=9,
                        headwidth=8,
                    )

    axs[0, 1].set_xlim(-81.052, -81.048)
    axs[0, 1].set_ylim(29.187, 29.191)

    # Plot the destination
    axs[0, 1].plot(
        *converter.sim_to_geo(swarm_destination[0], swarm_destination[1]),
        marker="s",
        markersize=10,
        color="none",
        mec="black",
    )
    axs[0, 1].text(
        converter.sim_to_geo(swarm_destination[0], swarm_destination[1])[1],
        converter.sim_to_geo(swarm_destination[0], swarm_destination[1])[0] + 3,
        "Destination",
        ha="center",
        va="bottom",
    )

    #######################
    # Plot Jn performance #
    #######################
    axs[1, 0].set_title("Average Communication Performance Indicator")
    axs[1, 0].plot(t_elapsed, Jn)
    axs[1, 0].set_xlabel("$t(s)$")
    axs[1, 0].set_ylabel("$J_n$", rotation=0, labelpad=20)
    axs[1, 0].text(
        t_elapsed[-1], Jn[-1], "Jn={:.4f}".format(Jn[-1]), ha="right", va="top"
    )

    #######################
    # Plot rn performance #
    #######################
    axs[1, 1].set_title("Average Distance Performance Indicator")
    axs[1, 1].plot(t_elapsed, rn)
    axs[1, 1].set_xlabel("$t(s)$")
    axs[1, 1].set_ylabel("$r_n$", rotation=0, labelpad=20)
    axs[1, 1].text(
        t_elapsed[-1], rn[-1], "$r_n$={:.4f}".format(rn[-1]), ha="right", va="top"
    )

    plt.tight_layout()
    plt.draw()
    plt.pause(0.01)


# ---------------------------#
# Initialize all parameters #
# ---------------------------#
max_iter = 500  # Maximum number of iterations
alpha = 10 ** (-5)  # Initialize system parameter about antenna characteristics
delta = 2  # Initialize required application data rate
beta = alpha * (2**delta - 1)
v = 3  # Initialize path loss exponent
r0 = 5  # Initialize reference distance
PT = 0.94  # Initialize the threshold value for communication quality


# Initialize agents' positions
swarm_position = np.array(
    [[-5, 14], [-5, -19], [0, 0], [35, -4], [68, 0], [72, 13], [72, -18]], dtype=float
)

# Initialize the swarm destination
swarm_destination = np.array([35, 100], dtype=float)

# Initialize the swarm size
swarm_size = swarm_position.shape[0]

# Initialize the swarm control
swarm_control_ui = np.zeros((swarm_size, 2))

# Initialize performance indicators
Jn = []
rn = []

# Initialize timer
start_time = time.time()
t_elapsed = []

# Initialize the communication qualities matrix to record the communication qualities between agents
communication_qualities_matrix = np.zeros((swarm_size, swarm_size))

# Initialize the distances matrix to record the distances between agents
distances_matrix = np.zeros((swarm_size, swarm_size))

# Initialize the matrix to record the aij (near-field communication quality) value to indicate neighboring agents
neighbor_agent_matrix = np.zeros((swarm_size, swarm_size))

# Initialize the list for swarm trajectory plot
swarm_paths = []

# Assign node (aka agent) color
node_colors = [
    [108 / 255, 155 / 255, 207 / 255],  # Light Blue
    [247 / 255, 147 / 255, 39 / 255],  # Orange
    [242 / 255, 102 / 255, 171 / 255],  # Light Pink
    [255 / 255, 217 / 255, 90 / 255],  # Light Gold
    [122 / 255, 168 / 255, 116 / 255],  # Green
    [147 / 255, 132 / 255, 209 / 255],  # Purple
    [245 / 255, 80 / 255, 80 / 255],  # Red
]

# Assign edge (aka communication links between agents) color
line_colors = np.random.rand(swarm_position.shape[0], swarm_position.shape[0], 3)

# Initialize a flag for Jn convergence
Jn_converged = False

# Initialize the figure
fig, axs = plt.subplots(2, 2, figsize=(10, 10))

# In your main code, create the converter
converter = CoordinateConverter()

# Create the position of the buttons
ax_reset = plt.axes([0.9, 0.60, 0.07, 0.05])
ax_pause = plt.axes([0.9, 0.50, 0.07, 0.05])
ax_continue = plt.axes([0.9, 0.40, 0.07, 0.05])
ax_stop = plt.axes([0.9, 0.30, 0.07, 0.05])

# Create the buttons with hexadecimal color codes
reset_button = Button(ax_reset, "Reset", color="#e3f0d8")  # Green
pause_button = Button(ax_pause, "Pause", color="#fdf2ca")  # Yellow
continue_button = Button(ax_continue, "Continue", color="#d8e3f0")  # Blue
stop_button = Button(ax_stop, "Stop", color="#f9aeae")  # Red

# Create a global variable to control the simulation
running = True


# Define button callback functions
def reset(event):
    global swarm_position, running, Jn, rn, t_elapsed, swarm_paths
    # Reset to initial positions
    swarm_position = np.array(
        [[-5, 14], [-5, -19], [0, 0], [35, -4], [68, 0], [72, 13], [72, -18]],
        dtype=float,
    )
    # Reset other variables
    running = True
    Jn = []
    rn = []
    t_elapsed = []
    swarm_paths = []
    # Reset start time
    global start_time
    start_time = time.time()


def pause(event):
    global running
    running = False


def continues(event):
    global running
    running = True


def stop(event):
    global running
    running = False
    plt.close()


# Assign the functions to the buttons
reset_button.on_clicked(reset)
pause_button.on_clicked(pause)
continue_button.on_clicked(continues)
stop_button.on_clicked(stop)

# ----------------------#
# Formation Controller #
# ----------------------#
for iter in range(max_iter):
    if not running:
        plt.pause(0.1)  # Add small pause to prevent CPU overload
        continue

    print("Iteration: ", iter)

    # Calculate control inputs and update positions as before
    for i in range(swarm_size):
        for j in [x for x in range(swarm_size) if x != i]:
            rij = calculate_distance(swarm_position[i], swarm_position[j])
            aij = calculate_aij(alpha, delta, rij, r0, v)
            gij = calculate_gij(rij, r0)
            if aij >= PT:
                # rho_ij is the derivative of upper case phi_ij (which is the same as the lower case phi_ij in powerpoint)
                rho_ij = calculate_rho_ij(beta, v, rij, r0)
            else:
                rho_ij = 0

            qi = swarm_position[i, :]
            qj = swarm_position[j, :]
            eij = (qi - qj) / np.sqrt(rij)

            ###########################
            # Formation control input #
            ###########################
            swarm_control_ui[i, 0] += rho_ij * eij[0]
            swarm_control_ui[i, 1] += rho_ij * eij[1]

            # Record the communication qualities, distances, and neighbor_agent matrices for Jn and rn performance plots
            phi_rij = gij * aij
            communication_qualities_matrix[i, j] = phi_rij
            communication_qualities_matrix[j, i] = phi_rij

            distances_matrix[i, j] = rij
            distances_matrix[j, i] = rij

            neighbor_agent_matrix[i, j] = aij
            neighbor_agent_matrix[j, i] = aij

        swarm_position[i, 0] += swarm_control_ui[i, 0]
        swarm_position[i, 1] += swarm_control_ui[i, 1]
        swarm_control_ui[i, 0] = 0
        swarm_control_ui[i, 1] = 0

        Jn_new = calculate_Jn(communication_qualities_matrix, neighbor_agent_matrix, PT)
        rn_new = calculate_rn(distances_matrix, neighbor_agent_matrix, PT)

    # Record the performance indicators
    Jn.append(round(Jn_new, 4))
    rn.append(round(rn_new, 4))

    # Check if the last 20 values in Jn are the same, if so, the formation is completed, and the swarm starts to reach the destination
    if len(Jn) > 19 and len(set(Jn[-20:])) == 1:
        if not Jn_converged:
            print(
                f"Formation completed: Jn values has converged in {round(t_elapsed[-1], 2)} seconds {iter - 20} iterations."
            )
            Jn_converged = True
            break

    # Record the elapsed time
    t_elapsed.append(time.time() - start_time)

    # Starts plotting
    plot_figures_task1(
        axs,
        t_elapsed,
        Jn,
        rn,
        swarm_position,
        PT,
        communication_qualities_matrix,
        swarm_size,
        swarm_paths,
        node_colors,
        line_colors,
        converter,
    )

    # Create DataFrame for current iteration
    data = {
        "Agent Name": range(1, swarm_size + 1),
        "Location": [
            f"{lon}, {lat}, 50"  # Swapped order: lon, lat, alt
            for lat, lon in [
                converter.sim_to_geo(pos[0], pos[1]) for pos in swarm_position
            ]
        ],
        "Destination": [
            f"{lon}, {lat}, 50"  # Swapped order: lon, lat, alt
            for lat, lon in [
                converter.sim_to_geo(swarm_destination[0], swarm_destination[1])
            ]
            * swarm_size
        ],
        "Altitude": [50 for _ in range(swarm_size)],
        "Pitch": [45 for _ in range(swarm_size)],
        "Yaw": [0 for _ in range(swarm_size)],
        "Roll": [0 for _ in range(swarm_size)],
        "Airspeed/Velocity": [
            np.linalg.norm(swarm_control_ui[i]) for i in range(swarm_size)
        ],
        "Acceleration": [0 for _ in range(swarm_size)],
        "Angular Velocity": [0 for _ in range(swarm_size)],
    }

    # Create DataFrame and write to database
    telemetry_df = pd.DataFrame(data)
    telemetry_tbl_writer(telemetry_df)
    ws_writer(data)

    # Check if figure is closed
    if not plt.fignum_exists(fig.number):
        break

    # Add plt.pause to allow GUI updates
    plt.pause(0.01)

plt.show()
