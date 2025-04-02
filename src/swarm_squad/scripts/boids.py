import matplotlib
import numpy as np

try:
    matplotlib.use("Qt5Agg")  # Try Qt5Agg first
except ImportError:
    try:
        matplotlib.use("TkAgg")  # Try TkAgg second
    except ImportError:
        matplotlib.use("Agg")  # Fall back to Agg if others fail
import random

import matplotlib.pyplot as plt

# Write the data to the SQLite database and websocket
import pandas as pd
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, Slider

from swarm_squad.utils.db_writer import telemetry_tbl_writer
from swarm_squad.utils.websocket_writer import ws_writer


class Boid:
    def __init__(self, position, velocity):
        self.position = position
        self.velocity = velocity


class Flock:
    def __init__(self, num_boids):
        # Initialize in meters (100m x 100m x 45m space)
        self.boids = [
            Boid(np.random.rand(3) * np.array([100, 100, 45]), np.random.rand(3) - 0.5)
            for _ in range(num_boids)
        ]
        # Store reference coordinates for conversion
        self.ref_lat = 29.189  # center latitude
        self.ref_lon = -81.050  # center longitude
        self.min_alt = 30
        self.max_alt = 100

    def meters_to_latlon(self, position):
        # Convert meters to lat/lon/alt
        # Approximate conversion (at equator, 1 degree = 111,111 meters)
        lat_offset = position[1] / 111111
        lon_offset = position[0] / (111111 * np.cos(np.radians(self.ref_lat)))

        lat = self.ref_lat + lat_offset
        lon = self.ref_lon + lon_offset
        alt = self.min_alt + (position[2] / 45) * (self.max_alt - self.min_alt)

        return np.array([lat, lon, alt])

    def update_boids(self, cohesion_weight, separation_weight, alignment_weight):
        colors = []

        for boid in self.boids:
            # Calculate forces from each rule
            v1 = self.rule1(boid) * cohesion_weight
            v2 = self.rule2(boid) * separation_weight
            v3 = self.rule3(boid) * alignment_weight
            v4 = self.enforce_bounds(boid)

            # Calculate magnitudes of each behavior
            cohesion_mag = np.linalg.norm(v1)
            separation_mag = np.linalg.norm(v2)
            alignment_mag = np.linalg.norm(v3)

            # Determine dominant behavior
            max_mag = max(cohesion_mag, separation_mag, alignment_mag)
            if max_mag == cohesion_mag:
                colors.append("#98C379")  # Green for cohesion
            elif max_mag == separation_mag:
                colors.append("#E06C75")  # Red for separation
            else:
                colors.append("#E5C07B")  # Yellow for alignment

            boid.velocity += v1 + v2 + v3 + v4

            # Limit velocity (in meters per second)
            speed = np.linalg.norm(boid.velocity)
            max_speed = 15.0
            min_speed = 5.0

            if speed > max_speed:
                boid.velocity = (boid.velocity / speed) * max_speed
            elif speed < min_speed:
                boid.velocity = (boid.velocity / speed) * min_speed

            boid.position += boid.velocity * 0.5

        # Create database entries with converted coordinates
        data = {
            "Agent Name": range(1, len(self.boids) + 1),
            "Location": [
                f"{pos[1]}, {pos[0]}, {pos[2]}"
                for pos in [self.meters_to_latlon(boid.position) for boid in self.boids]
            ],
            "Destination": [
                f"{pos[0]}, {pos[1] + random.uniform(0.0001, 0.001)}, 50"
                for pos in [self.meters_to_latlon(boid.position) for boid in self.boids]
            ],
            "Altitude": [
                self.meters_to_latlon(boid.position)[2] for boid in self.boids
            ],
            "Pitch": [45 for _ in self.boids],
            "Yaw": [0 for _ in self.boids],
            "Roll": [0 for _ in self.boids],
            "Airspeed/Velocity": [np.linalg.norm(boid.velocity) for boid in self.boids],
            "Acceleration": [0 for _ in self.boids],
            "Angular Velocity": [0 for _ in self.boids],
        }
        telemetry_df = pd.DataFrame(data)
        telemetry_tbl_writer(telemetry_df)
        ws_writer(data)

        return colors

    def rule1(self, boid):
        # Cohesion - steer towards center of mass of neighbors
        neighbors = [
            other_boid
            for other_boid in self.boids
            if other_boid != boid
            and np.linalg.norm(other_boid.position - boid.position) < 20
        ]
        if neighbors:
            center = np.mean([n.position for n in neighbors], axis=0)
            return (center - boid.position) * 0.05  # Increased from 0.01 to 0.05
        return np.zeros(3)

    def rule2(self, boid):
        # Separation - avoid crowding neighbors
        separation = np.zeros(3)
        for other in self.boids:
            if other != boid:
                diff = boid.position - other.position
                dist = np.linalg.norm(diff)
                if dist < 10:  # 10m minimum separation
                    separation += diff / (dist * dist)
        return separation * 0.05  # Increased from 0.01 to 0.05

    def rule3(self, boid):
        # Alignment - steer towards average heading of neighbors
        neighbors = [
            other_boid
            for other_boid in self.boids
            if other_boid != boid
            and np.linalg.norm(other_boid.position - boid.position) < 15
        ]
        if neighbors:
            avg_vel = np.mean([n.velocity for n in neighbors], axis=0)
            return (avg_vel - boid.velocity) * 0.25  # Increased from 0.125 to 0.25
        return np.zeros(3)

    def enforce_bounds(self, boid):
        # Keep boids within a 100m x 100m x 45m space
        bounds = np.array([[0, 100], [0, 100], [0, 45]])
        force = np.zeros(3)

        for i in range(3):
            if boid.position[i] < bounds[i][0]:
                force[i] = 2.0  # Increased from 1.0 to 2.0
            elif boid.position[i] > bounds[i][1]:
                force[i] = -2.0  # Increased from -1.0 to -2.0
        return force * 0.5


fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection="3d")

# Create the position of the sliders
plt.subplots_adjust(left=0.1, bottom=0.3)
ax_cohesion = plt.axes([0.15, 0.20, 0.75, 0.02])
ax_separation = plt.axes([0.15, 0.15, 0.75, 0.02])
ax_alignment = plt.axes([0.15, 0.10, 0.75, 0.02])
ax_boids = plt.axes([0.15, 0.05, 0.75, 0.02])

cohesion_slider = Slider(ax_cohesion, "Cohesion", 0, 5, valinit=0.2, valstep=0.1)
cohesion_slider.label.set_color("#98C379")  # Green for cohesion
separation_slider = Slider(ax_separation, "Separation", 0, 5, valinit=0.1, valstep=0.1)
separation_slider.label.set_color("#E06C75")  # Red for separation
alignment_slider = Slider(ax_alignment, "Alignment", 0, 5, valinit=0.3, valstep=0.1)
alignment_slider.label.set_color("#E5C07B")  # Yellow for alignment
boids_slider = Slider(ax_boids, "Boids", 1, 500, valinit=50, valstep=1)

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

# Create a global variable to control the animation
running = True


def reset(event):
    global flock, running
    # Reset the flock to its initial state
    flock = Flock(int(boids_slider.val))
    # Reset the running variable to True
    running = True
    # Reset the slider values to their initial values
    cohesion_slider.set_val(0.2)
    separation_slider.set_val(0.1)
    alignment_slider.set_val(0.3)
    boids_slider.set_val(50)


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


# Create the initial flock
flock = Flock(int(boids_slider.val))


def animate(i):
    global running
    if running:
        ax.clear()
        colors = flock.update_boids(
            cohesion_slider.val, separation_slider.val, alignment_slider.val
        )
        positions = [flock.meters_to_latlon(boid.position) for boid in flock.boids]
        ax.scatter(
            [pos[1] for pos in positions],  # longitude
            [pos[0] for pos in positions],  # latitude
            [pos[2] for pos in positions],  # altitude
            c=colors,
        )
        ax.set_xlim(-81.052, -81.048)
        ax.set_ylim(29.187, 29.191)
        ax.set_zlim(0, 150)


def update(val):
    global flock
    flock = Flock(int(boids_slider.val))


boids_slider.on_changed(update)

ani = FuncAnimation(fig, animate, frames=500, interval=100)

plt.show()

# Save the id of the figure
fig_id = fig.number

# Update the boids and write their data to the database every half second
while True:
    # If the figure doesn't exist, break the loop
    if not plt.fignum_exists(fig_id):
        break
    flock.update_boids(cohesion_slider.val, separation_slider.val, alignment_slider.val)
