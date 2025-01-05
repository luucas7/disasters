from dash import html

class Statistics:
    def __init__(self, data=None):
        self.data = data
        self.layout = html.Div(
            [
                html.P(
                    f"Total number of recorded disasters: {len(data):,}",
                    className="text-xl font-semibold text-blue-600",
                ),
                html.P(
                    f"Date range: {int(data['Start Year'].min())} - {int(data['Start Year'].max())}",
                    className="text-gray-600 mt-2",
                ),
                html.P(
                    f"Number of countries: {data['Country'].nunique():,}",
                    className="text-gray-600",
                ),
            ],
            className="p-4",
        )

    def __call__(self):
        return self.layout
