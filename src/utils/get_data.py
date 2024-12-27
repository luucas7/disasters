from typing import Optional, Dict, Any
from pathlib import Path
import pandas as pd
from pandas import DataFrame
import numpy as np
from . import logger

RAW_DISASTER_DATA_FILE = "public_emdat_custom_request_2024-12-26_cde276d8-746c-45c1-8c28-51e1fef813a6.xlsx"
COLUMNS_TO_IGNORE = [
    'External IDs', 'OFDA/BHA Response', 'Appeal', 'Declaration',
    'AID Contribution (\'000 US$)', 'Reconstruction Costs (\'000 US$)',
    'Reconstruction Costs, Adjusted (\'000 US$)', 'Insured Damage (\'000 US$)',
    'Insured Damage, Adjusted (\'000 US$)', 'CPI', 'Entry Date', 'Last Update'
]

def convert_to_csv(excel_path: Path, output_path: Path) -> bool:
    """
    Convert Excel file to CSV format.
    
    Args:
        excel_path: Path to Excel file
        output_path: Path for output CSV file
        
    Returns:
        True if conversion successful, False otherwise
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
    """
    try:
        full_path = file_path / RAW_DISASTER_DATA_FILE
        
        logger.info(f"Reading data from {full_path}")
        df = pd.read_excel(full_path)
        
        if df.empty:
            logger.error("The Excel file is empty")
            return None
        
        # Remove ignored columns if they exist
        columns_to_keep = [col for col in df.columns if col not in COLUMNS_TO_IGNORE]
        df = df[columns_to_keep]
            
        logger.info(f"Successfully read {len(df)} records")
        return df
        
    except FileNotFoundError:
        logger.error(f"Excel file not found in {file_path}")
        return None
    except Exception as e:
        logger.error(f"Error reading Excel file: {e}")
        return None


def clean_disaster_data(df: DataFrame) -> DataFrame:
    """
    Clean the disasters data.
    """
    logger.info("Starting data cleaning process")
    
    #TODO
    return df


def process_data(raw_data_path: Path) -> Dict[str, Any]:
    """
    Main function to process the disasters data.
    """
    try:
        # Read raw data
        raw_df = read_raw_disaster_data(raw_data_path)
        if raw_df is None:
            return {"success": False, "error": "Failed to read raw data"}
        
        # Convert to CSV if needed
        csv_path = raw_data_path / "raw_disasters.csv"
        convert_to_csv(raw_data_path / RAW_DISASTER_DATA_FILE, csv_path)
        
        #TODO
        return {"success": True}
        
    except Exception as e:
        logger.error(f"Error in data processing : {e}")
        return {"success": False, "error": str(e)}