from typing import Any, Dict

import pandas as pd
from dash import html, Dash

from src.components.checkbox import Checkbox
from src.components.filter import Filter
from src.components.fullscreen_card import FullscreenCard, register_fullscreen_callbacks
from src.components.side_menu import SideMenu

# Graphics components
from src.graphics.country_details import CountryDetails, register_details_callbacks
from src.graphics.disaster_table import DisasterTable, register_table_callbacks
from src.graphics.map import Map, register_map_callbacks
from src.graphics.pie_chart import DisasterPieChart, register_pie_callbacks
from src.graphics.statistics import Statistics, register_statistics_callbacks
from src.graphics.timed_count import TimedCount, register_timed_count_callbacks


def create_dashboard_layout(data: pd.DataFrame, geojson: Dict[str, Any], areas: Dict[str, float]) -> html.Div:
    """Create the main dashboard layout."""
    filters = Filter(data)
    disaster_filter = filters.disaster_filter("disaster-type-filter")
    region_filter = filters.region_filter("region-filter")
    group_by_filter = filters.group_by_filter("group-by-filter")
    temporal_impact_metric_filter = filters.temporal_impact_metric_filter("temporal-impact-metric-filter")
    map_impact_metric_filter = filters.map_impact_metric_filter("map-impact-metric-filter")

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
        options=[{"label": "Depending on the current country", "value": "country"}],
        value=["country"]
    )()
    
    return html.Div([
        SideMenu(data)(),
                
        # Main content
        html.Div([
            # Left side - Main visualizations
            html.Div([
                # Map only
                FullscreenCard(
                    title="Geographic distribution of disasters",
                    filters=[disaster_filter, region_filter, map_impact_metric_filter],
                    caption="TODO"
                )(Map(data, geojson, areas)()),
                
                # Time series chart
                FullscreenCard(
                    title="Disaster occurrences through time",
                    filters=[group_by_filter, temporal_impact_metric_filter],
                    caption= "   Note : The trend in the number of disasters shows significant peaks in certain years, notably in 2010 with the devastating earthquake in Haiti (see Total Deaths in Impact Metric). In recent years, there has been a slight downward trend in the total number of disasters recorded, although their human impact remains highly variable depending on the event."
                )(TimedCount(data)()),
            ], className="flex-1 flex flex-col gap-4"),
            
            # Right column - Secondary visualizations and stats
            html.Div([
                # Country details FullscreenCard
                FullscreenCard(
                    title="Country details",
                    caption="   Note : Exploring the data country by country, we discover very different profiles: the USA is mainly affected by storms and tornadoes, China records a high number of industrial accidents, while countries like Niger face recurrent epidemics. These differences reflect the specific vulnerabilities linked to each country's context: level of industrialization, healthcare system, or exposure to meteorological phenomena.",
                )(CountryDetails(data)()),
                
                # Statistics FullscreenCard
                FullscreenCard(
                    title="Database statistics"
                )(Statistics(data)()),
                
                # Pie chart
                FullscreenCard(
                    title="Disaster type distribution",
                    filters=[pie_chart_group_checkbox, pie_chart_other_checkbox, pie_chart_country_checkbox],
                    caption="   Note : Although floods and storms are the most frequent disasters, earthquakes cause the most deaths. This difference can be explained by the sudden and unpredictable nature of earthquakes, making evacuation impossible, unlike floods and storms, which can often be anticipated thanks to weather forecasting systems.",
                    className='min-h-[900px]'
                )(DisasterPieChart(data)()),

                # Table
                FullscreenCard(
                    title="Deadliest disasters",
                    filters=[]
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
    register_fullscreen_callbacks(app)