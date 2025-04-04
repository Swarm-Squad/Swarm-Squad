import os
from pathlib import Path

from dotenv import load_dotenv

from swarm_squad.utils.logger import get_logger

# Create module logger
logger = get_logger("map_fetcher")

# Define paths for various locations to look for .env files
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # 3 levels up from this file
CURRENT_DIR = Path.cwd()  # Current working directory when command is run
HOME_DIR = Path.home()  # User's home directory
ENV_SEARCH_PATHS = [
    CURRENT_DIR / ".env",  # First check current directory
    HOME_DIR / ".env",  # Then check home directory
    PROJECT_ROOT / ".env",  # Finally check project root (for development)
]
MAP_COMPONENT_PATH = (
    Path(__file__).resolve().parent.parent / "components" / "map_component.html"
)


def load_mapbox_token():
    """Load Mapbox access token from .env file"""
    # Try each possible .env location in order
    env_loaded = False
    for env_path in ENV_SEARCH_PATHS:
        if env_path.exists():
            load_dotenv(env_path)
            env_loaded = True
            break

    if not env_loaded:
        logger.error("No .env file found in search paths!")

    # Get the token from environment
    token = os.getenv("MAPBOX_ACCESS_TOKEN")
    if token:
        logger.debug("MAPBOX_ACCESS_TOKEN loaded successfully.")
    else:
        logger.warning(
            "MAPBOX_ACCESS_TOKEN not found in environment variables after checking .env files."
        )
    return token


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
            <p>Create a .env file in your current directory with:</p>
            <pre style="text-align: left; background: #222; padding: 10px; border-radius: 5px;">MAPBOX_ACCESS_TOKEN=your_token_here</pre>
        </div>
    </div>
    """


def read_map_html():
    """Read map HTML and inject Mapbox token"""
    # Load Mapbox token
    mapbox_token = load_mapbox_token()

    # Check if token exists
    if not mapbox_token:
        logger.warning("No MAPBOX_ACCESS_TOKEN found in environment")
        return get_error_html(
            "Please set a valid MAPBOX_ACCESS_TOKEN in your .env file."
        )

    # Check if map component file exists
    if not MAP_COMPONENT_PATH.exists():
        logger.error(f"Map component file not found at: {MAP_COMPONENT_PATH}")
        return get_error_html(f"Map component file not found at: {MAP_COMPONENT_PATH}")

    # Read and process map component
    try:
        with open(MAP_COMPONENT_PATH, "r") as f:
            content = f.read()
            return content.replace("YOUR_MAPBOX_TOKEN_PLACEHOLDER", mapbox_token)
    except Exception as e:
        logger.error(f"Failed to read map component: {e}")
        return get_error_html(f"Error reading map component: {str(e)}")
