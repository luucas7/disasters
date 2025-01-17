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
        
    def create_figure(self, filtered_data=None, impact_metric="Density"):
        """Create choropleth map figure from data"""
        data_to_use = filtered_data if filtered_data is not None else self.data
        
        counts_by_country = data_to_use.groupby(['ISO','Country']).size().reset_index(name='Disaster_Count')
        counts_by_country['Area'] = counts_by_country['ISO'].map(self.areas)
        
        if impact_metric == "Density":
            # Calculate disasters per 1000 km²
            counts_by_country['Disaster_Density'] = (counts_by_country['Disaster_Count']) / counts_by_country['Area']
            # Apply cube root transformation to amplify small differences
            counts_by_country['Display_Value'] = np.cbrt(counts_by_country['Disaster_Density'])
        else:  # Count
            counts_by_country['Display_Value'] = np.log10(counts_by_country['Disaster_Count'] + 1)
        
        # Min-max scaling for the display value
        min_val = counts_by_country['Display_Value'].min()
        max_val = counts_by_country['Display_Value'].max()
        counts_by_country['Scaled_Value'] = (counts_by_country['Display_Value'] - min_val) / (max_val - min_val)

        fig = go.Figure(go.Choroplethmapbox(
            geojson=self.geojson,
            locations=counts_by_country['ISO'],
            z=counts_by_country['Scaled_Value'],
            featureidkey="properties.ISO_A3", 
            colorscale="Viridis",
            marker_opacity=0.5,
            marker_line_width=0,
            hovertemplate="<b>%{customdata[1]}</b><br><br>" +
                         "Number of disasters: %{customdata[0]:,}<br>" +
                         "Area: %{customdata[2]:,.2f} km²<br>" +
                         "Click for details<extra></extra>",
            customdata=counts_by_country[['Disaster_Count', 'Country', 'Area']].values,
            colorbar=dict(
                title=dict(
                    side='right'
                ),
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
            Input('end-year-filter', 'value'),
            Input('map-impact-metric-filter', 'value')
        ]
    )
    def update_map(disaster_type, region, start_year, end_year, impact_metric):
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
            
        return map_viz.create_figure(filtered_data, impact_metric)