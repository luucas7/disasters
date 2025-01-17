import plotly.graph_objects as go
from dash.dependencies import Input, Output
from dash import dcc, html
from typing import Any, Dict
import numpy as np
import pandas as pd

class Map:
    def __init__(self, data, geojson, areas):
        self.data = data
        self.geojson = geojson
        self.areas = areas
        
    def create_figure(self, filtered_data=None):
        """Create choropleth map figure from data"""
        data_to_use = filtered_data if filtered_data is not None else self.data
        
        counts_by_country = data_to_use.groupby(['ISO','Country']).size().reset_index(name='Disaster_Count')

        counts_by_country['Area'] = counts_by_country['ISO'].map(self.areas)
        
        # Calculate disasters per 1000 km²
        counts_by_country['Disaster_Density'] = (counts_by_country['Disaster_Count']) / counts_by_country['Area']

        # Apply cube root transformation to amplify small differences
        counts_by_country['Root_Density'] = np.cbrt(counts_by_country['Disaster_Density'])
        
        # Then apply min-max scaling on the transformed values
        min_density = counts_by_country['Root_Density'].min()
        max_density = counts_by_country['Root_Density'].max()
        counts_by_country['Scaled_Density'] = (counts_by_country['Root_Density'] - min_density) / (max_density - min_density)      

        fig = go.Figure(go.Choroplethmapbox(
            geojson=self.geojson,
            locations=counts_by_country['ISO'],
            z=counts_by_country['Scaled_Density'],
            featureidkey="properties.ISO_A3", 
            colorscale="Viridis",
            marker_opacity=0.5,
            marker_line_width=0,
            hovertemplate="<b>%{customdata[1]}</b><br>" +
                         "Number of disasters: %{customdata[0]:,}<br>" +
                         "Area: %{customdata[2]:,.2f} km²<br>" +
                         "Click for details<extra></extra>",
            customdata=counts_by_country[['Disaster_Count','Country','Area']].values,
            colorbar=dict(
                tickmode="array",
                thicknessmode="pixels",
                thickness=20,
                lenmode="pixels",
                len=300,
                xanchor="left",
                x=0.01,
            )
        ))

        fig.update_layout(
            mapbox_style="carto-positron",
            mapbox_zoom=1,
            mapbox_center={"lat": 20, "lon": 0},
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            autosize=True,
            clickmode='event+select'  # Enable click events
        )
        
        return fig

    def __call__(self):
        fig = self.create_figure()
        return html.Div([
            dcc.Loading(
                id="loading-map",
                type="circle",
                children=dcc.Graph(
                    figure=fig,
                    id="map",
                    config={
                        'doubleClick': 'reset+autosize',
                        'scrollZoom': True,
                        'displayModeBar': False
                    }
                )
            )
        ], className="w-full border-solid border-2")

def register_map_callbacks(app, data, geojson, areas):
    map_viz = Map(data, geojson, areas)
    
    @app.callback(
        Output('map', 'figure'),
        [
            Input('disaster-type-filter', 'value'),
            Input('region-filter', 'value'),
            Input('start-year-filter', 'value'),
            Input('end-year-filter', 'value')
        ]
    )
    def update_map(disaster_type, region, start_year, end_year):
        filtered_data = data.copy()
        
        # Apply filters
        if start_year is not None:
            filtered_data = filtered_data[filtered_data['Start Year'] >= start_year]
        if end_year is not None:
            filtered_data = filtered_data[filtered_data['Start Year'] <= end_year]
        if disaster_type and disaster_type != "All":
            filtered_data = filtered_data[filtered_data['Disaster Type'] == disaster_type]
        if region and region != "All":
            filtered_data = filtered_data[filtered_data['Region'] == region]
            
        return map_viz.create_figure(filtered_data)