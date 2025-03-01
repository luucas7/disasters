from typing import Any, Dict

import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, Dash
from dash.dependencies import Input, Output


class TimedCount:
    """Time series visualization component."""

    def __init__(self, data: Any = None) -> None:
        self.data = data
        self.layout = html.Div(
            [
                dcc.Graph(
                    responsive=True,
                    id="time-series-chart",
                    style={"width": "95%", "height": "300px"},
                    config={
                        "displayModeBar": False,
                    },
                )
            ],
            className="flex-1 ml-16",
        )

    def create_figure(self, group_by: str = "Region", metric: str = "count") -> Dict:
        """
        Create the time series histogram.

        Args:
            group_by: Column to group by ('Region', 'Disaster Type', or 'Subregion')
            metric: Impact metric (variable) to display ('count', 'Total Damage', etc.)
        """
        if self.data is None:
            return {}

        # Group data by year and group_by column
        if metric == "count":
            grouped = (
                self.data.groupby(["Start Year", group_by])
                .size()
                .reset_index(name="Count")
            )
            y_title = "Number of disasters"
        else:
            grouped = (
                self.data.groupby(["Start Year", group_by])[metric].sum().reset_index()
            )
            y_title = metric

        # Create figure
        fig = go.Figure()

        # Add traces for each category
        for category in sorted(grouped[group_by].unique()):
            df_filtered = grouped[grouped[group_by] == category]

            fig.add_trace(
                go.Bar(
                    name=category,
                    x=df_filtered["Start Year"],
                    y=df_filtered["Count"]
                    if metric == "count"
                    else df_filtered[metric],
                    hovertemplate=(
                        f"{group_by}: {category}<br>"
                        + "Year: %{x}<br>"
                        + f"{y_title}: %{{y:,.0f}}<br>"
                        + "<extra></extra>"
                    ),
                )
            )

        # Update layout
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title=y_title,
            barmode="stack",
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02,
                bgcolor="white",
                bordercolor="gray",
                borderwidth=1,
            ),
            margin=dict(l=50, r=100, t=30, b=30),
            hovermode="closest",
        )

        return fig

    def __call__(self) -> html.Div:
        return self.layout


def register_timed_count_callbacks(app: Dash, data: pd.DataFrame) -> None:
    @app.callback(
        Output("time-series-chart", "figure"),
        [
            Input("start-year-filter", "value"),
            Input("end-year-filter", "value"),
            Input("group-by-filter", "value"),
            Input("temporal-impact-metric-filter", "value"),
        ],
    )
    def update_time_series(
        start_year: int, end_year: int, group_by: str, metric: str
    ) -> Dict[str, Any]:
        # Use min/max values if no year is selected
        start_year = (
            start_year if start_year is not None else int(data["Start Year"].min())
        )
        end_year = end_year if end_year is not None else int(data["Start Year"].max())

        # Filter data by year range
        filtered_data = data[
            (data["Start Year"] >= start_year) & (data["Start Year"] <= end_year)
        ].copy()

        # Create visualization
        time_viz = TimedCount(filtered_data)
        return time_viz.create_figure(group_by, metric)
