from typing import Any, Dict

import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output


class DisasterTreemap:
    """Treemap visualization component showing disaster impact by country."""
    
    def __init__(self, data: pd.DataFrame):
        """Initialize the treemap component."""
        self.data = data
        self.layout = html.Div([
            dcc.Loading(
                id="loading-treemap",
                type="circle",  
                children=dcc.Graph(
                    id='disaster-treemap',
                    style={'height': '600px'},
                    config={
                        'displayModeBar': False,
                        'displaylogo': False
                    }
                )
            )
        ], className="w-full")

    def create_figure(self, metric: str = "Total Deaths") -> Dict:
        """
        Create treemap figure from data.
        
        Args:
            metric: Impact metric to visualize (e.g., "Total Deaths", "Total Affected")
            
        Returns:
            Plotly figure dictionary
        """
        if self.data is None or len(self.data) == 0:
            return go.Figure().add_annotation(
                text="No data available for the selected filters, try other options!",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False
            )
            
        try:
            # Group data by disaster type and country
            if metric == "count":
                grouped = (self.data
                    .groupby(['Disaster Type', 'Country'])
                    .size()
                    .reset_index(name='value')
                )
            else:
                grouped = (self.data
                    .groupby(['Disaster Type', 'Country'])[metric]
                    .sum()
                    .reset_index(name='value')
                )
                
            if len(grouped) == 0 or grouped['value'].sum() == 0:
                return go.Figure().add_annotation(
                    text=f"No data available for {metric} with the selected filters",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False
                )
                
            # Sort by value and get top countries for each disaster type
            top_countries = []
            for disaster_type in grouped['Disaster Type'].unique():
                disaster_data = grouped[grouped['Disaster Type'] == disaster_type]
                top_n = disaster_data.nlargest(8, 'value')  # Get top 8 countries
                top_countries.append(top_n)
            
            final_data = pd.concat(top_countries)
            
            if metric == "count":
                labels = final_data.apply(
                    lambda x: f"{x['Country']} ({int(x['value'])} disasters)", 
                    axis=1
                )
            else:
                labels = final_data.apply(
                    lambda x: f"{x['Country']} ({x['value']:,.0f})", 
                    axis=1
                )
            
            # Create treemap
            fig = go.Figure(go.Treemap(
                labels=labels,
                parents=final_data['Disaster Type'],
                values=final_data['value'],
                branchvalues='total',
                textinfo='label',
                hovertemplate="""
                    Disaster Type: %{parent}<br>
                    Country: %{label}<br>
                    Impact: %{value:,.0f}<br>
                    <extra></extra>
                """,
                marker=dict(
                    colors=final_data['value'],
                    colorscale='Viridis',
                    showscale=True
                )
            ))
            
            # Update layout
            fig.update_layout(
                margin=dict(t=0, l=0, r=0, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            return fig
            
        except Exception as e:
            return go.Figure().add_annotation(
                text=f"Error processing data: {str(e)}",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False
            )

    def __call__(self) -> html.Div:
        """Render the component."""
        return self.layout


def register_treemap_callbacks(app: Any, data: pd.DataFrame) -> None:
    """
    Register callbacks for the treemap visualization.
    
    Args:
        app: Dash application instance
        data: Main DataFrame containing disaster data
    """
    @app.callback(
        Output('disaster-treemap', 'figure'),
        [
            Input('disaster-type-filter_without_all', 'value'),
            Input('treemap-region-filter', 'value'),
            Input('start-year-filter', 'value'),
            Input('end-year-filter', 'value'),
            Input('treemap-impact-metric-filter', 'value')
        ]
    )
    def update_treemap(disaster_type: str, region: str, 
                      start_year: int, end_year: int,
                      impact_metric: str) -> Dict[str, Any]:
                      
        # Create a local copy of the data for filtering
        filtered_data = data.copy()
        start_year = start_year if start_year is not None else filtered_data['Start Year'].min()
        end_year = end_year if end_year is not None else filtered_data['Start Year'].max()
        
        # Apply filters to the local copy
        filtered_data = filtered_data[
            (filtered_data['Start Year'] >= start_year) &
            (filtered_data['Start Year'] <= end_year)
        ]
        
        if disaster_type:  # Removed redundant check since using _without_all filter
            filtered_data = filtered_data[filtered_data['Disaster Type'] == disaster_type]
        if region and region != "All":
            filtered_data = filtered_data[filtered_data['Region'] == region]
            
        treemap = DisasterTreemap(filtered_data)
        return treemap.create_figure(impact_metric)