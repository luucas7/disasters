import dash
from dash import html
from src.utils.get_data import process_data
from src.utils.settings import get_project_paths

def initialize_app() -> dash.Dash:
    """
    Initialize and configure the Dash application.
    
    Returns:
        A configured Dash application instance
    """
    app = dash.Dash(
        __name__,
        external_stylesheets=[]
    )
    
    app.layout = html.Div([
        html.H1("Natural Disasters Analysis", className="text-center p-4"),
        html.Div(id="main-content")
    ])
    
    return app

def main() -> None:
    """Main function to initialize data and launch the dashboard."""
    paths = get_project_paths()
    process_data(paths['raw'])
    
    app = initialize_app()
    app.run_server(debug=True)

if __name__ == "__main__":
    main()