from .base import BaseScraper
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from datetime import datetime
import yaml
import os

class ReutersScraper(BaseScraper):
    def __init__(self, url, logger=None):
        super().__init__('ReutersScraper', url, logger)

    def scrape(self):
        self.logger.info(f"Starting scrape for {self.url}")
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        rows = []
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'scraper_config.yaml')
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            keywords = config.get('keywords', [])
            for i, keyword in enumerate(keywords):
                search_url = f"https://www.reuters.com/site-search/?query={keyword.replace(' ', '%20')}"
                print(f"[DEBUG] Reuters search URL: {search_url}")
                driver.get(search_url)
                time.sleep(4)
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                articles = soup.select('div.search-results__list > div.search-results__item')
                for article in articles:
                    headline_tag = article.find('h3', class_='search-results__headline')
                    headline = headline_tag.get_text(strip=True) if headline_tag else ''
                    link_tag = headline_tag.find('a') if headline_tag else None
                    link = f"https://www.reuters.com{link_tag['href']}" if link_tag and link_tag.has_attr('href') else search_url
                    meta_desc = article.find('p', class_='search-results__description')
                    meta_desc = meta_desc.get_text(strip=True) if meta_desc else ''
                    date_tag = article.find('time')
                    date_published = date_tag['datetime'] if date_tag and date_tag.has_attr('datetime') else ''
                    if not date_published:
                        date_published = datetime.now().strftime('%Y-%m-%d')
                    rows.append([
                        date_published,
                        'Reuters',
                        headline,
                        meta_desc,
                        link
                    ])
            self.save_headline_rows(rows)
            self.logger.info(f"Scraped {len(rows)} headlines from Reuters search and saved to all_headlines.csv.")
        except Exception as e:
            self.logger.error(f"Error scraping {self.url}: {e}")
        finally:
            driver.quit() 