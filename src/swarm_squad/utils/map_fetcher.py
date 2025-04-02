import os

from dotenv import load_dotenv


def read_map_html():
    # Try to load environment variables from different locations
    # First try from the project root directory
    root_dotenv_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        ".env",
    )
    if os.path.exists(root_dotenv_path):
        load_dotenv(root_dotenv_path)
    else:
        # Fallback to default behavior
        load_dotenv()

    mapbox_token = os.getenv("MAPBOX_ACCESS_TOKEN")
    # Check if token is missing or is a placeholder
    if mapbox_token is None:
        print(
            "[WARNING] Using a placeholder Mapbox token. The map may not display correctly."
        )
        print(f"[INFO] Looking for .env file at: {root_dotenv_path}")
        # Return a helpful message instead of raising an error
        return """
        <div id="map" style="width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; color: white; font-family: Arial, sans-serif;">
            <div style="text-align: center; max-width: 80%;">
                <h2>Map Unavailable</h2>
                <p>Please set a valid MAPBOX_ACCESS_TOKEN in your .env file.</p>
                <p>The current token is either missing or using a placeholder value.</p>
                <p>Get a free token at <a href="https://account.mapbox.com/access-tokens/" 
                   style="color: #3498db;" target="_blank">Mapbox</a></p>
            </div>
        </div>
        """

    # Update the path to look in the assets directory relative to the package
    map_path = os.path.join(
        os.path.dirname(__file__), "..", "components", "map_component.html"
    )

    # Create a default map component if the file doesn't exist
    if not os.path.exists(map_path):
        print(f"[WARNING] Map component file not found at: {map_path}")
        return """
        <div id="map" style="width: 100%; height: 100%; display: flex; justify-content: center; align-items: center;
              background-color: rgba(30, 30, 30, 0.9); color: white; font-family: Arial, sans-serif;">
            <div style="text-align: center; max-width: 80%;">
                <h2>Map Component Not Found</h2>
                <p>The map_component.html file could not be located in the assets directory.</p>
            </div>
        </div>
        """

    with open(map_path, "r") as f:
        content = f.read()
        content = content.replace("YOUR_MAPBOX_TOKEN_PLACEHOLDER", mapbox_token)
        return content
