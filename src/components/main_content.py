from dash import html
from typing import Any, Dict
from src.components.map import Map

class MainContent:
    """Main content component containing the map."""
    
    def __init__(self, data: Any = None, geojson: Dict[str, Any] = {}):
        self.data = data
        self.geojson = geojson
        self.layout = html.Div([
            Map(self.data, self.geojson)
        ], className="flex-1 ml-64 mt-16")  # ml-64 matches Filter width, mt-16 matches navbar height

    def __call__(self):
        return self.layout