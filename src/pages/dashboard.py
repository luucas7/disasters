# src/pages/dashboard.py
from dash import html, dcc
from typing import Any, Dict

from src.components.navbar import Navbar
from src.components.filter import Filter
from src.components.checkbox import Checkbox
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
    
    pie_chart_group_checkbox = Checkbox(
        id="group-similar-disasters",
        options=[{"label": "Group Similar Disasters", "value": "group"}],
        value=["group"]
    )()
    
    return html.Div([
        Navbar()(),
        SideMenu(data)(),
                
        # Main content
        html.Div([
            # Left column - Main visualizations
            html.Div([
                # Map
                Card(
                    title="Geographic Distribution",
                    filters=[disaster_filter, region_filter]
                )(Map(data, geojson)()),
                
                # Time series chart
                Card(
                    title="Temporal Evolution",
                    filters=[group_by_filter, impact_metric_filter]
                )(TimedCount(data)())
            ], className="flex-1 flex flex-col gap-4"),
            
            
            # Right column - Secondary visualizations and stats
            html.Div([
                # Database stats card
                Card(title="Overall Statistics", className="max-h-[200px]")(
                    html.Div([
                        html.P(f"Total number of recorded disasters: {len(data):,}", 
                              className="text-xl font-semibold text-blue-600"),
                        html.P(f"Date range: {int(data['Start Year'].min())} - {int(data['Start Year'].max())}",
                              className="text-gray-600 mt-2"),
                        html.P(f"Number of countries: {data['Country'].nunique():,}",
                              className="text-gray-600"),
                    ], className="p-4")
                ),
                
                # Pie chart
                Card(
                    title="Disaster Type Distribution",
                    filters=[pie_chart_group_checkbox]
                )(DisasterPieChart(data)())
            ], className="w-1/3 flex flex-col gap-4"),

        ], className="flex gap-4 p-4 ml-64 mt-16 bg-gray-100 min-h-screen")
    ])

def init_callbacks(app: Any, data: Any, geojson: Dict[str, Any]) -> None:
    """Initialize dashboard callbacks."""
    app.config.suppress_callback_exceptions = True
    
    # Register callbacks from components
    register_map_callbacks(app, data, geojson)
    register_timed_count_callbacks(app, data)
    register_pie_callbacks(app, data)