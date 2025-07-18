from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from utils.config import load_config
from webdriver_manager.chrome import ChromeDriverManager



config = load_config()
headless = config.get('driver', {}).get('headless', True)

def get_chrome_driver(headless=headless):
    options = Options()
    if headless:
        print("[DEBUG] Running Chrome in headless mode.")
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver
