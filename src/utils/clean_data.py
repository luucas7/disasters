from typing import Optional, Dict, Any, List, Union, Tuple
from pathlib import Path
import pandas as pd
import numpy as np
import json
from . import logger
from typing import Optional

class EMDATCleaner:
    """
    Class to handle cleaning of EM-DAT disaster data.
    """
    
    # Constants based on EM-DAT structure
    MONETARY_COLUMNS = [
        'AID Contribution (\'000 US$)',
        'Reconstruction Costs (\'000 US$)',
        'Insured Damage (\'000 US$)',
        'Total Damage (\'000 US$)'
    ]
    
    IMPACT_COLUMNS = [
        'Total Deaths',
        'No. Injured',
        'No. Affected',
        'No. Homeless',
        'Total Affected'
    ]
    
    BINARY_COLUMNS = [
        'Historic',
        'OFDA/BHA Response',
        'Appeal',
        'Declaration'
    ]

    def __init__(self, df: pd.DataFrame):
        """Initialize with a DataFrame."""
        self.df = df.copy()
        self.validate_required_columns()

    def validate_required_columns(self) -> None:
        """Validate presence of essential columns."""
        required_columns = [
            'DisNo.',  # Unique identifier
            'Disaster Group',
            'ISO',
            'Country',
            'Start Year'
        ]
        
        missing_columns = [col for col in required_columns if col not in self.df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

    def clean_identifiers(self) -> 'EMDATCleaner':
        """Clean DisNo. and other ID fields."""
        if 'DisNo.' in self.df.columns:
            # Split disaster number into components
            self.df['Year_ID'] = self.df['DisNo.'].str[:4]
            self.df['Sequence_ID'] = self.df['DisNo.'].str[5:9]
            
        if 'External IDs' in self.df.columns:
            # Parse external IDs (GLIDE, etc.)
            self.df['Has_External_IDs'] = self.df['External IDs'].notna()
            
        return self

    def clean_binary_fields(self) -> 'EMDATCleaner':
        """Clean Yes/No fields."""
        for col in self.BINARY_COLUMNS:
            if col in self.df.columns:
                self.df[col] = self.df[col].map({'Yes': True, 'No': False})
        return self

    def clean_admin_units(self) -> 'EMDATCleaner':
        """Process Admin Units JSON data."""
        if 'Admin Units' not in self.df.columns:
            return self
            
        def extract_admin_info(json_str: str) -> Dict[str, List[str]]:
            if pd.isna(json_str):
                return {'adm1': [], 'adm2': []}
            try:
                data = json.loads(json_str)
                return {
                    'adm1': [unit['adm1_name'] for unit in data if 'adm1_name' in unit],
                    'adm2': [unit['adm2_name'] for unit in data if 'adm2_name' in unit]
                }
            except (json.JSONDecodeError, TypeError):
                return {'adm1': [], 'adm2': []}

        admin_data = self.df['Admin Units'].apply(extract_admin_info)
        self.df['ADM1_Units'] = admin_data.apply(lambda x: x['adm1'])
        self.df['ADM2_Units'] = admin_data.apply(lambda x: x['adm2'])
        self.df['ADM1_Count'] = self.df['ADM1_Units'].str.len()
        self.df['ADM2_Count'] = self.df['ADM2_Units'].str.len()
        
        return self

    def clean_dates(self) -> 'EMDATCleaner':
        """Clean and standardize date fields."""
        date_components = {
            'Start': ['Start Year', 'Start Month', 'Start Day'],
            'End': ['End Year', 'End Month', 'End Day']
        }
        
        for prefix, columns in date_components.items():
            if all(col in self.df.columns for col in columns):
                # Convert to numeric first
                for col in columns:
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                
                # Create datetime column while preserving partial dates
                self.df[f'{prefix}_Date'] = pd.to_datetime(
                    {
                        'year': self.df[columns[0]],
                        'month': self.df[columns[1]].fillna(1),
                        'day': self.df[columns[2]].fillna(1)
                    },
                    errors='coerce'
                )
        
        # Calculate duration only when both dates are available
        if 'Start_Date' in self.df and 'End_Date' in self.df:
            mask = self.df['Start_Date'].notna() & self.df['End_Date'].notna()
            self.df.loc[mask, 'Duration_Days'] = (
                self.df.loc[mask, 'End_Date'] - 
                self.df.loc[mask, 'Start_Date']
            ).dt.days
            
        return self

    def clean_monetary_values(self) -> 'EMDATCleaner':
        """Process monetary columns, handling both raw and adjusted values."""
        for col in self.MONETARY_COLUMNS:
            raw_col = col
            adjusted_col = col.replace('(\'000 US$)', ', Adjusted (\'000 US$)')
            
            if raw_col in self.df.columns:
                self.df[raw_col] = pd.to_numeric(self.df[raw_col], errors='coerce')
                
            if adjusted_col in self.df.columns:
                self.df[adjusted_col] = pd.to_numeric(self.df[adjusted_col], errors='coerce')
                
            # Calculate adjustment ratio where both values exist
            if raw_col in self.df.columns and adjusted_col in self.df.columns:
                mask = (self.df[raw_col] > 0) & (self.df[adjusted_col] > 0)
                self.df.loc[mask, f'{raw_col}_Adjustment_Ratio'] = (
                    self.df.loc[mask, adjusted_col] / self.df.loc[mask, raw_col]
                )
        
        return self

    def clean_impact_values(self) -> 'EMDATCleaner':
        """Clean impact-related numeric columns."""
        for col in self.IMPACT_COLUMNS:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                
                # Add quality indicators
                self.df[f'{col}_is_missing'] = self.df[col].isna()
                if self.df[col].notna().any():
                    self.df[f'{col}_is_zero'] = self.df[col] == 0
                    
        return self

    def clean_geographic_data(self) -> 'EMDATCleaner':
      """Clean geographic data, focusing on river basin information."""
      if 'River Basin' in self.df.columns:
          self.df['Rivers_List'] = (
              self.df['River Basin']
              .str.split(',')
              .apply(lambda x: [r.strip() for r in x] if isinstance(x, list) else [])
          )
          self.df['River_Count'] = self.df['Rivers_List'].str.len()
      return self

    def process(self) -> pd.DataFrame:
        """Apply all cleaning steps and return cleaned DataFrame."""
        logger.info("Starting EMDAT data cleaning process")
        
        (self
         .clean_identifiers()
         .clean_binary_fields()
         .clean_admin_units()
         .clean_dates()
         .clean_monetary_values()
         .clean_impact_values()
         .clean_geographic_data()
        )
        
        logger.info("Completed EMDAT data cleaning process")
        return self.df

def process_and_clean_data(input_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Main function to process and clean EMDAT disaster data.
    
    Args:
        input_df: Raw DataFrame from EMDAT Excel file
        
    Returns:
        Tuple containing:
        - Cleaned DataFrame (or None if error)
        - Dictionary with processing results and statistics
    """
    results: Dict[str, Any] = {
        'success': False,
        'error': None,
        'statistics': {},
        'missing_columns': []
    }
    
    try:
        # Initial data validation
        if input_df is None or input_df.empty:
            raise ValueError("Input DataFrame is empty or None")
            
        initial_shape = input_df.shape
        logger.info(f"Starting data cleaning process with {initial_shape[0]} records")
        
        # Clean data using EMDATCleaner
        cleaned_df = EMDATCleaner(input_df).process()
        
        # Calculate statistics
        results['statistics'] = {
            'initial_records': initial_shape[0],
            'final_records': len(cleaned_df),
            'missing_values_pct': cleaned_df.isna().sum().to_dict(),
            'has_coordinates_pct': (
                (cleaned_df['Has_Coordinates'].mean() * 100)
                if 'Has_Coordinates' in cleaned_df.columns
                else 0
            )
        }
        
        # Add disaster type distribution
        if 'Disaster Type' in cleaned_df.columns:
            results['statistics']['disaster_type_counts'] = (
                cleaned_df['Disaster Type'].value_counts().to_dict()
            )
        
        results['success'] = True
        return cleaned_df, results
        
    except Exception as e:
        logger.error(f"Error in data cleaning process: {str(e)}")
        results['error'] = str(e)
        return None, results