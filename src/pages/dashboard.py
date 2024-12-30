from dash import html, dcc
from dash.dependencies import Input, Output
from typing import Any, Dict
import numpy as np

from src.components.navbar import Navbar
from src.components.filter import Filter
from src.components.main_content import MainContent
from src.components.time_visualization import TimeVisualization


def create_dashboard_layout(data: Any, geojson: Dict[str, Any]) -> html.Div:
    """
    Create the main dashboard layout.
    
    Args:
        data: DataFrame containing the disaster data
        geojson: GeoJSON data for the map
    """
    return html.Div([
        dcc.Location(id='url', refresh=False),
        Navbar()(),
        html.Div(id='page-content', className="flex h-screen"),
        dcc.Store(id='current-view', data='map')
    ])

def init_callbacks(app: Any, data: Any, geojson: Dict[str, Any]) -> None:
    """Initialize dashboard callbacks."""
    
    # Set suppress_callback_exceptions to True
    app.config.suppress_callback_exceptions = True
    # éviter les erreurs lorsque Dash ne peut pas initialement trouver tous les composants d'un callback. nécessaire avec un système de routage car certains composants n'existent que dans certaines pages/

    @app.callback(
        Output('page-content', 'children'),
        [Input('url', 'pathname')]
    )
    def display_page(pathname):
        view_type = 'map' if pathname == '/map' else 'time' if pathname == '/time' else 'about'
        
        # Create components
        filter_component = Filter(data, view_type)
        main_content = MainContent(data, geojson, view_type)
        
        # Return their layouts directly
        return [
            filter_component.layout,
            main_content.layout
        ]

    @app.callback(
        Output('main-map', 'figure'),
        [Input('start-year-filter', 'value'),
         Input('end-year-filter', 'value'),
         Input('disaster-type-filter', 'value'),
         Input('region-filter', 'value')]
    )
    def update_map(start_year: int, end_year: int, disaster_type: str, region: str) -> Dict[str, Any]:
        filtered_data = data.copy()
        
        # Appliquer les filtres
        if disaster_type and disaster_type != 'All':
            filtered_data = filtered_data[filtered_data['Disaster Type'] == disaster_type]
            
        if region and region != 'All':
            filtered_data = filtered_data[filtered_data['Region'] == region]
        
        # Filtrer par année de début et de fin
        filtered_data = filtered_data[
            (filtered_data['Start Year'] >= start_year) & 
            (filtered_data['Start Year'] <= end_year)
        ]
            
        # Compter le nombre de catastrophes par pays
        counts_by_country = filtered_data.groupby('Country').size().reset_index(name='Disaster_Count')
        counts_by_country['Scaled_Count'] = np.log10(counts_by_country['Disaster_Count'] + 1)  # +1 pour éviter log(0)
            
        return {
            'data': [{
                'type': 'choroplethmapbox',
                'geojson': geojson,
                'locations': counts_by_country['Country'],
                'z': counts_by_country['Disaster_Count'],
                'featureidkey': "properties.ADMIN", # Custom selon le fichier geojson
                'colorscale': "Jet",
                'marker': {
                    'opacity': 0.5,
                    'line': {'width': 0}
                },
                'hovertemplate': "<b>%{location}</b><br>" +
                                "Disaster count: %{z}<br>" +
                                "<extra></extra>"
            }],
            'layout': {
                'mapbox': {
                    'style': "carto-positron",
                    'zoom': 1,
                    'center': {"lat": 20, "lon": 0}
                },
                'margin': {"r":0,"t":0,"l":0,"b":0},
                'autosize': True
            }
        }

    @app.callback(
        Output('time-series-chart', 'figure'),
        [Input('start-year-filter', 'value'),
         Input('end-year-filter', 'value'),
         Input('group-by-filter', 'value'),
         Input('impact-metric-filter', 'value')]
    )
    def update_time_series(start_year: int, end_year: int, group_by: str, metric: str) -> Dict[str, Any]:
        # Filter data by year range
        filtered_data = data[
            (data['Start Year'] >= start_year) & 
            (data['Start Year'] <= end_year)
        ].copy()
        
        # Create visualization
        time_viz = TimeVisualization(filtered_data)
        return time_viz.create_figure(group_by, metric)