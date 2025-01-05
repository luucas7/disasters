from dash import html, dcc
from typing import Any

class SideMenu:
    """Side menu component for global year filters."""
    
    def __init__(self, data: Any = None):
        self.data = data
        self.layout = self._create_layout()
    
    def _create_layout(self):
        min_year = int(self.data["Start Year"].min()) if self.data is not None else None
        max_year = int(self.data["Start Year"].max()) if self.data is not None else None
        
        return html.Div([
            html.Div([
                html.H2("Global Filters", className="text-lg font-semibold mb-4"),
                
                # Start Year filter
                html.Div([
                    html.Label(
                        "Start Year",
                        className="block text-sm font-medium text-gray-700",
                    ),
                    dcc.Dropdown(
                        id="start-year-filter",
                        options=self._get_year_options(),
                        value=min_year,
                        className="mt-1",
                    ),
                ], className="mb-4"),
                
                # End Year filter
                html.Div([
                    html.Label(
                        "End Year",
                        className="block text-sm font-medium text-gray-700",
                    ),
                    dcc.Dropdown(
                        id="end-year-filter",
                        options=self._get_year_options(),
                        value=max_year,
                        className="mt-1",
                    ),
                ], className="mb-4"),
            ], className="p-4")
        ], className="w-64 bg-white border-r border-gray-200 h-screen fixed left-0 top-16 overflow-y-auto")
    
    def _get_year_options(self):
        if self.data is not None:
            years = sorted(self.data["Start Year"].unique(), reverse=True)
            return [{"label": str(year), "value": year} for year in years]
        return []
        
    def __call__(self):
        return self.layout