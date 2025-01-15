import json
from typing import Optional, Dict, Any
from pathlib import Path
import pandas as pd
from pandas import DataFrame
from . import logger
from .clean_data import process_and_clean_data
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os

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

def process_data(data_path: Path, force_clean: bool = False, force_scrape: bool = False) -> Dict[str, Any]:
    """
    Main function to process the disasters data.
    
    Args:
        data_path: Path to base data directory
        force_clean: Force data reprocessing even if cleaned data exists
        force_scrape: Enable web scraping to get fresh data
    """
    try:
        # Ensure directories exist
        raw_path = data_path / 'raw'
        clean_path = data_path / 'clean'
        
        for path in [raw_path, clean_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Check if we need to process data
        if not force_clean and not force_scrape and (clean_path / "cleaned_disasters.csv").exists():
            df = pd.read_csv(clean_path / "cleaned_disasters.csv")
            return {
                "success": True,
                "data": df
            }
        
        # Download fresh data if scraping is enabled
        if force_scrape:
            URL = "https://public.emdat.be"
            download_dir = str(os.path.abspath(raw_path))
            try:
                from config import USERNAME, PASSWORD
                logger.info("Downloading data from EMDAT website")
                download_from_site(URL, USERNAME, PASSWORD, download_dir, RAW_DISASTER_DATA_FILE)
            except ImportError:
                logger.error("Please provide a emdat USERNAME and PASSWORD in a config.py file at project root")
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
                
        return {
            "success": True,
            "data": cleaned_df
        }
        
    except Exception as e:
        logger.error(f"Error in data processing: {str(e)}")
        return {
            "success": False, 
            "error": str(e)
        }

def load_countries_geojson(geo_path: Path) -> Dict[str, Any]:
    """
    Load the countries GeoJSON data.
    
    Args:
        geo_path: Path to the GeoJSON file
    """
    try:
        geojson_path = geo_path / "countries.geojson"
        
        with open(geojson_path, 'r') as f:
            geojson = json.load(f)
        
        return geojson
        
    except FileNotFoundError:
        logger.error(f"GeoJSON file not found in {geo_path}")
        return None
    except Exception as e:
        logger.error(f"Error reading GeoJSON file: {e}")
        return None
    
def download_from_site(url: str, username: str, password: str, download_path: str, filename: str) -> None:
    """
    Download data file from EMDAT website using Selenium.
    
    Args:
        url: Base URL of the EMDAT website
        username: EMDAT login username 
        password: EMDAT login password
        download_path: Directory to save downloaded file
        filename: Name to save the file as
    """
    chrome_options = Options()
    chrome_options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "download.suggested_name": filename,
        }
    )
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate to the login page
        driver.get(f"{url}/login")
        
        # Wait for login form elements and fill them
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username")) 
        )
        password_field = driver.find_element(By.ID, "password")  
        
        username_field.send_keys(username)
        password_field.send_keys(password)
        
        # Submit login form
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ant-btn-primary[type='submit']"))
        )
        login_button.click()
        
        # Go to data page
        go_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/data']"))
        )
        go_button.click()

        # Click download button
        download_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Download')]"))
        )
        download_button.click()
        
        # Wait for download to complete
        time.sleep(7)
        
        # Rename downloaded file
        downloaded_file = max(
            [os.path.join(download_path, f) for f in os.listdir(download_path)],
            key=os.path.getctime
        )
        target_file = os.path.join(download_path, filename)
        if os.path.exists(target_file):
            os.remove(target_file) 
        os.rename(downloaded_file, target_file)
        
    finally:
        driver.quit()