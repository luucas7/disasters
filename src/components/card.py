from dash import html, Dash
from typing import List, Optional
from dash.dependencies import Input, Output, State

class Card:
    """Base card component with consistent styling and fullscreen capability."""
    def __init__(self, id: str, title: str = "", caption: str="", filters: Optional[List] = None, className: str = ""):
        self.id = id
        self.title = title
        self.caption = caption
        self.filters = filters if filters is not None else []
        self.className = className

    def __call__(self, children: List[html.Div]) -> html.Div:
        
        return html.Div(
            [
                # Header avec style
                html.Div(
                    [
                        html.Div([
                            html.H3(self.title, className="text-lg font-semibold"),
                            html.P(self.caption, className="text-sm text-gray-500 italic ml-5 mt-2 mb-2") if self.caption else None,
                            html.Div(self.filters, className="flex flex-wrap gap-4 mt-4") if self.filters else None,
                        ], className="flex-1"),
                       
                        # Expand button
                        html.Button(
                            "🔍",
                            id=f"{self.id}-expand-btn",
                            className="p-2 hover:bg-gray-100 rounded transition-colors",
                            n_clicks=0
                        ),
                    ],
                    className="p-4 border-b border-gray-300 flex justify-between items-start",
                )
                if self.title
                else None,
                # Card content
                html.Div(children, className="p-4"),
            ],
            id=f"{self.id}-container",
            className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-all duration-300 " + self.className,
        )

def register_card_callback(app: Dash, id: str) -> None:
    """Register the fullscreen toggle callback."""

    @app.callback(
        Output(f"{id}-container", "className"),
        Input(f"{id}-expand-btn", "n_clicks"),
        State(f"{id}-container", "className"),
        prevent_initial_call=True
    )
    def toggle_card_fullscreen(n_clicks: Optional[int], current_className: str) -> str:
        
        if n_clicks is None:
            return current_className  # type: ignore[unreachable]
            
        if n_clicks % 2 == 1:  # Expand
            return current_className + " fixed inset-4 z-50 overflow-auto w-[calc(100%-2rem)]"
        else:  # Collapse
            return current_className.replace(" fixed inset-4 z-50 overflow-auto w-[calc(100%-2rem)]", "")