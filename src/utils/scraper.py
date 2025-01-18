import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def download_from_site(
    url: str, username: str, password: str, download_path: str, filename: str
) -> None:
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
        },
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
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button.ant-btn-primary[type='submit']")
            )
        )
        login_button.click()

        # Go to data page
        go_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/data']"))
        )
        go_button.click()

        # Click download button
        download_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//span[contains(text(), 'Download')]")
            )
        )
        download_button.click()

        # Wait for download to complete
        time.sleep(7)

        # Rename downloaded file
        downloaded_file = max(
            [os.path.join(download_path, f) for f in os.listdir(download_path)],
            key=os.path.getctime,
        )
        target_file = os.path.join(download_path, filename)
        if os.path.exists(target_file):
            os.remove(target_file)
        os.rename(downloaded_file, target_file)

    finally:
        driver.quit()
