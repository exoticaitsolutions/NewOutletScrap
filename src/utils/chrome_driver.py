import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from utils.config import load_config

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

CHROMEDRIVER_PATH = os.path.join(
    BASE_DIR, "driver", "chromedriver-win32", "chromedriver.exe"
)

config = load_config()
headless = config.get('driver', {}).get('headless', True)

def get_chrome_driver(headless=False):
    if not os.path.isfile(CHROMEDRIVER_PATH):
        raise FileNotFoundError(f"ChromeDriver not found at: {CHROMEDRIVER_PATH}")

    options = Options()
    if headless:
        print("[DEBUG] Running Chrome in headless mode.")
        options.add_argument('--headless=new')
        options.add_argument('--disable-gpu')

    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(
        service=Service(CHROMEDRIVER_PATH),
        options=options
    )

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
    })

    try:
        driver.maximize_window()
    except Exception as e:
        print(f"[WARNING] Could not maximize window: {e}")

    return driver  





