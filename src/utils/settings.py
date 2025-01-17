from typing import Dict
from pathlib import Path

def get_project_paths() -> Dict[str, Path]:
    """
    Define and create project directories structure.
    
    Returns:
        Dictionary containing project paths including data, components, and pages directories
    """
    project_root = Path(__file__).resolve().parent.parent.parent
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