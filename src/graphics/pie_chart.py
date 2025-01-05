import plotly.graph_objects as go
from dash import html, dcc
from dash.dependencies import Input, Output

class DisasterPieChart:
    def __init__(self, data=None):
        self.data = data
        self.layout = html.Div([            
            
            # Graph container
            html.Div([
                dcc.Graph(
                    id='disaster-pie-chart',
                    style={'height': '600px'}, 
                    config={
                        'displayModeBar': False,
                        'displaylogo': False
                    }
                )
            ], className="w-full p-4")
        ], className="h-full flex flex-col")

    def __call__(self):
        return self.layout


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
  
  
def register_pie_callbacks(app, data):
    @app.callback(
        Output('disaster-pie-chart', 'figure'),
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
        
        return go.Figure(
            data=[go.Pie(
                labels=counts.index,
                values=counts.values,
                textinfo='percent',
                showlegend=True,
                textposition='auto',
                hole=0.4,  # Adds a donut hole
                marker=dict(
                    line=dict(color='white', width=2)  # Adds white borders between sections
                )
            )],
            layout=dict(
                autosize=True,
                height=500,
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="right",
                    x=1.1,
                    font=dict(size=12),
                    bgcolor='rgba(255, 255, 255, 0.8)',
                    bordercolor='rgba(0, 0, 0, 0.1)',
                    borderwidth=1
                ),
                margin=dict(r=150, t=30, l=30, b=30),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
            )
        )