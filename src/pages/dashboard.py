from typing import Any, Dict

import pandas as pd
from dash import Dash, html

from src.components.card import Card, register_card_callback
from src.components.checkbox import Checkbox
from src.components.filter import Filter
from src.components.side_menu import SideMenu, register_side_menu_callbacks

# Graphics components
from src.graphics.country_details import CountryDetails, register_details_callbacks
from src.graphics.disaster_table import DisasterTable, register_table_callbacks
from src.graphics.map import Map, register_map_callbacks
from src.graphics.pie_chart import DisasterPieChart, register_pie_callbacks
from src.graphics.statistics import Statistics, register_statistics_callbacks
from src.graphics.timed_count import TimedCount, register_timed_count_callbacks
from src.graphics.treemap import DisasterTreemap, register_treemap_callbacks

# Import resource strings
from src.utils.resources import (
    DETAILS_CARD_CAPTION,
    MAP_CARD_CAPTION,
    PIE_CARD_CAPTION,
    TABLE_CARD_CAPTION,
    TEMPORAL_CARD_CAPTION,
    TREEMAP_CARD_CAPTION,
)


def create_dashboard_layout(app: Dash, data: pd.DataFrame, geojson: Dict[str, Any], areas: Dict[str, float]) -> html.Div:
    """Create the main dashboard layout."""
    filters = Filter(data)
    disaster_filter = filters.disaster_filter("disaster-type-filter")
    region_filter = filters.region_filter("region-filter")
    group_by_filter = filters.group_by_filter("group-by-filter")
    temporal_impact_metric_filter = filters.temporal_impact_metric_filter("temporal-impact-metric-filter")
    treemap_region_filter = filters.region_filter("treemap-region-filter")
    treemap_impact_metric_filter = filters.temporal_impact_metric_filter("treemap-impact-metric-filter")
    map_impact_metric_filter = filters.map_impact_metric_filter("map-impact-metric-filter")
    disaster_filter_without_all = filters.disaster_filter_without_all("disaster-type-filter_without_all")

    pie_chart_group_checkbox = Checkbox(
        id="group-similar-disasters",
        options=[{"label": "Group Similar Disasters", "value": "group"}],
        value=["group"]
    )()

    pie_chart_other_checkbox = Checkbox(
        id="show-other",
        options=[{"label": "Group smaller categories", "value": "other"}],
        value=["other"]
    )()
    
    pie_chart_country_checkbox = Checkbox(
        id="show-country",
        options=[{"label": "Depending on the country selected on the map", "value": "country"}],
        value=["country"]
    )()
    
    return html.Div([
        SideMenu(data)(),
                
        # Main content
        html.Div([
            # Left side - Main visualizations
            html.Div([
                # Map only
                Card(
                    id="map-card",
                    title="Geographic distribution of disasters",
                    filters=[disaster_filter, region_filter, map_impact_metric_filter],
                    caption=MAP_CARD_CAPTION
                )(Map(data, geojson, areas)()),
                
                # Time series chart
                Card(
                    id="temporal-card",
                    title="Disaster occurrences through time",
                    filters=[group_by_filter, temporal_impact_metric_filter],
                    caption=TEMPORAL_CARD_CAPTION
                )(TimedCount(data)()),
                
                # Treemap
                Card(
                    id="treemap-card",
                    title="Disaster impact by region",
                    filters=[disaster_filter_without_all, treemap_region_filter, treemap_impact_metric_filter],
                    caption=TREEMAP_CARD_CAPTION
                )(DisasterTreemap(data)()),
            ], className="flex-1 flex flex-col gap-4"),
            
            # Right column - Secondary visualizations and stats
            html.Div([
                # Country details Card
                Card(
                    id="details-card",
                    title="Country details",
                    caption=DETAILS_CARD_CAPTION
                )(CountryDetails(data)()),
                
                # Statistics Card
                Card(
                    id="stats-card",
                    title="Database statistics"
                )(Statistics(data)()),
                
                # Pie chart
                Card(
                    id="pie-card",
                    title="Disaster type distribution",
                    filters=[pie_chart_group_checkbox, pie_chart_other_checkbox, pie_chart_country_checkbox],
                    caption=PIE_CARD_CAPTION,
                    className='min-h-[900px]'
                )(DisasterPieChart(data)()),

                # Table
                Card(
                    id="table-card",
                    title="Deadliest disasters",
                    filters=[],
                    caption=TABLE_CARD_CAPTION
                )(DisasterTable(data)()),

            ], className="w-1/3 flex flex-col gap-4"),

        ], className="flex gap-4 p-4 ml-64 bg-gray-300 min-h-screen")
    ])

def init_callbacks(app: Dash, data: pd.DataFrame, geojson: Dict[str, Any], areas: Dict[str, float]) -> None:
    """Initialize dashboard callbacks."""
    app.config.suppress_callback_exceptions = True
    
    # Register callbacks from components
    register_map_callbacks(app, data, geojson, areas)
    register_timed_count_callbacks(app, data)
    register_pie_callbacks(app, data)
    register_statistics_callbacks(app, data)
    register_details_callbacks(app, data)
    register_table_callbacks(app, data)
    register_treemap_callbacks(app, data)
    register_side_menu_callbacks(app, data)


    for id in ["map-card", "temporal-card", "details-card", "stats-card", "pie-card", "table-card", "treemap-card"]:
        register_card_callback(app, id)
