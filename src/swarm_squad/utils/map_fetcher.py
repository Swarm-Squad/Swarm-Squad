import os
from pathlib import Path

from dotenv import load_dotenv

# Define paths
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # 3 levels up from this file
ENV_FILE = PROJECT_ROOT / ".env"
MAP_COMPONENT_PATH = (
    Path(__file__).resolve().parent.parent / "components" / "map_component.html"
)


def load_mapbox_token():
    """Load Mapbox access token from .env file"""
    # Try to load environment from project root first
    if ENV_FILE.exists():
        load_dotenv(ENV_FILE)
        print(f"[INFO] Loaded environment from {ENV_FILE}")
    else:
        # Fallback to default dotenv behavior
        load_dotenv()
        print("[INFO] No .env file found at project root, using default environment")

    # Get the token from environment
    return os.getenv("MAPBOX_ACCESS_TOKEN")


def get_error_html(message):
    """Generate error HTML when map can't be displayed"""
    return f"""
    <div id="map" style="width: 100%; height: 100%; display: flex; justify-content: center; 
         align-items: center; color: white; font-family: Arial, sans-serif;">
        <div style="text-align: center; max-width: 80%;">
            <h2>Map Unavailable</h2>
            <p>{message}</p>
            <p>Get a free token at <a href="https://account.mapbox.com/access-tokens/" 
               style="color: #3498db;" target="_blank">Mapbox</a></p>
        </div>
    </div>
    """


def read_map_html():
    """Read map HTML and inject Mapbox token"""
    # Load Mapbox token
    mapbox_token = load_mapbox_token()

    # Check if token exists
    if not mapbox_token:
        return get_error_html(
            "Please set a valid MAPBOX_ACCESS_TOKEN in your .env file."
        )

    # Check if map component file exists
    if not MAP_COMPONENT_PATH.exists():
        return get_error_html(f"Map component file not found at: {MAP_COMPONENT_PATH}")

    # Read and process map component
    try:
        with open(MAP_COMPONENT_PATH, "r") as f:
            content = f.read()
            return content.replace("YOUR_MAPBOX_TOKEN_PLACEHOLDER", mapbox_token)
    except Exception as e:
        print(f"[ERROR] Failed to read map component: {e}")
        return get_error_html(f"Error reading map component: {str(e)}")
