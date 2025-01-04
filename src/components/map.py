from dash import html, dcc


class Map:
    """Map component."""

    def __init__(self, data=None, geojson=None):
        self.data = data
        self.geojson = geojson
        self.layout = html.Div(
            [
                dcc.Graph(
                    id="main-map",
                    style={"height": "calc(100vh - 64px)", "width": "100%"},
                    config={"displayModeBar": False},
                ),
            ],
            className="flex-1 ml-16 mt-16",
        )
