import dash
from src.utils.get_data import process_data, load_countries_geojson
from src.utils.settings import get_project_paths
from src.pages.dashboard import create_dashboard_layout, init_callbacks

def initialize_app() -> dash.Dash:
    """
    Initialize and configure the Dash application.
    
    Returns:
        A configured Dash application instance
    """
    paths = get_project_paths()
    
    # Process data
    data = process_data(paths['data'])['data']
    geojson = load_countries_geojson(paths['geo_mapping'])
    
    # Initialize app
    app = dash.Dash(
        __name__,
        external_stylesheets=[
            'https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css'
        ],
        suppress_callback_exceptions=True
    )
    
    # Set up layout
    app.layout = create_dashboard_layout(data, geojson)
    
    # Initialize callbacks
    init_callbacks(app, data, geojson)
    
    return app

def main() -> None:
    """Main function to launch the dashboard."""
    app = initialize_app()
    app.run_server(debug=True)

if __name__ == "__main__":
    main()