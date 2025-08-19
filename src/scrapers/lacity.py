import os
import yaml
import time
import random
from .base import BaseScraper
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
from utils.chrome_driver import get_chrome_driver
from utils.config import load_config
from datetime import datetime, timedelta, timezone


class LacityScraper(BaseScraper):
    def __init__(self, url, logger=None):
        super().__init__('LacityScraper', url, logger)


    def parse_date(self, date_text):
        try:
            return datetime.strptime(date_text.strip(), "%B %d, %Y").replace(tzinfo=timezone.utc)
        except Exception:
            return None

    def scrape(self):
        config = load_config()
        driver = get_chrome_driver()
        seen_urls = self.load_existing_urls()
        rows = []

        try:
            self.logger.info(f"Starting scrape for {self.url}")
            keywords = config.get('keywords', [])
            base_url = config.get('sites', {}).get('lacity', {}).get('url', self.url)
            cutoff_days = config.get('cutoff_days', 1)
            cutoff_date = datetime.now() - timedelta(days=cutoff_days)
            seen_urls = self.load_existing_urls()

            for keyword in keywords:
                self.logger.info(f"\nScraping keyword: {keyword}")
                search_url = f"{base_url}search/site?keys={keyword.replace(' ', '%20')}"
                driver.get(search_url)
                time.sleep(random.uniform(9,11))

                li_list = driver.find_elements(By.CSS_SELECTOR, 'ol.list-group.node_search-results li.list-group-item')
                self.logger.info(f"Found {len(li_list)} articles for keyword '{keyword}'")

                article_links = []
                for li in li_list:
                    try:
                        a_tag = li.find_element(By.TAG_NAME, 'a')
                        title = a_tag.text.strip()
                        href = a_tag.get_attribute('href')
                        text = li.text.strip()

                        if href in seen_urls:
                            self.logger.info(f"[SKIP] URL already in CSV: {href}")
                            continue

                        article_links.append((title, text, href))
                    except Exception:
                        continue
                    
                for title, text, href in article_links:
                    try:
                        driver.get(href)
                        time.sleep(random.uniform(4,6))

                        try:
                            date_div = driver.find_element(By.CSS_SELECTOR, 'div.field--name-field-date')
                            date_text = date_div.text.strip()
                            if "Posted on" in date_text:
                                date_str = date_text.replace("Posted on", "").strip()
                                published_date = datetime.strptime(date_str, "%m/%d/%Y")

                                if published_date >= cutoff_date:
                                    formatted_date = published_date.strftime("%Y-%m-%d")
                                    rows.append((formatted_date, "LAcity", title, text, href))
                        except NoSuchElementException:
                            continue
                    except Exception:
                        continue

            self.save_headline_rows(rows)
            self.logger.info(f"Scraped {len(rows)} new headlines from LAcity and saved to all_headlines.csv")

        finally:
            driver.quit()




