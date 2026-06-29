"""Standalone launcher for the Global Disasters Dashboard.

This module is the entry point used to build the self-contained Windows
executable (see ``disasters.spec`` and ``.github/workflows/build-exe.yml``).

Running the produced ``disasters.exe`` does everything automatically:
it loads the bundled data, starts a local web server and opens the
dashboard in the default browser. No Python installation or setup is
required on the user's machine.
"""

import os
import threading
import webbrowser

from main import app


def _open_browser(url: str) -> None:
    """Open the dashboard URL in the user's default web browser."""
    try:
        webbrowser.open(url)
    except Exception:
        # Failing to open the browser must not crash the server; the user
        # can still navigate to the printed URL manually.
        pass


def main() -> None:
    """Start the local server and open the dashboard automatically."""
    port = int(os.environ.get("PORT", 8050))
    url = f"http://127.0.0.1:{port}/"

    # Open the browser shortly after launch so the server has time to bind.
    threading.Timer(1.5, _open_browser, args=(url,)).start()

    print("=" * 60)
    print(" Global Disasters Dashboard")
    print(f" Running at: {url}")
    print(" Keep this window open. Close it to stop the dashboard.")
    print("=" * 60)

    # Bind to localhost only: this is a local desktop launch, not a server.
    app.run_server(debug=False, port=port, host="127.0.0.1")


if __name__ == "__main__":
    main()
