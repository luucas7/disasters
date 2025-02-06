import os
import dash

from src.pages.dashboard import create_dashboard_layout, init_callbacks
from src.utils.get_data import load_areas_file, load_json_file, process_data
from src.utils.settings import get_project_paths


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
        paths["data"], force_clean=force_clean, force_scrape=force_scrape
    )["data"]

    geojson = load_json_file(paths["geojson_file"])
    areas = load_areas_file(paths["areas_file"])

    # Initialize app
    app = dash.Dash(
        __name__,
        external_stylesheets=["/assets/tailwind.min.css"],
        suppress_callback_exceptions=True,
    )

    server = app.server

    @server.route("/health")
    def health():
        return "OK", 200

    # Set up layout
    app.layout = create_dashboard_layout(app, data, geojson, areas)

    # Initialize callbacks
    init_callbacks(app, data, geojson, areas)

    return app


# Expose server for Gunicorn
app = initialize_app()
server = app.server  # Gunicorn va chercher cette variable


def main() -> None:
    """Main function to launch the dashboard."""
    import argparse  # Déplacement de argparse ici pour éviter les conflits

    parser = argparse.ArgumentParser(
        description="Dashboard launching script with data processing options"
    )
    parser.add_argument("--clean", action="store_true", help="Force cleaning of existing data")
    parser.add_argument("--scrape", action="store_true", help="Force new data scraping")
    parser.add_argument("--port", type=int, default=8050, help="Port to run the dashboard on (default: 8050)")
    args = parser.parse_args()

    # Utiliser $PORT si défini par DigitalOcean, sinon l'argument CLI
    port = int(os.environ.get("PORT", args.port))

    # Lancer le serveur
    app.run_server(debug=False, port=port, host="0.0.0.0")


if __name__ == "__main__":
    main()
