from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from utils.config import load_config
from webdriver_manager.chrome import ChromeDriverManager


CHROMEDRIVER_PATH = r"E:\Prateek\Prateek Projects\News_scraping\NewOutletScrap\driver\chromedriver-win32\chromedriver.exe"

config = load_config()
print(config)
headless = config.get('driver',{}).get('headless', True)

def get_chrome_driver(headless=headless):
    options = Options()
    if headless:
        print("[DEBUG] Running Chrome in headless mode.")
        options.add_argument('--headless')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
        # options.add_argument("--start-maximized")
        options.add_argument("--start-maximized")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(
        service=Service(CHROMEDRIVER_PATH),
        options=options
    )
    return driver
