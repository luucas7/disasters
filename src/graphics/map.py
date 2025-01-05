import plotly.graph_objects as go
from dash.dependencies import Input, Output
from dash import dcc, html
from typing import Any, Dict
import numpy as np

class Map:
    def __init__(self, data, geojson):
        self.data = data
        self.geojson = geojson

    def __call__(self):
        counts_by_country = self.data.groupby('Country').size().reset_index(name='Disaster_Count')
        counts_by_country['Scaled_Count'] = np.log10(counts_by_country['Disaster_Count'] + 1)
        
        fig = go.Figure(go.Choroplethmapbox(
            geojson=self.geojson,
            locations=counts_by_country['Country'],
            z=counts_by_country['Scaled_Count'],
            featureidkey="properties.ADMIN",
            colorscale="Viridis",
            marker_opacity=0.5,
            marker_line_width=0
        ))

        fig.update_layout(
            mapbox_style="carto-positron",
            mapbox_zoom=1,
            mapbox_center={"lat": 20, "lon": 0},
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            autosize=True
        )
        
        return html.Div(dcc.Graph(figure=fig), style={'width': '100%', 'height': '500px'})

def register_map_callbacks(app, data, geojson):
    @app.callback(
        Output('map', 'figure'),
        [Input('some-input', 'value')]
    )
    def update_map(some_value):
        counts_by_country = data.groupby('Country').size().reset_index(name='Disaster_Count')
        counts_by_country['Scaled_Count'] = np.log10(counts_by_country['Disaster_Count'] + 1)
        
        fig = go.Figure(go.Choroplethmapbox(
            geojson=geojson,
            locations=counts_by_country['Country'],
            z=counts_by_country['Scaled_Count'],
            featureidkey="properties.ADMIN",
            colorscale="Viridis",
            marker_opacity=0.5,
            marker_line_width=0
        ))

        fig.update_layout(
            mapbox_style="carto-positron",
            mapbox_zoom=1,
            mapbox_center={"lat": 20, "lon": 0},
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            autosize=True
        )
        
        return fig