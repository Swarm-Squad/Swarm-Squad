from datetime import datetime
from queue import Queue
from typing import Any, Dict

from swarm_squad.utils.logger import get_logger
from swarm_squad.utils.websocket_manager import WebSocketManager

# Create module logger
logger = get_logger("websocket_writer")


class WebSocketWriter:
    def __init__(self, host="localhost", port=8051):
        self.host = host
        self.port = port
        self._message_queue = Queue()
        # Use existing WebSocket manager instance
        self.ws_manager = WebSocketManager()  # This will return the singleton instance
        logger.debug("WebSocketWriter initialized")

    def ws_writer(self, data: Dict[str, Any]):
        """Write data to the WebSocket server through the database"""
        # Format data for WebSocket clients
        ws_data = {
            "droneCoords": [[loc] for loc in data["Location"]],
            "droneNames": [[f"Drone {name}"] for name in data["Agent Name"]],
            "dronePitch": [[pitch] for pitch in data["Pitch"]],
            "droneYaw": [[yaw] for yaw in data["Yaw"]],
            "droneRoll": [[roll] for roll in data["Roll"]],
            "timestamp": datetime.now().isoformat(),
        }
        self._message_queue.put(ws_data)
        logger.debug(
            f"Added data to WebSocket queue (queue size: {self._message_queue.qsize()})"
        )


# Global WebSocket writer instance
_ws_writer = None


def get_ws_writer() -> WebSocketWriter:
    """Get or create the global WebSocket writer instance"""
    global _ws_writer
    if _ws_writer is None:
        logger.debug("Creating global WebSocketWriter instance")
        _ws_writer = WebSocketWriter()
    return _ws_writer


def ws_writer(data: Dict[str, Any]):
    """Synchronous wrapper for writing data to WebSocket clients"""
    writer = get_ws_writer()
    writer.ws_writer(data)
