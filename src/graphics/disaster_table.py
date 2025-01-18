from typing import Any

import dash_ag_grid as dag
import pandas as pd
from dash import html
from dash.dependencies import Input, Output


class DisasterTable:
    """Disaster table visualization component."""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.column_defs = [
            {
                "field": "Year",
                "headerName": "Year",
                "filter": "agNumberColumnFilter",
                "sortable": True,
                "width": 100,
                "headerClass": "text-blue-600",
            },
            {
                "field": "Type",
                "headerName": "Disaster Type",
                "filter": True,
                "sortable": True,
                "width": 150,
                "headerClass": "text-blue-600",
            },
            {
                "field": "Country",
                "headerName": "Country",
                "filter": True,
                "sortable": True,
                "width": 140,
                "headerClass": "text-blue-600",
            },
            {
                "field": "Location",
                "headerName": "Location",
                "filter": True,
                "sortable": True,
                "width": 180,
                "headerClass": "text-blue-600",
            },
            {
                "field": "Deaths",
                "headerName": "Deaths",
                "filter": "agNumberColumnFilter",
                "sortable": True,
                "type": "numericColumn",
                "width": 120,
                "headerClass": "text-blue-600",
            },
            {
                "field": "Damage",
                "headerName": "Damage ($M)",
                "filter": "agNumberColumnFilter",
                "sortable": True,
                "type": "numericColumn",
                "width": 140,
                "headerClass": "text-blue-600",
            },
        ]

    def simplify_location(self, location: str) -> str:
        """Simplify location string by taking only the first part before any comma or parenthesis.
        To avoid values over extending"""
        if pd.isna(location):
            return "" # type: ignore[unreachable]
        parts = location.split(",")[0].split("(")[0].strip()
        if len(parts) > 30:
            return parts[:27] + "..."
        return parts.strip()

    def prepare_table_data(self, filtered_data: pd.DataFrame) -> list:
        """Prepare data for AG Grid table"""
        data_to_use = filtered_data if not filtered_data.empty else self.data

        # Process data: get deadliest disasters
        worst_disasters = data_to_use.sort_values("Total Deaths", ascending=False).head(
            50
        )

        # Prepare data for table
        return [
            {
                "Year": int(row["Start Year"]),
                "Type": row["Disaster Type"],
                "Country": row["Country"],
                "Location": self.simplify_location(row["Location"]),
                "Deaths": int(row["Total Deaths"])
                if pd.notna(row["Total Deaths"])
                else 0,
                "Damage": float(row["Total Damage"]) / 1000
                if pd.notna(row["Total Damage"]) and row["Total Damage"] != 0
                else None,
            }
            for _, row in worst_disasters.iterrows()
        ]

    def __call__(self) -> html.Div:
        table_data = self.prepare_table_data(pd.DataFrame())
        return html.Div(
            [
                dag.AgGrid(
                    id="disaster-table",
                    columnDefs=self.column_defs,
                    rowData=table_data,
                    columnSize="sizeToFit",
                    defaultColDef={
                        "resizable": True,
                        "sortable": True,
                        "filter": True,
                        "minWidth": 100,
                    },
                    dashGridOptions={
                        "pagination": True,
                        "paginationAutoPageSize": True,
                        "animateRows": True,
                    },
                    className="ag-theme-alpine",
                    style={"height": "500px", "width": "100%"},
                )
            ],
            className="w-full",
        )


def register_table_callbacks(app: Any, data: pd.DataFrame) -> None:
    """Register callbacks for the disaster table visualization."""
    table_viz = DisasterTable(data)

    @app.callback(
        Output("disaster-table", "rowData"),
        [
            Input("start-year-filter", "value"),
            Input("end-year-filter", "value"),
        ],
    )
    def update_table(
        start_year: int, end_year: int
    ) -> list[dict[str, Any]]:
        filtered_data = data.copy()

        # Apply filters
        if start_year is not None:
            filtered_data = filtered_data[filtered_data["Start Year"] >= start_year]
        if end_year is not None:
            filtered_data = filtered_data[filtered_data["Start Year"] <= end_year]

        return table_viz.prepare_table_data(filtered_data)
