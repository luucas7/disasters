from typing import Any
from dash import dcc, html

class Navbar:
    """Navigation bar component with global year filters."""
    
    def __init__(self, data: Any = None):
        self.data = data
        self.layout = self._create_layout()
    
    def _create_layout(self) -> html.Div:
        """Create the layout for the navigation bar."""
        min_year = int(self.data["Start Year"].min()) if self.data is not None else None
        max_year = int(self.data["Start Year"].max()) if self.data is not None else None
        
        return html.Nav(
            html.Div([
                # Left side - Title and subtitle
                html.Div([
                    html.H1(
                        "Global Disasters Watch", 
                        className="text-xl font-bold text-white"
                    ),
                    html.P(
                        "Understanding disasters across time and space",
                        className="text-sm text-gray-300"
                    )
                ], className="flex flex-col"),

                # Center - Year filters
                html.Div([
                    # Start Year filter
                    html.Div([
                        html.Label(
                            "Start Year",
                            className="block text-sm font-medium text-white",
                        ),
                        dcc.Dropdown(
                            id="start-year-filter",
                            options=self._get_year_options(),
                            value=min_year,
                            className="w-32",
                        ),
                    ], className="mr-4"),
                    
                    # End Year filter
                    html.Div([
                        html.Label(
                            "End Year",
                            className="block text-sm font-medium text-white",
                        ),
                        dcc.Dropdown(
                            id="end-year-filter",
                            options=self._get_year_options(),
                            value=max_year,
                            className="w-32",
                        ),
                    ]),
                ], className="flex items-end")
                
            ], className="container mx-auto px-4 flex justify-between items-center h-full"),
            className="bg-blue-800 h-20 w-full fixed top-0 z-50 shadow-lg"
        )
    
    def _get_year_options(self) -> list:
        """Return a list of year options based on the data."""
        if self.data is not None:
            years = sorted(self.data["Start Year"].unique(), reverse=True)
            return [{"label": str(year), "value": year} for year in years]
        return []
        
    def __call__(self) -> html.Div:
        return self.layout