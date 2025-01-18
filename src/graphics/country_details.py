from typing import Optional

import pandas as pd
from dash import html
from dash.dependencies import Input, Output


class CountryDetails:
    """A component to display country-specific disaster details."""

    def __init__(self, data: Optional[pd.DataFrame] = None):
        self.data = data

    def create_disaster_row(
        self, disaster_type: str, count: int, percentage: float
    ) -> html.Div:
        """Create a single row for a disaster type."""
        return html.Div(
            [
                html.Div(
                    [
                        html.Span(disaster_type, className="text-gray-700"),
                        html.Div(
                            [
                                html.Span(f"{count:,}", className="font-medium"),
                                html.Span(
                                    f" ({percentage:.1f}%)",
                                    className="text-sm text-gray-500",
                                ),
                            ]
                        ),
                    ],
                    className="flex justify-between items-center py-2",
                )
            ],
            className="hover:bg-gray-50 px-4",
        )

    def create_details_content(
        self, country_iso: Optional[str], filtered_data: Optional[pd.DataFrame] = None
    ) -> html.Div:
        """Create the content for country details."""
        if not country_iso:
            return html.Div(
                "Select a country on the map to see details",
                className="text-gray-500 italic text-center p-4",
            )

        data_to_use = filtered_data if filtered_data is not None else self.data
        if data_to_use is None:
            return html.Div(
                "No data available", className="text-gray-500 italic text-center p-4"
            )

        country_data = data_to_use[data_to_use["ISO"] == country_iso]

        if len(country_data) == 0:
            return html.Div(
                "No disasters recorded for selected filters",
                className="text-gray-500 italic text-center p-4",
            )

        country_name = country_data["Country"].iloc[0]
        disaster_counts = country_data["Disaster Type"].value_counts()
        total_disasters = disaster_counts.sum()

        # Create disaster rows sorted by count
        disaster_rows = []
        for disaster_type, count in disaster_counts.sort_values(
            ascending=False
        ).items():
            percentage = (count / total_disasters) * 100
            disaster_rows.append(
                self.create_disaster_row(disaster_type, count, percentage)
            )

        return html.Div(
            [
                # Header
                html.Div(
                    [
                        html.H3(
                            f"Details for {country_name}",
                            className="text-lg font-semibold text-gray-800",
                        ),
                        html.Div(
                            f"Total Disasters: {total_disasters:,}",
                            className="text-sm text-gray-600",
                        ),
                    ],
                    className="px-4 py-3 bg-gray-50 border-b",
                ),
                # Content
                html.Div(
                    disaster_rows,
                    className="divide-y divide-gray-100 overflow-y-auto max-h-96",
                ),
            ],
            className="bg-white rounded-lg shadow-sm w-full",
        )

    def __call__(self) -> html.Div:
        """Render the component."""
        return html.Div(id="country-details-content", className="h-full")


def register_details_callbacks(app, data):
    """Register callbacks for the details card."""

    @app.callback(
        Output("country-details-content", "children"),
        [
            Input("map", "clickData"),
            Input("disaster-type-filter", "value"),
            Input("region-filter", "value"),
            Input("start-year-filter", "value"),
            Input("end-year-filter", "value"),
        ],
    )
    def update_details(clickData, disaster_type, region, start_year, end_year):
        filtered_data = data.copy()

        # Apply filters
        if start_year is not None:
            filtered_data = filtered_data[filtered_data["Start Year"] >= start_year]
        if end_year is not None:
            filtered_data = filtered_data[filtered_data["Start Year"] <= end_year]
        if region and region != "All":
            filtered_data = filtered_data[filtered_data["Region"] == region]

        # Create details content
        details = CountryDetails(data)
        country_iso = clickData["points"][0]["location"] if clickData else None

        return details.create_details_content(country_iso, filtered_data)
