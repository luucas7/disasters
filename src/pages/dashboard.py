from dash import html
from dash.dependencies import Input, Output
from typing import Any, Dict

from src.components.navbar import Navbar
from src.components.filter import Filter
from src.components.main_content import MainContent

def create_dashboard_layout(data: Any, geojson: Dict[str, Any]) -> html.Div:
    """
    Create the main dashboard layout.
    
    Args:
        data: DataFrame containing the disaster data
        geojson: GeoJSON data for the map
    """
    return html.Div([
        # Main container with flex layout
        html.Div([
            Navbar()(),
            Filter(data)(),
            MainContent(data, geojson)()
        ], className="flex h-screen")
    ])

def init_callbacks(app: Any, data: Any, geojson: Dict[str, Any]) -> None:
    """
    Initialize dashboard callbacks.
    
    Args:
        app: Dash application instance
        data: DataFrame containing the disaster data
        geojson: GeoJSON data for the map
    """
    @app.callback(
        Output('main-map', 'figure'),
        [Input('year-filter', 'value'),
         Input('disaster-type-filter', 'value'),
         Input('region-filter', 'value')]
    )
    
    def update_map(year: int, disaster_type: str, region: str) -> Dict[str, Any]:
        filtered_data = data.copy()
        
        # Appliquer les filtres
        if disaster_type and disaster_type != 'All':
            filtered_data = filtered_data[filtered_data['Disaster Type'] == disaster_type]
            
        if region and region != 'All':
            filtered_data = filtered_data[filtered_data['Region'] == region]
        
        # Traitement différent selon si on veut toutes les années ou une année spécifique
        if year and year != 'All':
            # Pour une année spécifique
            filtered_data = filtered_data[filtered_data['Start Year'] == year]
            # Compter le nombre de catastrophes par pays
            counts_by_country = filtered_data.groupby('Country').size().reset_index(name='Disaster_Count')
        else:
            # Pour toutes les années, on somme le nombre total de catastrophes par pays
            counts_by_country = filtered_data.groupby('Country').size().reset_index(name='Disaster_Count')
            
        return {
            'data': [{
                'type': 'choroplethmapbox',
                'geojson': geojson,
                'locations': counts_by_country['Country'],
                'z': counts_by_country['Disaster_Count'],
                'featureidkey': "properties.ADMIN",
                'colorscale': "Viridis",
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