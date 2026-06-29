import sys
from typing import Dict
from pathlib import Path


def get_base_path() -> Path:
    """
    Return the base path used to locate bundled resources.

    When the application runs as a PyInstaller bundle (the packaged .exe),
    data and assets are extracted next to the bootloader in ``sys._MEIPASS``.
    Otherwise we fall back to the project root, computed from this file.

    Returns:
        Base directory containing the ``data`` and ``assets`` folders.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent.parent


def get_project_paths() -> Dict[str, Path]:
    """
    Define and create project directories structure.

    Returns:
        Dictionary containing project paths including data, components, and pages directories
    """
    project_root = get_base_path()
    paths = {
        'data' : project_root / 'data',
        'raw': project_root / 'data' / 'raw',
        'clean': project_root / 'data' / 'clean',
        'geo_mapping': project_root / 'data' / 'geo_mapping',
        'geojson_file': project_root / 'data' / 'geo_mapping' / 'countries.geojson',
        'areas_file': project_root / 'data' / 'geo_mapping' / 'countries_area.csv',
        'components': project_root / 'src' / 'components',
        'pages': project_root / 'src' / 'pages',
        'utils': project_root / 'src' / 'utils'
    }

    return paths
