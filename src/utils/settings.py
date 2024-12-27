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
        'raw': project_root / 'data' / 'raw',
        'clean': project_root / 'data' / 'clean',
        'geo_mapping': project_root / 'data' / 'raw' / 'geo_mapping',
        'components': project_root / 'src' / 'components',
        'pages': project_root / 'src' / 'pages',
        'utils': project_root / 'src' / 'utils'
    }
    
    # Create directories if they don't exist
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
        
    return paths