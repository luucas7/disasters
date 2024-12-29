from typing import Optional, Dict, Any
from pathlib import Path
import pandas as pd
from pandas import DataFrame
import numpy as np
from . import logger
from .geolocation_processor import GeolocationProcessor
from .clean_data import process_and_clean_data

RAW_DISASTER_DATA_FILE = "public_emdat_custom_request_2024-12-26_cde276d8-746c-45c1-8c28-51e1fef813a6.xlsx"

def convert_to_csv(excel_path: Path, output_path: Path) -> bool:
    """
    Convert Excel file to CSV format.
    
    Args:
        excel_path: Path to Excel file
        output_path: Path for output CSV file
    """
    try:
        df = pd.read_excel(excel_path)
        df.to_csv(output_path, index=False)
        logger.info(f"Successfully converted Excel to CSV: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error converting Excel to CSV: {e}")
        return False

def read_raw_disaster_data(file_path: Path) -> Optional[DataFrame]:
    """
    Read the EMDAT disasters Excel file.
    
    Args:
        file_path: Path to directory containing the Excel file
    """
    try:
        full_path = file_path / RAW_DISASTER_DATA_FILE
        
        logger.info(f"Reading data from {full_path}")
        df = pd.read_excel(full_path)
        
        if df.empty:
            logger.error("The Excel file is empty")
            return None
            
        logger.info(f"Successfully read {len(df)} records")
        return df
        
    except FileNotFoundError:
        logger.error(f"Excel file not found in {file_path}")
        return None
    except Exception as e:
        logger.error(f"Error reading Excel file: {e}")
        return None

def process_data(data_path: Path) -> Dict[str, Any]:
    """
    Main function to process the disasters data.
    
    Args:
        data_path: Path to base data directory
    """
    try:
        # Ensure directories exist
        raw_path = data_path / 'raw'
        clean_path = data_path / 'clean'
        geo_path = data_path / 'geo_mapping'
        
        for path in [raw_path, clean_path, geo_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Read raw data
        raw_df = read_raw_disaster_data(raw_path)
        if raw_df is None:
            return {"success": False, "error": "Failed to read raw data"}
        
        # Convert to CSV for readability, bien mieux
        csv_path = raw_path / "raw_disasters.csv"
        convert_to_csv(raw_path / RAW_DISASTER_DATA_FILE, csv_path)
        
        # Clean data first
        logger.info("Starting data cleaning")
        cleaned_df, cleaning_results = process_and_clean_data(raw_df)
        

        # Save intermediate cleaned data
        interim_path = clean_path / "cleaned_disasters_no_coords.csv"
        if cleaned_df is not None:
            cleaned_df.to_csv(interim_path, index=False)
        
        # Process geolocation on cleaned data
        logger.info("Starting geolocation processing")
        #geo_processor = GeolocationProcessor(geo_path)
        #final_df = geo_processor.ProcessGeolocation(cleaned_df)
        final_df = cleaned_df.copy()
        
        # Save final data with coordinates
        output_path = clean_path / "cleaned_disasters_with_coords.csv"
        final_df.to_csv(output_path, index=False)
        logger.info(f"Saved final data to {output_path}")
        
        # Save processing summary
        stats = cleaning_results['statistics']
        stats.update({
            'input_records': len(raw_df),
            'cleaned_records': len(cleaned_df),
            'geo_mapped_records': final_df[['Latitude', 'Longitude']].notna().all(axis=1).sum()
        })
        
        return {
            "success": True,
            "statistics": stats,
        }
        
    except Exception as e:
        logger.error(f"Error in data processing: {str(e)}")
        return {
            "success": False, 
            "error": str(e)
        }