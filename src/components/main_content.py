from dash import html
from typing import Any, Dict
from src.components.map import Map
from src.components.time_visualization import TimeVisualization


class MainContent:
    """Main content component containing the visualization."""

    def __init__(
        self, data: Any = None, geojson: Dict[str, Any] = None, view_type: str = "map"
    ):
        self.data = data
        self.geojson = geojson
        self.view_type = view_type
        self.layout = self._create_layout()

    def _create_layout(self):
        if self.view_type == "map":
            content = Map(self.data, self.geojson)
        elif self.view_type == "time":
            content = TimeVisualization(self.data)
        else:
            return html.Div("About page content here", className="p-4")

        return html.Div([content.layout], className="flex-1 ml-64 mt-16")

    def __call__(self):
        return self.layout
