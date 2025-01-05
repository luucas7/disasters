from dash import html, dcc
from typing import Any

class Filter:
    """Collection of reusable filter components."""
    
    def __init__(self, data: Any = None):
        self.data = data

    def disaster_filter(self):
        """Create a disaster type filter dropdown."""
        return html.Div([
            html.Label(
                "Disaster Type",
                className="block text-sm font-medium text-gray-700",
            ),
            dcc.Dropdown(
                id="disaster-type-filter",
                options=self._get_disaster_options(),
                value="All",
                className="mt-1",
            ),
        ], className="mb-4")

    def region_filter(self):
        """Create a region filter dropdown."""
        return html.Div([
            html.Label(
                "Region",
                className="block text-sm font-medium text-gray-700",
            ),
            dcc.Dropdown(
                id="region-filter",
                options=self._get_region_options(),
                value="All",
                className="mt-1",
            ),
        ], className="mb-4")

    def group_by_filter(self):
        """Create a group by filter dropdown."""
        return html.Div([
            html.Label(
                "Group By",
                className="block text-sm font-medium text-gray-700",
            ),
            dcc.Dropdown(
                id="group-by-filter",
                options=[
                    {"label": "Region", "value": "Region"},
                    {"label": "Subregion", "value": "Subregion"},
                    {"label": "Disaster Type", "value": "Disaster Type"},
                ],
                value="Region",
                className="mt-1",
            ),
        ], className="mb-4")

    def impact_metric_filter(self):
        """Create an impact metric filter dropdown."""
        return html.Div([
            html.Label(
                "Impact Metric",
                className="block text-sm font-medium text-gray-700",
            ),
            dcc.Dropdown(
                id="impact-metric-filter",
                options=[
                    {"label": "Number of Disasters", "value": "count"},
                    {"label": "Total Deaths", "value": "Total Deaths"},
                    {"label": "Total Damage", "value": "Total Damage (in US$)"},
                    {"label": "Affected people", "value": "Affected people"},
                    {"label": "Insured Damage", "value": "Insured Damage (in US$)"},
                ],
                value="count",
                className="mt-1",
            ),
        ], className="mb-4")

    def _get_disaster_options(self):
        if self.data is not None:
            disasters = sorted(self.data["Disaster Type"].unique())
            return [{"label": "All", "value": "All"}] + [
                {"label": disaster, "value": disaster} for disaster in disasters
            ]
        return []

    def _get_region_options(self):
        if self.data is not None:
            regions = sorted(self.data["Region"].unique())
            return [{"label": "All", "value": "All"}] + [
                {"label": region, "value": region} for region in regions
            ]
        return []