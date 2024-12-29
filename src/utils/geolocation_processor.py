from typing import Optional, Dict, List, Tuple
import pandas as pd
import numpy as np
from pathlib import Path
from .geocoding_helper import GeocodingHelper

from . import logger

class GeolocationProcessor:
    """
    Process geolocation data for disaster datasets.
    """
    
    REQUIRED_COLUMNS = ['Location', 'Country', 'Subregion', 'Region']
    GEOLOC_DB_FILENAME = 'geolocation_database.csv'
    
    def __init__(self, data_folder: Path):
        """
        Initialize with path to data folder.
        
        Args:
            data_folder: Path to the data folder where geolocation database will be stored
        """
        self.data_folder = data_folder
        self.geocoder = GeocodingHelper()
        self.db_path = self.data_folder / self.GEOLOC_DB_FILENAME
        self._load_or_create_database()

    def _load_or_create_database(self) -> None:
        """Load existing geolocation database or create new one."""
        try:
            self.geo_db = pd.read_csv(self.db_path)
            logger.info(f"Loaded existing geolocation database with {len(self.geo_db)} entries")
        except FileNotFoundError:
            self.geo_db = pd.DataFrame(columns=[
                'Location', 'Country', 'Subregion', 'Region',
                'Latitude', 'Longitude', 'source_column'
            ])
            logger.info("Created new geolocation database")

    def _get_most_precise_location(self, row: pd.Series) -> Tuple[str, str]:
        """
        Get the most precise location available in row.
        
        Returns:
            Tuple of (location string, source column name)
        """
        # Order from most to least precise
        for col in ['Location', 'Country', 'Subregion', 'Region']:
            if pd.notna(row[col]) and row[col] != '':
                location = row[col]
                if col != 'Location' and pd.notna(row['Country']):
                    location = f"{location}, {row['Country']}"
                return location, col
        return '', ''

    def _create_location_key(self, row: pd.Series) -> str:
        """Create a unique key from location information."""
        return '|'.join(str(row[col]) if pd.notna(row[col]) else '' 
                       for col in self.REQUIRED_COLUMNS)

    def ProcessGeolocation(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process DataFrame to add/update geolocation data.
        
        Args:
            df: DataFrame with Location, Country, Subregion, Region columns
            
        Returns:
            DataFrame with added/updated Latitude and Longitude columns
        """
        # Validate input
        missing_cols = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Create working copy
        result_df = df.copy()
        
        # Ensure Latitude and Longitude columns exist
        for col in ['Latitude', 'Longitude']:
            if col not in result_df.columns:
                result_df[col] = np.nan

        # Process each row
        for idx, row in result_df.iterrows():
            # Skip if already has coordinates
            if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
                continue
                
            # Create location key
            loc_key = self._create_location_key(row)
            
            # Check if location exists in database
            db_match = self.geo_db[
                self.geo_db[self.REQUIRED_COLUMNS].fillna('')
                .agg('|'.join, axis=1) == loc_key
            ]
            
            if not db_match.empty:
                # Use coordinates from database
                result_df.at[idx, 'Latitude'] = db_match.iloc[0]['Latitude']
                result_df.at[idx, 'Longitude'] = db_match.iloc[0]['Longitude']
                continue
            
            # Get most precise location available
            location_str, source_col = self._get_most_precise_location(row)
            
            if location_str:
                try:
                    # Get coordinates from API
                    coords = self.geocoder.get_coordinates(location_str)
                    if coords:
                        # Update DataFrame
                        result_df.at[idx, 'Latitude'] = coords['latitude']
                        result_df.at[idx, 'Longitude'] = coords['longitude']
                        
                        # Add to database
                        self.geo_db = pd.concat([self.geo_db, pd.DataFrame([{
                            'Location': row['Location'],
                            'Country': row['Country'],
                            'Subregion': row['Subregion'],
                            'Region': row['Region'],
                            'Latitude': coords['latitude'],
                            'Longitude': coords['longitude'],
                            'source_column': source_col
                        }])], ignore_index=True)
                except Exception as e:
                    logger.error(f"Error geocoding {location_str}: {e}")

        # Save updated database
        self.geo_db.to_csv(self.db_path, index=False)
        
        # Log statistics
        total = len(result_df)
        with_coords = result_df[['Latitude', 'Longitude']].notna().all(axis=1).sum()
        logger.info(f"Geolocation complete: {with_coords}/{total} records have coordinates "
                   f"({with_coords/total*100:.1f}%)")
        
        return result_df