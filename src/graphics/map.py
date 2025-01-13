import plotly.graph_objects as go
from dash.dependencies import Input, Output
from dash import dcc, html
from typing import Any, Dict
import numpy as np

class Map:
    def __init__(self, data, geojson):
        self.data = data
        self.geojson = geojson
        
    def create_figure(self, filtered_data=None):
        """Create choropleth map figure from data"""
        data_to_use = filtered_data if filtered_data is not None else self.data
        
        counts_by_country = data_to_use.groupby(['ISO','Country']).size().reset_index(name='Disaster_Count')
        counts_by_country['Scaled_Count'] = np.log10(counts_by_country['Disaster_Count'] + 1)
        
        fig = go.Figure(go.Choroplethmapbox(
            geojson=self.geojson,
            locations=counts_by_country['ISO'],
            z=counts_by_country['Scaled_Count'],
            featureidkey="properties.ISO_A3", 
            colorscale="Viridis",
            marker_opacity=0.5,
            marker_line_width=0,
            hovertemplate="<b>%{customdata[1]}</b><br>" +
                         "Number of disasters: %{customdata[0]:,}<extra></extra>",
            customdata=counts_by_country[['Disaster_Count','Country']].values
        ))

        fig.update_layout(
            mapbox_style="carto-positron",
            mapbox_zoom=1,
            mapbox_center={"lat": 20, "lon": 0},
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            autosize=True,
        )
        
        return fig

    def __call__(self):
        fig = self.create_figure()
        return html.Div([
            dcc.Loading(
                id="loading-map",
                type="default",
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

def register_map_callbacks(app, data, geojson):
    map_viz = Map(data, geojson)
    
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