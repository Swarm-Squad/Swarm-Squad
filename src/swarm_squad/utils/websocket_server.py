import asyncio
import json
import sqlite3
from datetime import datetime
from functools import lru_cache
from time import time

import pandas as pd
import websockets
from websockets.exceptions import ConnectionClosedError

from swarm_squad.utils.db_init import get_db_path
from swarm_squad.utils.logger import get_logger

# Create module logger
logger = get_logger("websocket_server")

# Get the database path
DB_PATH = get_db_path()


class DroneWebsocketServer:
    def __init__(self, host="localhost", port=8051):
        self.host = host
        self.port = port
        self.connected_clients = set()
        self.last_update = 0
        self.cache_ttl = 0.05  # 50ms cache TTL for smoother updates
        self.stop_event = asyncio.Event()
        self.server = None
        self._tasks = []
        self._last_drone_data = None  # Store last successful data
        self._telemetry_was_empty = (
            False  # Track telemetry empty state to avoid repetitive logs
        )

    @lru_cache(maxsize=1)
    def get_drone_data(self, timestamp):
        """Cache drone data for short periods to reduce database load"""
        try:
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql_query("SELECT * from telemetry", conn)
            conn.close()

            if df.empty:
                # Only log warning if this is a state change
                if not self._telemetry_was_empty:
                    logger.warning("Telemetry table is empty")
                    self._telemetry_was_empty = True
                return self._last_drone_data or {
                    "droneCoords": [],
                    "droneNames": [],
                    "dronePitch": [],
                    "droneYaw": [],
                    "droneRoll": [],
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                # Reset empty state flag when data is found
                if self._telemetry_was_empty:
                    logger.info("Telemetry data is now available")
                    self._telemetry_was_empty = False

            data = {
                "droneCoords": [[row["Location"]] for _, row in df.iterrows()],
                "droneNames": [
                    [f"Drone {row['Agent Name']}"] for _, row in df.iterrows()
                ],
                "dronePitch": [[row["Pitch"]] for _, row in df.iterrows()],
                "droneYaw": [[row["Yaw"]] for _, row in df.iterrows()],
                "droneRoll": [[row["Roll"]] for _, row in df.iterrows()],
                "timestamp": datetime.now().isoformat(),
            }

            # Store last successful data
            self._last_drone_data = data
            return data

        except Exception as e:
            logger.error(f"Error getting drone data: {e}")
            # Return last known data or empty data if not available
            return self._last_drone_data or {
                "droneCoords": [],
                "droneNames": [],
                "dronePitch": [],
                "droneYaw": [],
                "droneRoll": [],
                "timestamp": datetime.now().isoformat(),
            }

    async def broadcast_drone_data(self):
        error_count = 0
        max_errors = 3
        recovery_delay = 0.2  # 200ms

        while not self.stop_event.is_set():
            try:
                current_time = time()
                if current_time - self.last_update >= self.cache_ttl:
                    drone_data = self.get_drone_data(
                        int(current_time * 20)  # Round to 50ms
                    )
                    self.last_update = current_time

                    if self.connected_clients:
                        # Create a list to store tasks
                        tasks = []
                        for client in list(self.connected_clients):
                            try:
                                # Create a task for each client
                                tasks.append(client.send(json.dumps(drone_data)))
                            except Exception as e:
                                logger.error(f"Error creating send task: {e}")
                                # Don't break the whole loop for a single client error
                                continue

                        # Execute all send tasks together
                        if tasks:
                            results = await asyncio.gather(
                                *tasks, return_exceptions=True
                            )
                            # Check for exceptions in results
                            for result in results:
                                if isinstance(result, Exception):
                                    error_count += 1
                                    logger.error(f"Error in client send: {result}")

                            # Reset error count on success
                            if not any(isinstance(r, Exception) for r in results):
                                error_count = 0

                # If we've had too many errors in a row, wait a bit longer
                if error_count >= max_errors:
                    logger.warning(f"Too many errors ({error_count}), increasing delay")
                    await asyncio.sleep(recovery_delay)
                    error_count = 0  # Reset after recovery
                else:
                    await asyncio.sleep(0.05)  # 50ms update rate

            except Exception as e:
                logger.error(f"Error broadcasting data: {e}")
                error_count += 1
                await asyncio.sleep(0.1)  # Slightly longer sleep on error

    async def handle_client(self, websocket):
        logger.debug("New client connected")
        self.connected_clients.add(websocket)
        try:
            # Send initial data immediately to new client
            if self._last_drone_data:
                await websocket.send(json.dumps(self._last_drone_data))

            await websocket.wait_closed()
        except ConnectionClosedError:
            logger.error("Client connection closed unexpectedly")
        except Exception as e:
            logger.error(f"Error handling client: {e}")
        finally:
            self.connected_clients.remove(websocket)
            logger.debug("Client disconnected")

    def stop(self):
        """Stop the websocket server"""
        logger.debug("Stopping WebSocket server...")
        self.stop_event.set()

        # Close all connected clients
        if self.connected_clients:
            logger.info(f"Closing {len(self.connected_clients)} client connections...")
            loop = asyncio.get_event_loop_policy().get_event_loop()
            if loop.is_running():
                for client in list(self.connected_clients):
                    try:
                        loop.create_task(
                            client.close(code=1001, reason="Server shutting down")
                        )
                    except Exception as e:
                        logger.error(f"Error closing client connection: {e}")
            else:
                logger.warning(
                    "Event loop not running, cannot close client connections gracefully"
                )

        # Cancel any pending tasks
        for task in self._tasks:
            if not task.done():
                task.cancel()

        # Close the server
        if self.server:
            self.server.close()

    async def start_server(self):
        self.stop_event.clear()
        try:
            server = websockets.serve(
                self.handle_client,
                self.host,
                self.port,
                ping_interval=20,
                ping_timeout=20,
                compression=None,
                # Explicitly set the origins parameter to allow any origin
                origins=None,
            )

            self.server = await server
            logger.info(f"WebSocket server running at ws://{self.host}:{self.port}")

            # Create a task for the broadcast loop
            broadcast_task = asyncio.create_task(self.broadcast_drone_data())
            self._tasks.append(broadcast_task)

            # Wait until stop event is set
            await self.stop_event.wait()

        except Exception as e:
            logger.error(f"WebSocket server error: {e}")
        finally:
            self.stop_event.set()

            # Cancel all tasks
            for task in self._tasks:
                if not task.done():
                    task.cancel()

            # Close all connections
            for client in list(self.connected_clients):
                try:
                    await client.close(code=1001, reason="Server shutting down")
                except Exception as e:
                    logger.error(f"Error closing client connection: {e}")

            # Close server
            if self.server:
                self.server.close()
                await self.server.wait_closed()
                logger.debug("WebSocket server closed")

    def run(self):
        try:
            asyncio.run(self.start_server())
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")


if __name__ == "__main__":
    server = DroneWebsocketServer()
    server.run()
