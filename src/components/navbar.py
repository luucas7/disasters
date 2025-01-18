from dash import html


class Navbar:
    """Navigation bar component."""

    def __init__(self) -> None:
        self.layout = html.Nav(
            html.Div(
                [
                    # Title and subtitle container
                    html.Div(
                        [
                            html.H1(
                                "Global Disasters Watch",
                                className="text-xl font-bold text-white",
                            ),
                            html.P(
                                "Understanding disasters across time and space",
                                className="text-sm text-gray-300 mt-1",
                            ),
                        ],
                        className="flex flex-col",
                    ),
                    # Navigation links
                    html.Div(
                        [
                            html.A(
                                "About",
                                href="/about",
                                id="about-link",
                                className="text-white hover:text-gray-300 px-3 py-2",
                            ),
                            html.A(
                                [html.I(className="fab fa-github mr-2"), "Source Code"],
                                href="https://github.com/hyprra/disasters",
                                className="text-white hover:text-gray-300 px-3 py-2 flex items-center",
                                target="_blank",
                            ),
                        ],
                        className="flex items-center space-x-4",
                    ),
                ],
                className="container px-4 flex justify-between items-center h-full",
            ),
            className="bg-blue-800 h-20 w-full z-50 relative",  # Increased height for subtitle
        )

    def __call__(self) -> html.Nav:
        return self.layout
