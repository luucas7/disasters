from dash import html
from typing import List
 

class Card:
    """Base card component with consistent styling."""

    def __init__(self, title: str = "", caption: str="", filters: List = [], className: str = ""):
        self.title = title
        self.caption = caption
        self.filters = filters
        self.className = className

    def __call__(self, children):
        return html.Div(
            [
                # Header avec style
                html.Div(
                    [
                        html.H3(self.title, className="text-lg font-semibold"),
                        html.P(self.caption, className="text-sm text-gray-500 italic ml-5 mt-2 mb-2") if self.caption else None,
                        html.Div(self.filters, className="flex flex-wrap gap-4 mt-4") if self.filters else None,
                    ],
                    className="p-4 border-b border-gray-300",
                )
                if self.title
                else None,
                # Card content
                html.Div(children, className="p-4"),
            ],
            className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow duration-200 " + self.className,
        )