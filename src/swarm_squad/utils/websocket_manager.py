import asyncio
import atexit
import os
import socket
import threading
import time

from swarm_squad.utils.websocket_server import DroneWebsocketServer


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
            self._server = DroneWebsocketServer()

    def is_port_in_use(self, port, host="localhost"):
        """Check if the port is already in use"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                return False
            except socket.error:
                return True

    def is_websocket_running(self):
        """Check if the websocket server is running"""
        return self._is_running and (
            self._websocket_thread is not None and self._websocket_thread.is_alive()
        )

    def start_websocket(self):
        """Start the WebSocket server in a background thread"""
        if self.is_websocket_running():
            print("[INFO] WebSocket server already running")
            return

        # Check if port is already in use
        if self.is_port_in_use(8051):
            print(
                "[INFO] Port 8051 is already in use, assuming WebSocket server is running"
            )
            self._is_running = True
            return

        self._is_running = True

        # Create and start thread for websocket server
        self._websocket_thread = threading.Thread(
            target=self._run_websocket_server,
            daemon=True,  # This ensures the thread will exit when the main program exits
        )
        self._websocket_thread.start()
        print("[INFO] WebSocket server started")

    def _run_websocket_server(self):
        """Run the websocket server in its own event loop"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._server.start_server())
        except Exception as e:
            print(f"[ERROR] WebSocket server error: {e}")
        finally:
            loop.close()

    def cleanup_websocket(self, force=False):
        """Cleanup the WebSocket server"""
        if self._is_running or force:
            print("[INFO] Shutting down WebSocket server...")
            self._is_running = False

            # Signal the server to stop
            if hasattr(self, "_server"):
                self._server.stop()

            # Wait for the thread to finish if it exists
            if self._websocket_thread and self._websocket_thread.is_alive():
                self._websocket_thread.join(timeout=5)  # Wait up to 5 seconds

            # Force release the port
            self.force_release_port(8051)

            print("[INFO] WebSocket server stopped")

    def force_release_port(self, port, host="localhost"):
        """Force release a port by creating and closing a socket"""
        # First try to connect to check if something is listening
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()

        if result == 0:  # Port is in use
            try:
                # Try to kill the process using the port (Linux only)
                try:
                    os.system(f"fuser -k {port}/tcp >/dev/null 2>&1")
                    print(f"[INFO] Killed process using port {port}")
                except Exception as e:
                    print(f"[ERROR] Could not kill process using port {port}: {e}")

                # Wait a moment to allow the port to be released
                time.sleep(0.5)

                # Create a socket with SO_REUSEADDR and SO_REUSEPORT if available
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                # SO_REUSEPORT may not be available on all platforms
                try:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                except (AttributeError, OSError) as e:
                    print(f"[ERROR] Could not set SO_REUSEPORT: {e}")

                try:
                    s.bind((host, port))
                    s.close()
                    print(f"[INFO] Successfully released port {port}")
                except socket.error:
                    print(
                        f"[INFO] Port {port} is still in use but will be released when app exits"
                    )
            except Exception as e:
                print(f"[ERROR] Could not release port {port}: {e}")
        else:
            print(f"[INFO] Port {port} is not in use")
