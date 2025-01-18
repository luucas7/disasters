from typing import List

from dash import dcc, html


class Checkbox:
    """Reusable checkbox component with consistent styling."""
    
    def __init__(self, 
                 id: str,
                 options: List[dict],
                 value: List[str]):
        self.id = id
        self.options = options
        self.value = value if value is not None else []

    def __call__(self) -> html.Div:
        return html.Div([
            dcc.Checklist(
                id=self.id,
                options=self.options,
                value=self.value,
                className="space-y-2",
                inputClassName="w-4 h-4 mr-2 text-blue-600 border-gray-300 rounded focus:ring-blue-500",
                labelClassName="text-sm text-gray-700",
                labelStyle={"display": "flex", "alignItems": "center"}
            )
        ], className="mb-4")