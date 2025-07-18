from .base import BaseScraper
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from datetime import datetime

class LAistScraper(BaseScraper):
    def __init__(self, url, logger=None):
        super().__init__('LAistScraper', url, logger)

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
            driver.get(self.url)
            time.sleep(3)  # Wait for page to load
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            articles = soup.select('article')
            for article in articles:
                headline_tag = article.find(['h2', 'h3'])
                headline = headline_tag.get_text(strip=True) if headline_tag else ''
                link_tag = headline_tag.find('a') if headline_tag else None
                link = link_tag['href'] if link_tag and link_tag.has_attr('href') else self.url
                meta_desc = article.find('p').get_text(strip=True) if article.find('p') else ''
                date_tag = article.find('time')
                date_published = date_tag['datetime'] if date_tag and date_tag.has_attr('datetime') else ''
                if not date_published:
                    date_published = datetime.now().strftime('%Y-%m-%d')
                rows.append([
                    date_published,
                    'LAist',
                    headline,
                    meta_desc,
                    link
                ])
            self.save_headline_rows(rows)
            self.logger.info(f"Scraped {len(rows)} headlines from LAist and saved to all_headlines.csv.")
        except Exception as e:
            self.logger.error(f"Error scraping {self.url}: {e}")
        finally:
            driver.quit() 