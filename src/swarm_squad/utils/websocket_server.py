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
        self.cache_ttl = 0.1  # 100ms cache TTL
        self.stop_event = asyncio.Event()
        self.server = None
        self._tasks = []

    @lru_cache(maxsize=1)
    def get_drone_data(self, timestamp):
        """Cache drone data for short periods to reduce database load"""
        try:
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql_query("SELECT * from telemetry", conn)
            conn.close()

            return {
                "droneCoords": [[row["Location"]] for _, row in df.iterrows()],
                "droneNames": [
                    [f"Drone {row['Agent Name']}"] for _, row in df.iterrows()
                ],
                "dronePitch": [[row["Pitch"]] for _, row in df.iterrows()],
                "droneYaw": [[row["Yaw"]] for _, row in df.iterrows()],
                "droneRoll": [[row["Roll"]] for _, row in df.iterrows()],
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting drone data: {e}")
            # Return empty data on error
            return {
                "droneCoords": [],
                "droneNames": [],
                "dronePitch": [],
                "droneYaw": [],
                "droneRoll": [],
                "timestamp": datetime.now().isoformat(),
            }

    async def broadcast_drone_data(self):
        while not self.stop_event.is_set():
            try:
                current_time = time()
                if current_time - self.last_update >= self.cache_ttl:
                    drone_data = self.get_drone_data(
                        int(current_time * 10)
                    )  # Round to 100ms
                    self.last_update = current_time

                    if self.connected_clients:
                        websockets_coros = [
                            client.send(json.dumps(drone_data))
                            for client in self.connected_clients
                        ]
                        await asyncio.gather(*websockets_coros, return_exceptions=True)

            except Exception as e:
                logger.error(f"Error broadcasting data: {e}")

            await asyncio.sleep(0.1)  # 100ms update rate

    async def handle_client(self, websocket):
        logger.debug("New client connected")
        self.connected_clients.add(websocket)
        try:
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
