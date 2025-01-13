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
from src.graphics.statistics import Statistics, register_statistics_callbacks
from src.graphics.country_details import CountryDetails, register_details_callbacks

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

    pie_chart_other_checkbox = Checkbox(
        id="show-other",
        options=[{"label": "Show every categories", "value": "other"}],
        value=["other"]
    )()
    
    return html.Div([
        SideMenu(data)(),
                
        # Main content
        html.Div([
            # Left side - Main visualizations
            html.Div([
                # Map only
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
                # Country details card
                Card(
                    title="Country Details"
                )(CountryDetails(data)()),
                
                # Statistics card
                Card(
                    title="Database Statistics"
                )(Statistics(data)()),
                
                # Pie chart
                Card(
                    title="Disaster Type Distribution",
                    filters=[pie_chart_group_checkbox, pie_chart_other_checkbox],
                    className='min-h-[900px]'
                )(DisasterPieChart(data)())
            ], className="w-1/3 flex flex-col gap-4"),

        ], className="flex gap-4 p-4 ml-64 bg-gray-100 min-h-screen")
    ])

def init_callbacks(app: Any, data: Any, geojson: Dict[str, Any]) -> None:
    """Initialize dashboard callbacks."""
    app.config.suppress_callback_exceptions = True
    
    # Register callbacks from components
    register_map_callbacks(app, data, geojson)
    register_timed_count_callbacks(app, data)
    register_pie_callbacks(app, data)
    register_statistics_callbacks(app, data)
    register_details_callbacks(app, data)