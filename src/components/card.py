from dash import html
from typing import List


class Card:
    """Base card component with consistent styling."""

    def __init__(self, title: str = "", filters: List = [], className: str = ""):
        self.title = title
        self.filters = filters
        self.className = className

    def __call__(self, children):
        return html.Div(
            [
                # Header avec style amélioré
                html.Div(
                    [
                        html.H3(self.title, className="text-lg font-semibold"),
                        html.Div(self.filters, className="flex flex-wrap gap-4 mt-3") if self.filters else None,
                    ],
                    className="p-4 border-b",
                )
                if self.title or self.filters
                else None,
                # Card content
                html.Div(children, className="p-4"),
            ],
            className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow duration-200 " + self.className,
        )