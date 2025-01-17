import plotly.graph_objects as go
from dash.dependencies import Input, Output
from dash import dcc, html
from typing import Any, Dict
import pandas as pd

class DisasterTable:
    def __init__(self, data: pd.DataFrame):
        self.data = data

    def simplify_location(self, location: str) -> str:
        """Simplify location string by taking only the first part before any comma or parenthesis.
        Stopping locations like "Port-au-prince, Kenscoff municipalities (Port-au-Prince district),
        Croix-des-Bouquets municipality..."
        """
        if pd.isna(location):
            return ""
        parts = location.split(',')[0].split('(')[0].strip()
        if len(parts) > 30:
            return parts[:27] + "..."
        return parts.strip()

    def create_figure(self, filtered_data: pd.DataFrame = None) -> go.Figure:
        """Create table figure from data"""
        data_to_use = filtered_data if filtered_data is not None else self.data

        # Process data: get worst disasters by total deaths
        worst_disasters = (data_to_use
            .sort_values('Total Deaths', ascending=False)
            .head(10)
            )
        
        # Prepare data for table with simplified location
        table_data = {
            'Year': worst_disasters['Start Year'],
            'Type': worst_disasters['Disaster Type'],
            'Country': worst_disasters['Country'],
            'Location': worst_disasters['Location'].apply(self.simplify_location),
            'Deaths': worst_disasters['Total Deaths'],
            'Damage ($M)': worst_disasters['Total Damage'].apply(lambda x: x/1000 if x != 0 else pd.NA)
        }

        fig = go.Figure(data=[go.Table(
            columnwidth=[50, 80, 100, 80, 70, 70], 
            header=dict(
                values=[f'<b>{col}</b>' for col in table_data.keys()],
                font=dict(size=12, color='white'),
                fill_color='rgb(0, 106, 178)',
                align=['center'] * 6,
                height=35
            ),
            cells=dict(
                values=[table_data[k] for k in table_data.keys()],
                font=dict(size=11),
                align=['center'] * 6,
                height=30,
                fill_color=[['white', 'rgb(245, 249, 253)'] * len(worst_disasters)],
                format=[None, None, None, None, ',', ',.0f']  # Number formatting
            )
        )])

        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            height=400,
            width=800,  # Fixed width to enable horizontal scroll
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            autosize=False,  # Disable autosize to enforce width
        )

        return fig

    def __call__(self):
        fig = self.create_figure()
        return html.Div([
            dcc.Loading(
                id="loading-table",
                type="circle",
                children=dcc.Graph(
                    figure=fig,
                    id="disaster-table",
                    config={
                        'displayModeBar': False,
                        'scrollZoom': False
                    },
                    style={
                        'width': '100%',
                        'minWidth': '800px'  # Minimum width to match figure width
                    }
                )
            )
        ], className="w-full overflow-x-auto")  # Enable horizontal scroll


def register_table_callbacks(app: Any, data: pd.DataFrame) -> None:
    """Register callbacks for the disaster table visualization."""
    table_viz = DisasterTable(data)

    @app.callback(
        Output('disaster-table', 'figure'),
        [
            Input('disaster-type-filter', 'value'),
            Input('region-filter', 'value'),
            Input('start-year-filter', 'value'),
            Input('end-year-filter', 'value')
        ]
    )
    def update_table(disaster_type: str, region: str, 
                    start_year: int, end_year: int) -> Dict[str, Any]:
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

        return table_viz.create_figure(filtered_data)