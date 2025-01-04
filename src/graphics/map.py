import plotly.graph_objects as go
from dash.dependencies import Input, Output
from typing import Any, Dict
import numpy as np


def create_map(geojson, counts_by_country):
    return {
        "data": [{
            "type": "choroplethmapbox",
            "geojson": geojson,
            "locations": counts_by_country["Country"],
            "z": counts_by_country["Scaled_Count"],
            "featureidkey": "properties.ADMIN",
            "marker": {"opacity": 0.5, "line": {"width": 0}},
            "colorscale": "Viridis",
            "hovertemplate": "<b>%{location}</b><br>" +
                            "Disaster count: %{customdata}<br>" +
                            "<extra></extra>",
            "customdata": counts_by_country["Disaster_Count"],
        }],
        "layout": {
            "mapbox": {
                "style": "carto-positron",
                "zoom": 1,
                "center": {"lat": 20, "lon": 0},
            },
            "margin": {"r": 0, "t": 0, "l": 0, "b": 0},
            "autosize": True,
        }
    }
    
    
def register_callbacks(app, data, geojson):
    @app.callback(
        Output("main-map", "figure"),
        [
            Input("start-year-filter", "value"),
            Input("end-year-filter", "value"),
            Input("disaster-type-filter", "value"),
            Input("region-filter", "value"),
        ],
    )
    def update_map(
        start_year: int, end_year: int, disaster_type: str, region: str
    ) -> Dict[str, Any]:
        filtered_data = data.copy()

        # Use min/max values if no year is selected
        start_year = start_year if start_year is not None else int(data["Start Year"].min())
        end_year = end_year if end_year is not None else int(data["Start Year"].max())

        # Apply filters
        if disaster_type and disaster_type != "All":
            filtered_data = filtered_data[filtered_data["Disaster Type"] == disaster_type]

        if region and region != "All":
            filtered_data = filtered_data[filtered_data["Region"] == region]

        # Filter by start and end year
        filtered_data = filtered_data[
            (filtered_data["Start Year"] >= start_year)
            & (filtered_data["Start Year"] <= end_year)
        ]

        # Count number of disasters by country
        counts_by_country = (
            filtered_data.groupby("Country").size().reset_index(name="Disaster_Count")
        )

        # Use log scale for better color distribution
        counts_by_country["Scaled_Count"] = np.log10(
            counts_by_country["Disaster_Count"] + 1
        )

        return {
            "data": [
                {
                    "type": "choroplethmapbox",
                    "geojson": geojson,
                    "locations": counts_by_country["Country"],
                    "z": counts_by_country["Scaled_Count"],
                    "featureidkey": "properties.ADMIN",
                    "marker": {"opacity": 0.5, "line": {"width": 0}},
                    "colorscale": "Viridis",
                    "hovertemplate": "<b>%{location}</b><br>"
                    + "Disaster count: %{customdata}<br>"
                    + "<extra></extra>",
                    "customdata": counts_by_country["Disaster_Count"],
                }
            ],
            "layout": {
                "mapbox": {
                    "style": "carto-positron",
                    "zoom": 1,
                    "center": {"lat": 20, "lon": 0},
                },
                "margin": {"r": 0, "t": 0, "l": 0, "b": 0},
                "autosize": True,
            },
        }