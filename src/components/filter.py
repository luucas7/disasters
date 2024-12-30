from dash import html, dcc
from typing import Any, List

class Filter:
    """Filter sidebar component."""
    
    def __init__(self, data: Any = None, view_type: str = "map"):
        self.data = data
        self.view_type = view_type
        self.layout = self._create_layout()
    
    def _create_layout(self):
        filters = []
        
        # Get min and max years
        min_year = int(self.data['Start Year'].min()) if self.data is not None else None
        max_year = int(self.data['Start Year'].max()) if self.data is not None else None
        
        # Common filters
        filters.extend([
            # Start Year filter
            html.Div([
                html.Label("Start Year", className="block text-sm font-medium text-gray-700"),
                dcc.Dropdown(
                    id='start-year-filter',
                    options=self._get_year_options() if self.data is not None else [],
                    value=min_year,
                    className="mt-1"
                )
            ], className="mb-4"),
            
            # End Year filter
            html.Div([
                html.Label("End Year", className="block text-sm font-medium text-gray-700"),
                dcc.Dropdown(
                    id='end-year-filter',
                    options=self._get_year_options() if self.data is not None else [],
                    value=max_year,
                    className="mt-1"
                )
            ], className="mb-4"),
        ])
        
        if self.view_type == "map":
            # Map specific filters
            filters.extend([
                # Disaster type filter
                html.Div([
                    html.Label("Disaster type", className="block text-sm font-medium text-gray-700"),
                    dcc.Dropdown(
                        id='disaster-type-filter',
                        options=self._get_disaster_options() if self.data is not None else [],
                        value='All',
                        className="mt-1"
                    )
                ], className="mb-4"),
                
                # Region filter
                html.Div([
                    html.Label("Region", className="block text-sm font-medium text-gray-700"),
                    dcc.Dropdown(
                        id='region-filter',
                        options=self._get_region_options() if self.data is not None else [],
                        value='All',
                        className="mt-1"
                    )
                ], className="mb-4"),
            ])
        
        elif self.view_type == "time":
            # Time visualization specific filters
            filters.extend([
                # Group by filter
                html.Div([
                    html.Label("Group by", className="block text-sm font-medium text-gray-700"),
                    dcc.Dropdown(
                        id='group-by-filter',
                        options=[
                            {'label': 'Region', 'value': 'Region'},
                            {'label': 'Subregion', 'value': 'Subregion'},
                            {'label': 'Disaster Type', 'value': 'Disaster Type'},
                        ],
                        value='Region',
                        className="mt-1"
                    )
                ], className="mb-4"),
                
                # Impact metric filter
                html.Div([
                    html.Label("Impact Metric", className="block text-sm font-medium text-gray-700"),
                    dcc.Dropdown(
                        id='impact-metric-filter',
                        options=[
                            {'label': 'Number of Disasters', 'value': 'count'},
                            {'label': 'Total Deaths', 'value': 'Total Deaths'},
                            {'label': 'Total Damage', 'value': 'Total Damage (in US$)'},
                            {'label': 'Affected people', 'value': 'Affected people'},
                            {'label': 'Insured Damage', 'value': 'Insured Damage (in US$)'}
                        ],
                        value='count',
                        className="mt-1"
                    )
                ], className="mb-4"),
            ])
        
        return html.Div([
            html.Div([
                html.H2("Filters", className="text-lg font-semibold mb-4"),
                *filters
            ], className="p-4")
        ], className="w-64 bg-white border-r border-gray-200 h-screen fixed left-0 top-16 overflow-y-auto")

    def _get_year_options(self):
        if self.data is not None:
            years = sorted(self.data['Start Year'].unique(), reverse=True)
            return [{'label': str(year), 'value': year} for year in years]
        return []
    
    def _get_disaster_options(self):
        if self.data is not None:
            disasters = sorted(self.data['Disaster Type'].unique())
            return [{'label': 'All', 'value': 'All'}] + [
                {'label': disaster, 'value': disaster} for disaster in disasters
            ]
        return []
    
    def _get_region_options(self):
        if self.data is not None:
            regions = sorted(self.data['Region'].unique())
            return [{'label': 'All', 'value': 'All'}] + [
                {'label': region, 'value': region} for region in regions
            ]
        return []

    def __call__(self):
        return self.layout