import dash
from src.utils.get_data import process_data, load_json_file, load_areas_file
from src.utils.settings import get_project_paths
from src.pages.dashboard import create_dashboard_layout, init_callbacks
import argparse

def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        Parsed command line arguments
    """
    parser = argparse.ArgumentParser(description='Dashboard launching script with data processing options')
    parser.add_argument(
        '--clean', 
        action='store_true',
        help='Force cleaning of existing data'
    )
    parser.add_argument(
        '--scrape', 
        action='store_true',
        help='Force new data scraping'
    )
    parser.add_argument(
        '--port', 
        type=int,
        default=8050,
        help='Port to run the dashboard on (default: 8050)'
    )
    return parser.parse_args()

def initialize_app(force_clean: bool = False, force_scrape: bool = False) -> dash.Dash:
    """
    Initialize and configure the Dash application.
    
    Args:
        force_clean: Whether to force cleaning of existing data
        force_scrape: Whether to force new data scraping
    
    Returns:
        A configured Dash application instance
    """
    paths = get_project_paths()
    
    # Process data with new parameters
    data = process_data(
        paths["data"],
        force_clean=force_clean,
        force_scrape=force_scrape
    )["data"]
    
    geojson = load_json_file(paths["geojson_file"])
    areas = load_areas_file(paths["areas_file"])


    
    # Initialize app
    app = dash.Dash(
        __name__,
        external_stylesheets=[
            "/assets/tailwind.min.css"
        ],
        suppress_callback_exceptions=True,
    )
    
    # Set up layout
    app.layout = create_dashboard_layout(data, geojson, areas)
    
    # Initialize callbacks
    init_callbacks(app, data, geojson, areas)
    
    return app

def main() -> None:
    """Main function to launch the dashboard."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Initialize app with parsed arguments
    app = initialize_app(
        force_clean=args.clean,
        force_scrape=args.scrape
    )
    
    # Run server with specified port
    app.run_server(debug=True, port=args.port)

if __name__ == "__main__":
    main()