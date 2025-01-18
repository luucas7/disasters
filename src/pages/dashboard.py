from typing import Any, Dict

import pandas as pd
from dash import html, Dash

from src.components.checkbox import Checkbox
from src.components.filter import Filter
from src.components.side_menu import SideMenu
from src.components.card import Card, register_card_callback

# Graphics components
from src.graphics.country_details import CountryDetails, register_details_callbacks
from src.graphics.disaster_table import DisasterTable, register_table_callbacks
from src.graphics.map import Map, register_map_callbacks
from src.graphics.pie_chart import DisasterPieChart, register_pie_callbacks
from src.graphics.statistics import Statistics, register_statistics_callbacks
from src.graphics.timed_count import TimedCount, register_timed_count_callbacks
from src.graphics.treemap import DisasterTreemap, register_treemap_callbacks


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
                    caption="   Note: The map shows that the absolute number of disasters is highest in densely populated countries such as China, India and the USA. However, if we consider density in relation to surface area, we can see that many small countries are actually very affected in proportion to their size, such as the Philippines and Haiti. A country's vulnerability therefore depends not only on its exposure to hazards, but also on its ability to cope with them."
                )(Map(data, geojson, areas)()),
                
                # Time series chart
                Card(
                    id="temporal-card",
                    title="Disaster occurrences through time",
                    filters=[group_by_filter, temporal_impact_metric_filter],
                    caption= "   Note : In recent years, there has been a slight downward trend in the total number of disasters recorded, although their human impact remains highly variable depending on the event. This visualization shows that the impact of disasters strongly depends on the local context: developed countries suffer greater economic losses, while developing countries record more victims, reflecting global disparities in disaster resilience."
                )(TimedCount(data)()),
                
                # Treemap
                Card(
                    title="Disaster impact by region",
                    filters=[disaster_filter_without_all, treemap_region_filter, treemap_impact_metric_filter],
                    caption="   Note: The treemap reveals specific geographical vulnerabilities: China and the Philippines are particularly hard hit by floods, Japan and Indonesia by earthquakes, while the USA is more affected by storms. These differences reflect the specific vulnerabilities linked to each country's context: level of industrialization, healthcare system, or exposure to meteorological phenomena."
                )(DisasterTreemap(data)()),
            ], className="flex-1 flex flex-col gap-4"),
            
            # Right column - Secondary visualizations and stats
            html.Div([
                # Country details Card
                Card(
                    id="details-card",
                    title="Country details",
                    caption="   Note : Exploring the data country by country, we discover very different profiles: the USA is mainly affected by storms and tornadoes, China records a high number of industrial accidents, while countries like Niger face recurrent epidemics.",
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
                    caption="   Note : Although floods and storms are the most frequent disasters, earthquakes cause the most deaths. This difference can be explained by the sudden and unpredictable nature of earthquakes, making evacuation impossible, unlike floods and storms, which can often be anticipated thanks to weather forecasting systems.",
                    className='min-h-[900px]'
                )(DisasterPieChart(data)()),

                # Table
                Card(
                    id="table-card",
                    title="Deadliest disasters",
                    filters=[],
                    caption="   Note : The deadliest disasters are mainly earthquakes, floods, and storms, which cause the most deaths notably in 2010 with the devastating earthquake in Haiti. This table allows us to identify the most vulnerable regions and the types of disasters that have the greatest impact on human life.",
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

    for id in ["map-card", "temporal-card", "details-card", "stats-card", "pie-card", "table-card"]:
        register_card_callback(app, id)
