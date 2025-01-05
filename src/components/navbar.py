from dash import html

class Navbar:
    """Navigation bar component."""
    
    def __init__(self):
        self.layout = html.Nav(
            html.Div([
                html.H1("Natural Disasters Analysis", 
                       className="text-xl font-bold text-white"),
                html.Div([
                    html.A("About", href="/about", id="about-link",
                          className="text-white hover:text-gray-300 px-3 py-2"),
    
                ], className="flex items-center space-x-4")
            ], className="container mx-auto px-4 flex justify-between items-center h-full"),
            className="bg-blue-800 h-16 w-full z-50"
        )

    def __call__(self):
        return self.layout