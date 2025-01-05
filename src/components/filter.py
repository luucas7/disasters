from dash import html, dcc
from typing import Any, List, Dict

class Filter:
    """Collection of reusable filter components with enhanced styling."""
    
    def __init__(self, data: Any = None):
        self.data = data

    def dropdown_filter(self, id: str, label: str, options: List[Dict], value: Any = None) -> html.Div:
        """Create a styled dropdown filter."""
        return html.Div([
            html.Label(
                label,
                className="block text-base font-medium text-gray-700 mb-2"
            ),
            dcc.Dropdown(
                id=id,
                options=options,
                value=value,
                className="text-base",
                style={
                    'min-width': '230px'
                }
            ),
        ], className="mb-6")

    def disaster_filter(self):
        """Create a disaster type filter dropdown."""
        return self.dropdown_filter(
            id="disaster-type-filter",
            label="Disaster Type",
            options=self._get_disaster_options(),
            value="All"
        )

    def region_filter(self):
        """Create a region filter dropdown."""
        return self.dropdown_filter(
            id="region-filter",
            label="Region",
            options=self._get_region_options(),
            value="All"
        )

    def group_by_filter(self):
        """Create a group by filter dropdown."""
        return self.dropdown_filter(
            id="group-by-filter",
            label="Group By",
            options=[
                {"label": "Region", "value": "Region"},
                {"label": "Subregion", "value": "Subregion"},
                {"label": "Disaster Type", "value": "Disaster Type"},
            ],
            value="Region"
        )

    def impact_metric_filter(self):
        """Create an impact metric filter dropdown."""
        return self.dropdown_filter(
            id="impact-metric-filter",
            label="Impact Metric",
            options=[
                {"label": "Number of Disasters", "value": "count"},
                {"label": "Total Deaths", "value": "Total Deaths"},
                {"label": "Total Damage", "value": "Total Damage (in US$)"},
                {"label": "Affected people", "value": "Affected people"},
                {"label": "Insured Damage", "value": "Insured Damage (in US$)"},
            ],
            value="count"
        )

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