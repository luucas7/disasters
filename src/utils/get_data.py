import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
from pandas import DataFrame

from . import logger
from .clean_data import process_and_clean_data
from .scraper import download_from_site

RAW_DISASTER_DATA_FILE = "public_emdat.xlsx"


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


def process_data(
    data_path: Path, force_clean: bool = False, force_scrape: bool = False
) -> Dict[str, Any]:
    """
    Main function to process the disasters data.

    Args:
        data_path: Path to base data directory
        force_clean: Force data reprocessing even if cleaned data exists
        force_scrape: Enable web scraping to get fresh data
    """
    try:
        # Ensure directories exist
        raw_path = data_path / "raw"
        clean_path = data_path / "clean"

        for path in [raw_path, clean_path]:
            path.mkdir(parents=True, exist_ok=True)

        # Check if we need to process data
        if (
            not force_clean
            and not force_scrape
            and (clean_path / "cleaned_disasters.csv").exists()
        ):
            df = pd.read_csv(clean_path / "cleaned_disasters.csv")
            return {"success": True, "data": df}

        # Download fresh data if scraping is enabled
        if force_scrape:
            URL = "https://public.emdat.be"
            download_dir = str(os.path.abspath(raw_path))
            try:
                from config import PASSWORD, USERNAME

                logger.info("Downloading data from EMDAT website")
                download_from_site(
                    URL, USERNAME, PASSWORD, download_dir, RAW_DISASTER_DATA_FILE
                )
            except ImportError:
                logger.error(
                    "Please provide a emdat USERNAME and PASSWORD in a config.py file at project root"
                )
                return {"success": False, "error": "No credentials provided"}

        # Read raw data
        raw_df = read_raw_disaster_data(raw_path)
        if raw_df is None:
            return {"success": False, "error": "Failed to read raw data"}

        # Convert to CSV for readability
        csv_path = raw_path / "raw_disasters.csv"
        convert_to_csv(raw_path / RAW_DISASTER_DATA_FILE, csv_path)

        # Clean data
        cleaned_df = process_and_clean_data(raw_df)
        if cleaned_df is None:
            return {"success": False, "error": "Failed to clean data"}

        # Save cleaned data
        final_df_path = clean_path / "cleaned_disasters.csv"
        cleaned_df.to_csv(final_df_path, index=False)

        return {"success": True, "data": cleaned_df}

    except Exception as e:
        logger.error(f"Error in data processing: {str(e)}")
        return {"success": False, "error": str(e)}


def load_json_file(file_path: Path) -> Dict[str, Any]:
    """
    Load the countries GeoJSON data.

    Args:
        file_path: Path to the GeoJSON file
    """
    try:
        with open(file_path, "r") as f:
            geojson = json.load(f)

        return geojson

    except FileNotFoundError:
        logger.error(f"GeoJSON file not found in {file_path}")
        return None
    except Exception as e:
        logger.error(f"Error reading GeoJSON file: {e}")
        return None


def load_areas_file(file_path: Path) -> Dict[str, float]:
    """
    Load the countries areas data into a dictionary.

    Args:
        file_path: Path to the areas CSV file

    Returns:
        Dictionary mapping ISO codes to country areas
    """
    try:
        areas_df = pd.read_csv(file_path)

        # Convertir le DataFrame en dictionnaire avec ISO comme clé
        areas_dict = areas_df.set_index("ISO")["Area"].to_dict()

        return areas_dict

    except FileNotFoundError:
        logger.error(f"Areas file not found in {file_path}")
        return None
    except Exception as e:
        logger.error(f"Error reading areas file: {e}")
        return None
