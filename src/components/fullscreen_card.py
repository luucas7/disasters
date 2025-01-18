from dash import html, Dash    
from typing import List, Optional

class FullscreenCard:
    """Base card component with consistent styling and fullscreen capability."""
    
    def __init__(self, 
                 title: str = "", 
                 caption: str = "", 
                 filters: Optional[List] = None, 
                 className: str = "",
                 id: Optional[str] = None):
        self.title = title
        self.caption = caption
        self.filters = filters if filters is not None else []
        self.className = className
        self.id = id if id is not None else f"card-{title.lower().replace(' ', '-')}"

    def __call__(self, children: List[html.Div]) -> html.Div:
        # Container div with conditional classes
        return html.Div(
            id={"type": "card-container", "index": self.id},
            className=f"bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow duration-200 relative {self.className}",
            children=[
                # Header section
                html.Div([
                    # Title and caption container
                    html.Div([
                        html.H3(self.title, className="text-lg font-semibold"),
                        html.P(self.caption, className="text-sm text-gray-500 italic ml-5") if self.caption else None,
                        html.Div(self.filters, className="flex flex-wrap gap-4 mt-4") if self.filters else None,
                    ], className="flex-1"),
                    
                    # Fullscreen toggle button
                    html.Button([
                        # Maximize icon (shown when not fullscreen)
                        html.I(className="fas fa-expand hidden", id={"type": "maximize-icon", "index": self.id}),
                        # Minimize icon (shown when fullscreen)
                        html.I(className="fas fa-compress", id={"type": "minimize-icon", "index": self.id}),
                    ],
                    id={"type": "fullscreen-button", "index": self.id},
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200"
                    )
                ],
                className="p-4 border-b border-gray-300 flex justify-between items-start"
                ) if self.title else None,
                
                # Content section
                html.Div(
                    children,
                    className="p-4",
                    id={"type": "card-content", "index": self.id}
                )
            ]
        )

def register_fullscreen_callbacks(app: Dash) -> None:
    """Register callbacks for fullscreen functionality."""
    from dash.dependencies import Input, Output, State, MATCH
    
    @app.callback(
        Output({"type": "card-container", "index": MATCH}, "className"),
        Output({"type": "maximize-icon", "index": MATCH}, "className"),
        Output({"type": "minimize-icon", "index": MATCH}, "className"),
        Input({"type": "fullscreen-button", "index": MATCH}, "n_clicks"),
        State({"type": "card-container", "index": MATCH}, "className"),
        prevent_initial_call=True
    )
    def toggle_fullscreen(n_clicks: int, current_classes: str) -> tuple[str, str, str]:
        is_currently_fullscreen = "fixed inset-0 w-full h-full z-50" in current_classes
        
        if is_currently_fullscreen:
            # Remove fullscreen classes
            new_classes = current_classes.replace("fixed inset-0 w-full h-full z-50", "").strip()
            maximize_classes = "fas fa-expand"
            minimize_classes = "fas fa-compress hidden"
        else:
            # Add fullscreen classes
            new_classes = f"{current_classes} fixed inset-0 w-full h-full z-50"
            maximize_classes = "fas fa-expand hidden"
            minimize_classes = "fas fa-compress"
            
        return new_classes, maximize_classes, minimize_classes