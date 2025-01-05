import plotly.graph_objects as go
from dash import html, dcc
from dash.dependencies import Input, Output

def group_similar_disasters(data, group=False):
    if not group:
        return data
    
    groups = {
        'Mass Movement': ['Mass movement (dry)', 'Mass movement (wet)'],
        'Collapse': ['Collapse (Industrial)', 'Collapse (Miscellaneous)'],
        'Explosion': ['Explosion (Industrial)', 'Explosion (Miscellaneous)'],
        'Fire': ['Fire (Industrial)', 'Fire (Miscellaneous)'],
    }
    
    data_copy = data.copy()
    for group_name, disasters in groups.items():
        mask = data_copy['Disaster Type'].isin(disasters)
        if mask.any(): 
            data_copy.loc[mask, 'Disaster Type'] = group_name
    
    return data_copy
  
class DisasterPieChart:
    def __init__(self, data=None):
        self.data = data
        self.layout = html.Div([    
            # Légende placeholder        
            html.Div([
                dcc.Graph(
                    id='disaster-pie-legend',
                    style={'height': '100px'},
                    config={
                        'displayModeBar': False,
                        'displaylogo': False
                    }
                )
            ], className="w-full mb-5"),
            
            # Graphique principal
            html.Div([
                dcc.Graph(
                    id='disaster-pie-chart',
                    style={'height': '350px'},
                    config={
                        'displayModeBar': False,
                        'displaylogo': False
                    }
                )
            ], className="w-full")
        ], className="h-full flex flex-col")

    def __call__(self):
        return self.layout

def register_pie_callbacks(app, data):
    @app.callback(
        [Output('disaster-pie-chart', 'figure'),
         Output('disaster-pie-legend', 'figure')],
        [Input('group-similar-disasters', 'value'),
         Input('start-year-filter', 'value'),
         Input('end-year-filter', 'value')]
    )
    def update_pie(group_similar, start_year, end_year):
        start_year = start_year if start_year is not None else data['Start Year'].min()
        end_year = end_year if end_year is not None else data['Start Year'].max()
        
        filtered_data = data[
            (data['Start Year'] >= start_year) &
            (data['Start Year'] <= end_year)
        ]
        
        if group_similar and 'group' in group_similar:
            filtered_data = group_similar_disasters(filtered_data, True)
        
        counts = filtered_data['Disaster Type'].value_counts()
        
        # Figure principale avec pie chart sans légende
        pie_fig = go.Figure(
            data=[go.Pie(
                labels=counts.index,
                values=counts.values,
                textinfo='none',
                showlegend=False,
                textposition='auto',
                hole=0.4,
                marker=dict(
                    line=dict(color='white', width=2)
                )
            )],
            layout=dict(
                autosize=True,
                margin=dict(l=20, r=20, t=20, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
            )
        )
        
        # Figure pour la légende uniquement
        legend_fig = go.Figure(
            data=[go.Pie(
                labels=counts.index,
                values=counts.values,
                textinfo='none',
                showlegend=True,
                hole=1, # Rend le pie invisible
            )],
            layout=dict(
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="middle",
                    y=0.5,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=11),
                ),
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=100,
            )
        )

        return pie_fig, legend_fig