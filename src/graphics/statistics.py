from typing import Any, List

import pandas as pd
from dash import html
from dash.dependencies import Input, Output


class Statistics:
    def __init__(self, data: pd.DataFrame = None):
        self.data = data
        self.layout = self._create_layout()

    def _create_layout(self) -> html.Div:
        return html.Div(
            [
                html.Div(
                    [
                        self._create_stat_box(
                            "Total Disasters",
                            id_prefix="total-disasters",
                            initial_value=len(self.data)
                            if self.data is not None
                            else 0,
                        ),
                        self._create_stat_box(
                            "Countries Affected",
                            id_prefix="affected-countries",
                            initial_value=self.data["Country"].nunique()
                            if self.data is not None
                            else 0,
                        ),
                        self._create_stat_box(
                            "Total Deaths",
                            id_prefix="total-deaths",
                            initial_value=self.data["Total Deaths"].sum()
                            if self.data is not None
                            else 0,
                        ),
                        self._create_stat_box(
                            "People Affected",
                            id_prefix="affected-people",
                            initial_value=self.data["Total Affected"].sum()
                            if self.data is not None
                            else 0,
                        ),
                    ],
                    id="stats-container",
                    className="grid grid-cols-2 gap-4",
                )
            ],
            id="stats-wrapper",
            className="p-4 bg-white rounded-lg shadow-sm",
            style={
                "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06)",
                "WebkitBoxShadow": "0 4px 6px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06)",  # Pour Chrome
            },
        )

    @staticmethod
    def _create_stat_box(
        title: str, id_prefix: str, initial_value: float = 0
    ) -> html.Div:
        return html.Div(
            [
                html.H3(title, className="text-sm font-medium text-gray-500"),
                html.P(
                    html.Span(
                        f"{initial_value:,.0f}",
                        id=f"{id_prefix}-value",
                        className="text-2xl font-semibold text-blue-600",
                    ),
                    className="mt-1",
                ),
            ],
            className="p-4 bg-white rounded-lg shadow-md border border-gray-300",
            style={
                "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06)",
                "WebkitBoxShadow": "0 4px 6px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06)",  # Pour Chrome
            },
        )

    def __call__(self) -> html.Div:
        return self.layout


def register_statistics_callbacks(app: Any, data: pd.DataFrame) -> None:
    @app.callback(
        Output("stats-container", "children"),
        [Input("start-year-filter", "value"), Input("end-year-filter", "value")],
    )
    def update_statistics(start_year: int, end_year: int) -> List[html.Div]:
        start_year = start_year if start_year is not None else data["Start Year"].min()
        end_year = end_year if end_year is not None else data["Start Year"].max()

        filtered_df = data[
            (data["Start Year"] >= start_year) & (data["Start Year"] <= end_year)
        ]

        stats = {
            "total_disasters": len(filtered_df),
            "total_deaths": filtered_df["Total Deaths"].sum(),
            "total_affected": filtered_df["Total Affected"].sum(),
            "countries": filtered_df["Country"].nunique(),
        }

        return [
            Statistics._create_stat_box(
                "Total Disasters", "total-disasters", stats["total_disasters"]
            ),
            Statistics._create_stat_box(
                "Countries Affected", "affected-countries", stats["countries"]
            ),
            Statistics._create_stat_box(
                "Total Deaths", "total-deaths", stats["total_deaths"]
            ),
            Statistics._create_stat_box(
                "People Affected", "affected-people", stats["total_affected"]
            ),
        ]
