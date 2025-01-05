# src/pages/dashboard.py
from dash import html, dcc
from typing import Any, Dict

from src.components.navbar import Navbar
from src.components.filter import Filter
from src.components.side_menu import SideMenu
from src.components.card import Card

# Graphics components
from src.graphics.map import Map, register_map_callbacks
from src.graphics.timed_count import TimedCount, register_timed_count_callbacks
from src.graphics.pie_chart import DisasterPieChart, register_pie_callbacks

def create_dashboard_layout(data: Any, geojson: Dict[str, Any]) -> html.Div:
    """Create the main dashboard layout."""
    
    filters = Filter(data)
    disaster_filter = filters.disaster_filter()
    region_filter = filters.region_filter()
    group_by_filter = filters.group_by_filter()
    impact_metric_filter = filters.impact_metric_filter()                 
    
    return html.Div([
        Navbar()(),
        SideMenu()(),
                
        # Main content
        html.Div([
            # Left side with Map and Pie Chart side by side
            html.Div([
                # Container for Map and Pie side by side
                html.Div([
                    
                    # Map container
                    html.Div([
                        Card(
                            title="Geographic Distribution",
                            filters=[disaster_filter, region_filter]
                        )(Map(data, geojson)())
                    ], className="w-2/3"),  # 2/3 de la largeur
                    
                    # Pie chart container
                    html.Div([
                        Card(
                            title="Disaster Type Distribution"
                        )(DisasterPieChart(data)())
                    ], className="w-1/3"), 
                    
                ], className="flex gap-4"),  # Flex pour les mettre côte à côte
            ], className="w-full"),
            

        ], className="flex gap-4 p-4 ml-64 mt-16 bg-gray-100")
    ])

def init_callbacks(app: Any, data: Any, geojson: Dict[str, Any]) -> None:
    """Initialize dashboard callbacks."""
    app.config.suppress_callback_exceptions = True
    
    # Register callbacks from components
    register_map_callbacks(app, data, geojson)
    register_timed_count_callbacks(app, data)
    register_pie_callbacks(app, data)