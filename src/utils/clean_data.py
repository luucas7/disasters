from typing import Optional, Dict, Any, List, Union
import pandas as pd
from . import logger

class EMDATCleaner:
    """
    Class to handle cleaning of EM-DAT disaster data.
    """
    
    # Constants based on EM-DAT structure
    MONETARY_COLUMNS = [
        'Insured Damage (\'000 US$)',
        'Total Damage (\'000 US$)'
    ]

    UNUSED_COLUMNS = [
        'Classification Key',
        'OFDA/BHA Response',
        'Appeal',
        'Declaration',
        'AID Contribution (\'000 US$)',
        'River Basin',
        'Insured Damage, Adjusted (\'000 US$)',
        'Total Damage, Adjusted (\'000 US$)',
        'CPI',
        'Admin Units',
        'Entry Date',
        'Last Update'
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
            'DisNo.',
            'Disaster Type',
            'ISO',
            'Country',
            'Start Year'
        ]
        
        missing_columns = [col for col in required_columns if col not in self.df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

    def delete_useless_columns(self) -> 'EMDATCleaner':
        """Delete unused columns that exist in the DataFrame."""
        columns_to_drop = [col for col in self.UNUSED_COLUMNS if col in self.df.columns]
        if columns_to_drop:
            self.df.drop(columns=columns_to_drop, inplace=True)
        return self

    def clean_identifiers(self) -> 'EMDATCleaner':
        """Clean DisNo. and other ID fields."""
        if 'DisNo.' in self.df.columns:
            # Split disaster number into components
            self.df['Year_ID'] = self.df['DisNo.'].str[:4]
            self.df['Sequence_ID'] = self.df['DisNo.'].str[5:9]
            
        if 'External IDs' in self.df.columns:
            self.df['Has_External_IDs'] = self.df['External IDs'].notna()
            
        return self

    def clean_binary_fields(self) -> 'EMDATCleaner':
        """Clean Yes/No fields."""
        for col in self.BINARY_COLUMNS:
            if col in self.df.columns:
                self.df[col] = self.df[col].map({'Yes': True, 'No': False})
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
        """Process monetary columns, handling raw values."""
        for col in self.MONETARY_COLUMNS:
            raw_col = col
            cleaned_col = col.replace(" ('000 US$)", "")
            if cleaned_col != raw_col:
                logger.info(f"Cleaning monetary column: {raw_col}; cleaned as {cleaned_col}")
            if raw_col in self.df.columns:
                self.df[cleaned_col] = pd.to_numeric(self.df[raw_col], errors='coerce')
        return self

    def clean_impact_values(self) -> 'EMDATCleaner':
        """Clean impact-related numeric columns."""
        for col in self.IMPACT_COLUMNS:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')                    
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
         .clean_dates()
         .clean_monetary_values()
         .clean_impact_values()
         .clean_geographic_data()
         .delete_useless_columns()
        )
        return self.df

def process_and_clean_data(input_df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    Main function to process and clean EMDAT disaster data.
    
    Args:
        input_df: Raw DataFrame from EMDAT Excel file
        
    Returns:
        Cleaned DataFrame or None if error occurs
    """
    try:
        # Initial data validation
        if input_df is None or input_df.empty:
            raise ValueError("Input DataFrame is empty or None")
            
        initial_shape = input_df.shape
        logger.info(f"Starting data cleaning process with {initial_shape[0]} records")
        
        # Print column names for debugging
        logger.info(f"Columns in input DataFrame: {input_df.columns.tolist()}")
        
        # Clean data using EMDATCleaner
        cleaned_df = EMDATCleaner(input_df).process()
        
        if cleaned_df is not None:
            final_shape = cleaned_df.shape
            logger.info(f"Cleaning completed. Final shape: {final_shape}")
            
            # Print remaining columns for debugging
            logger.info(f"Columns in cleaned DataFrame: {cleaned_df.columns.tolist()}")
        
        return cleaned_df
        
    except Exception as e:
        logger.error(f"Error in data cleaning process: {str(e)}")
        return None