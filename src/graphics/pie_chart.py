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
            # Pie chart
            html.Div([
                dcc.Graph(
                    id='disaster-pie-chart',
                    style={},
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
        Output('disaster-pie-chart', 'figure'),
        [Input('group-similar-disasters', 'value'),
        Input('show-other', 'value'), 
        Input('start-year-filter', 'value'),
        Input('end-year-filter', 'value'),
        Input('show-country', 'value'),     
        Input('map', 'clickData')]
    )
    def update_pie(group_similar, show_other, start_year, end_year, show_country, clickData):
        start_year = start_year if start_year is not None else data['Start Year'].min()
        end_year = end_year if end_year is not None else data['Start Year'].max()
        
        filtered_data = data[
            (data['Start Year'] >= start_year) &
            (data['Start Year'] <= end_year)
        ]
        
        if show_country:
            country_iso = clickData['points'][0]['location'] if clickData else None
            if country_iso:
                filtered_data = filtered_data[filtered_data['ISO'] == country_iso]
            
        if group_similar and 'group' in group_similar:
            filtered_data = group_similar_disasters(filtered_data, True)
        
        counts = filtered_data['Disaster Type'].value_counts()

        if show_other and 'other' in show_other:
            other_mask = counts.rank(ascending=False) > 9
            if other_mask.any():
                others_sum = counts[other_mask].sum()
                counts = counts[~other_mask]
                counts['Others'] = others_sum

        text_infos = 'percent' if show_other else 'none'
        
        pie_fig = go.Figure(
            data=[go.Pie(
                labels=counts.index,
                values=counts.values,
                textinfo=text_infos,
                showlegend=True,
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
        
        return pie_fig