from dash import dcc, html
import pandas as pd
from typing import Dict, Any

def Map(data: pd.DataFrame, geojson: Dict[str, Any]) -> html.Div:
    """
    Create a Plotly map component with polygons.
    
    Args:
        data: DataFrame containing the data to be displayed on the map
        geojson: GeoJSON data for the polygons
    
    Returns:
        A Dash HTML component containing the map
    """
    return html.Div(
        dcc.Graph(
            id='main-map',
            figure={
                'data': [{
                    'type': 'choroplethmapbox',
                    'geojson': geojson,
                    'locations': data['Country'],
                    'z': data['Total Affected'],
                    'featureidkey': "properties.ADMIN",
                    'colorscale': "Viridis",
                    'marker': {
                        'opacity': 0.5,
                        'line': {'width': 0}
                    }
                }],
                'layout': {
                    'mapbox': {
                        'style': "carto-positron",
                        'zoom': 1,
                        'center': {"lat": 20, "lon": 0}
                    },
                    'margin': {"r":0,"t":0,"l":0,"b":0},
                    'autosize': True,
                }
            },
            style={'height': 'calc(100vh - 64px)', 'width': '100%'}
        ),
        style={'height': 'calc(100vh - 64px)', 'width': '100%'}
    )