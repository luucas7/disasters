from dash import html, dcc
from typing import Any

class Filter:
    """Filter sidebar component."""
    
    def __init__(self, data: Any = None):
        self.data = data
        self.layout = html.Div([
            html.Div([
                html.H2("Filtres", className="text-lg font-semibold mb-4"),
                
                # Year filter
                html.Div([
                    html.Label("Année", className="block text-sm font-medium text-gray-700"),
                    dcc.Dropdown(
                        id='year-filter',
                        options=self._get_year_options() if self.data is not None else [],
                        value='All',
                        className="mt-1"
                    )
                ], className="mb-4"),
                
                # Disaster type filter
                html.Div([
                    html.Label("Disaster type", 
                             className="block text-sm font-medium text-gray-700"),
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
                
            ], className="p-4")
        ], className="w-64 bg-white border-r border-gray-200 h-screen fixed left-0 top-16 overflow-y-auto")
    
    def _get_year_options(self):
        if self.data is not None:
            years = sorted(self.data['Start Year'].unique(), reverse=True)
            return [{'label': 'All', 'value': 'All'}] + [{'label': str(year), 'value': year} for year in years]
        return []
    
    def _get_max_year(self):
        if self.data is not None:
            return self.data['Start Year'].max()
        return None
    
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