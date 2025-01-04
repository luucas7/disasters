from dash import html, dcc
from dash.dependencies import Input, Output
from typing import Any, Dict
import numpy as np

from src.components.navbar import Navbar
from src.components.filter import Filter
from src.components.card import Card
from src.components.map import Map
from src.components.time_visualization import TimeVisualization

from src.graphics.map import register_callbacks as map_callbacks
from src.graphics.timed_count import register_callbacks as time_callbacks

def create_dashboard_layout(data: Any, geojson: Dict[str, Any]) -> html.Div:
    """Create the main dashboard layout."""
    
    # Get min/max years for global filters
    min_year = int(data["Start Year"].min()) if data is not None else None
    max_year = int(data["Start Year"].max()) if data is not None else None
    
    # Create filter instances for each visualization
    map_filters = Filter(data, "map")
    time_filters = Filter(data, "time")
    
    return html.Div([
        # Navigation
        Navbar()(),
        
        # Global filters row
        html.Div([
            html.Div([
                html.Label("Start Year"),
                dcc.Dropdown(
                    id="start-year-filter",
                    options=map_filters._get_year_options(),
                    value=min_year
                )
            ], className="w-1/4"),
            html.Div([
                html.Label("End Year"),
                dcc.Dropdown(
                    id="end-year-filter",
                    options=map_filters._get_year_options(),
                    value=max_year
                )
            ], className="w-1/4"),
        ], className="flex gap-4 p-4 fixed w-full top-16 bg-white z-40 shadow-sm"),
        
        # Main content grid
        html.Div([
            # Map section
            html.Div([
                Card(
                    title="Geographic Distribution",
                    filters=[
                        html.Div([
                            html.Label("Disaster Type"),
                            dcc.Dropdown(id="disaster-type-filter")
                        ], className="w-1/2"),
                        html.Div([
                            html.Label("Region"),
                            dcc.Dropdown(id="region-filter")
                        ], className="w-1/2"),
                    ]
                )(Map(data, geojson).layout)
            ], className="w-3/4"),
            
            # Side panel
            html.Div([
                # Time series
                Card(
                    title="Temporal Analysis",
                    filters=[
                        html.Div([
                            html.Label("Group By"),
                            dcc.Dropdown(id="group-by-filter")
                        ]),
                        html.Div([
                            html.Label("Impact Metric"),
                            dcc.Dropdown(id="impact-metric-filter")
                        ])
                    ]
                )(TimeVisualization(data).layout)
            ], className="w-1/4")
            
        ], className="flex gap-4 p-4 mt-24 bg-gray-100 min-h-screen")
    ])


def init_callbacks(app: Any, data: Any, geojson: Dict[str, Any]) -> None:
    """Initialize dashboard callbacks."""
    
    app.config.suppress_callback_exceptions = True

    map_callbacks(app, data, geojson)
    time_callbacks(app, data)

