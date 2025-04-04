import asyncio
import atexit
import os
import signal
import socket
import subprocess
import threading
import time

from swarm_squad.utils.logger import get_logger
from swarm_squad.utils.websocket_server import DroneWebsocketServer

# Create module logger
logger = get_logger("websocket_manager")


class WebSocketManager:
    _instance = None
    _websocket_server = None
    _is_running = False
    _websocket_thread = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WebSocketManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.initialized = True
            atexit.register(self.cleanup_websocket)

            # Register signal handlers for cleaner shutdown
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)

            self._server = DroneWebsocketServer()

    def _signal_handler(self, sig, frame):
        """Handle termination signals"""
        logger.info(f"Received signal {sig}, shutting down...")
        self.cleanup_websocket(force=True)
        # Continue with default signal handling
        signal.default_int_handler(sig, frame)

    def is_port_in_use(self, port, host="localhost"):
        """Check if the port is already in use using the same method as force_release_port"""
        # Use connect_ex as a more reliable way to check if port is in use
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()

        if result == 0:
            # Connection succeeded, port is in use
            return True
        else:
            # Connection failed, port is free
            return False

    def is_websocket_running(self):
        """Check if the websocket server is running"""
        return self._is_running and (
            self._websocket_thread is not None and self._websocket_thread.is_alive()
        )

    def start_websocket(self):
        """Start the WebSocket server in a background thread (only in main process)."""
        # Prevent execution in the reloader process
        if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            logger.debug(
                f"Process ID {os.getpid()}: Skipping WebSocket start in reloader process."
            )
            return

        logger.debug(
            f"Process ID {os.getpid()}: Attempting to start WebSocket server..."
        )

        if self.is_websocket_running():
            logger.debug("WebSocket server already running")
            return

        # Check if port is already in use
        port_status = self.is_port_in_use(8051)

        if port_status:
            logger.debug("Port 8051 is in use, attempting to release it")
            release_success = self.force_release_port(8051)

            if not release_success:
                logger.error(
                    "Failed to release port 8051, websocket server will not start"
                )
                return

            # Double-check port status after release attempt
            if self.is_port_in_use(8051):
                logger.error(
                    "Port 8051 is still in use after release attempt, websocket server will not start"
                )
                return
        else:
            logger.debug("Port 8051 is available for use")

        # At this point, we've verified the port is free
        self._is_running = True

        # Create and start thread for websocket server
        self._websocket_thread = threading.Thread(
            target=self._run_websocket_server,
            daemon=True,  # This ensures the thread will exit when the main program exits
        )
        self._websocket_thread.start()
        logger.info("Started background WebSocket server")

    def _run_websocket_server(self):
        """Run the websocket server in its own event loop"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._server.start_server())
        except Exception as e:
            logger.error(f"WebSocket server error: {e}")
        finally:
            loop.close()

    def cleanup_websocket(self, force=False):
        """Cleanup the WebSocket server"""
        if self._is_running or force:
            logger.debug("Shutting down WebSocket server...")
            self._is_running = False

            # Signal the server to stop
            if hasattr(self, "_server"):
                self._server.stop()

            # Wait for the thread to finish if it exists
            if self._websocket_thread and self._websocket_thread.is_alive():
                self._websocket_thread.join(timeout=5)  # Wait up to 5 seconds

            # Force release the port
            self.force_release_port(8051)

            logger.debug("WebSocket server stopped")

    def force_release_port(self, port, host="localhost"):
        """Force release a port by creating and closing a socket"""
        # First try to connect to check if something is listening
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()

        if result == 0:  # Port is in use
            logger.debug(
                f"Port {port} is confirmed to be in use (connect_ex returned 0)"
            )
            try:
                # Try multiple methods to kill the process using the port (Linux only)
                try:
                    # First try fuser (commonly available)
                    try:
                        logger.info(
                            f"Attempting to kill process using port {port} with fuser"
                        )
                        os.system(f"fuser -k {port}/tcp >/dev/null 2>&1")
                    except Exception:
                        pass

                    # Try lsof as an alternative
                    try:
                        logger.info(
                            f"Attempting to find and kill process using port {port} with lsof"
                        )
                        process = subprocess.run(
                            ["lsof", "-i", f":{port}", "-t"],
                            capture_output=True,
                            text=True,
                        )
                        if process.stdout.strip():
                            for pid in process.stdout.strip().split("\n"):
                                if pid:
                                    os.system(f"kill -9 {pid} >/dev/null 2>&1")
                                    logger.info(
                                        f"Killed process {pid} using port {port}"
                                    )
                    except Exception:
                        pass

                    # Try netstat as another alternative
                    try:
                        logger.info(
                            f"Attempting to find and kill process using port {port} with netstat"
                        )
                        process = subprocess.run(
                            ["netstat", "-tlnp"], capture_output=True, text=True
                        )
                        for line in process.stdout.split("\n"):
                            if f":{port}" in line and "LISTEN" in line:
                                parts = line.split()
                                for part in parts:
                                    if "/" in part:
                                        pid = part.split("/")[0]
                                        os.system(f"kill -9 {pid} >/dev/null 2>&1")
                                        logger.info(
                                            f"Killed process {pid} using port {port}"
                                        )
                    except Exception:
                        pass

                except Exception as e:
                    logger.warning(f"Could not kill process using port {port}: {e}")

                # Wait a moment to allow the port to be released
                time.sleep(1)

                # Check again if the port is in use
                check_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                check_sock.settimeout(1)
                check_result = check_sock.connect_ex((host, port))
                check_sock.close()

                if check_result == 0:
                    logger.warning(f"Port {port} is still in use after kill attempts")
                else:
                    logger.info(f"Successfully released port {port}")
                    return True

                # Create a socket with SO_REUSEADDR and SO_REUSEPORT if available
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                # SO_REUSEPORT may not be available on all platforms
                try:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                except (AttributeError, OSError) as e:
                    logger.warning(f"Could not set SO_REUSEPORT: {e}")

                try:
                    s.bind((host, port))
                    s.close()
                    logger.info(
                        f"Successfully bound to port {port}, it should now be released"
                    )
                    return True
                except socket.error as e:
                    logger.warning(
                        f"Port {port} is still in use and could not be released: {e}"
                    )
                    return False
            except Exception as e:
                logger.error(f"Could not release port {port}: {e}")
                return False
        else:
            logger.debug(
                f"Port {port} is confirmed to be free (connect_ex returned {result})"
            )
            return True
