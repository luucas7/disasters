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
                className="block text-base font-medium text-sage-700 mb-2"
            ),
            dcc.Dropdown(
                id=id,
                options=options,
                clearable=False,
                value=value,
                className="rounded-md border-sage-200 focus:border-sage-500 focus:ring-sage-500",
                style={
                    'min-width': '230px'
                },
                placeholder=f"Select {label.lower()}..."
            ),
        ], className="mb-6 relative group")  # group pour interactions
    
    def disaster_filter(self, id):
        """Create a disaster type filter dropdown."""
        return self.dropdown_filter(
            id=id,
            label="Disaster Type",
            options=self._get_disaster_options(),
            value="All"
        )

    def region_filter(self, id):
        """Create a region filter dropdown."""
        return self.dropdown_filter(
            id=id,
            label="Region",
            options=self._get_region_options(),
            value="All"
        )

    def group_by_filter(self, id):
        """Create a group by filter dropdown."""
        return self.dropdown_filter(
            id=id,
            label="Group By",
            options=[
                {"label": "Region", "value": "Region"},
                {"label": "Subregion", "value": "Subregion"},
                {"label": "Disaster Type", "value": "Disaster Type"},
            ],
            value="Region"
        )

    def temporal_impact_metric_filter(self, id):
        """Create an impact metric filter dropdown."""
        return self.dropdown_filter(
            id=id,
            label="Impact Metric",
            options=[
                {"label": "Number of Disasters", "value": "count"},
                {"label": "Total Deaths", "value": "Total Deaths"},
                {"label": "Affected people", "value": "Total Affected"},
                {"label": "Total Damage ($ USD)", "value": "Total Damage"},
                {"label": "Insured Damage ($ USD)", "value": "Insured Damage"},
                {"label": "Reconstruction Costs ($ USD)", "value": "Reconstruction Costs"},
            ],
            value="count"
        )
    
    def map_impact_metric_filter(self, id):
        """Create an impact metric filter dropdown."""
        return self.dropdown_filter(
            id=id,
            label="Impact Metric",
            options=[
                {"label": "Disaster density (/km²)", "value": "Density"},
                {"label": "Disaster count", "value": "Count"},
            ],
            value="Density"
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