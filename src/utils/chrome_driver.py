from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
from utils.config import load_config

# CHROMEDRIVER_PATH = r"driver\chromedriver-win32\chromedriver.exe"
CHROMEDRIVER_PATH = r"driver\chromedriver-linux64\chromedriver"

config = load_config()
headless = config.get('driver',{}).get('headless', True)


# Unset any proxy-related environment variables
for var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
    os.environ.pop(var, None)

def get_chrome_driver(headless=False):
    options = Options()

    # ✅ Force-disable all proxy settings
    options.add_argument("--no-proxy-server")
    options.add_argument("--proxy-server='direct://'")
    options.add_argument("--proxy-bypass-list=*")


    if headless:
        print("[DEBUG] Running Chrome in headless mode.")
        options.add_argument('--headless=new')
        options.add_argument('--disable-gpu')

    # Anti-detection flags
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # Fake user-agent
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/114.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(
        service=Service(CHROMEDRIVER_PATH),
        options=options
    )

    # Hide `navigator.webdriver`
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """
    })

    try:
        driver.maximize_window()
    except Exception as e:
        print(f"[WARNING] Could not maximize window: {e}")

    return driver

