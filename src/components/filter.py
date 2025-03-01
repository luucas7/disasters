from typing import Any, Dict, List

from dash import dcc, html


class Filter:
    """Collection of reusable filter components with consistent styling."""
    
    def __init__(self, data: Any = None):
        self.data = data

    def dropdown_filter(self, id: str, label: str, options: List[Dict], value: Any = None) -> html.Div:
        """Create a styled dropdown filter."""
        return html.Div([
            html.Label(
                label,
                className="block text-base font-medium mb-2"
            ),
            dcc.Dropdown(
                id=id,
                options=options,
                clearable=False,
                value=value,
                className="rounded-md border-gray-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500",
                style={
                    'minWidth': '230px'
                },
                placeholder=f"Select {label.lower()}...",
            ),
        ], className="relative group") # Add group class for focus styles
    
    def disaster_filter(self, id: str) -> html.Div:
        """Create a disaster type filter dropdown."""
        return self.dropdown_filter(
            id=id,
            label="Disaster Type",
            options=self._get_disaster_options(),
            value="All"
        )
        
    def disaster_filter_without_all(self, id: str) -> html.Div:
        """Create a disaster type filter dropdown without 'All' option."""
        options = self._get_disaster_options(include_all=False)
        return self.dropdown_filter(
            id=id,
            label="Disaster Type",
            options=options,
            value=options[0]["value"] if options else None
        )

    def region_filter(self, id: str) -> html.Div:
        """Create a region filter dropdown."""
        return self.dropdown_filter(
            id=id,
            label="Region",
            options=self._get_region_options(),
            value="All"
        )

    def group_by_filter(self, id: str) -> html.Div:
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

    def temporal_impact_metric_filter(self, id: str) -> html.Div:
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
    
    def map_impact_metric_filter(self, id: str) -> html.Div:
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

    def _get_disaster_options(self, include_all: bool = True) -> List[Dict[str, str]]:
        """Get the list of disaster type options from the data.
        
        Returns:
            A list of dictionaries containing the disaster type options.
        """
        if self.data is not None:
            disasters = sorted(self.data["Disaster Type"].unique())
            options = [{"label": disaster, "value": disaster} for disaster in disasters]
            if include_all:
                options.insert(0, {"label": "All", "value": "All"})
            return options
        return []

    def _get_region_options(self) -> List[Dict[str, str]]:
        """Get the list of region options from the data.
        
        Returns:
            A list of dictionaries containing the region options.
        """
        if self.data is not None:
            regions = sorted(self.data["Region"].unique())
            return [{"label": "All", "value": "All"}] + [
                {"label": region, "value": region} for region in regions
            ]
        return []