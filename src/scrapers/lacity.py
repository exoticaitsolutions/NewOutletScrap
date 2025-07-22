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
from datetime import datetime, timedelta
from urllib.parse import urljoin


class LacityScraper(BaseScraper):
    def __init__(self, url, logger=None):
        super().__init__('LacityScraper', url, logger)

    def scrape(self):
        config = load_config()
        driver = get_chrome_driver()

        rows = []
        seen_urls = set() 

        try:
            print("yaha tak chal gaya-----------------------")
            self.logger.info(f"Starting scrape for {self.url}")
            # time.sleep(random.uniform(5,7))
            keywords = config.get('keywords', [])
            base_url = config.get('sites', {}).get('lacity', {}).get('url', self.url)

            for i, keyword in enumerate(keywords):
                print(f"\n Scraping keyword: {keyword}")
                search_url = f"{base_url}search/site?keys={keyword.replace(' ', '%20')}"

                driver.get(search_url)
                time.sleep(10)
                print(f"lacity search URL: {search_url}")
                time.sleep(random.uniform(4, 6))
                
                li_list = driver.find_elements(By.CSS_SELECTOR, 'ol.list-group.node_search-results li.list-group-item')
                print(f"Found {len(li_list)} articles for keyword '{keyword}'")

                for li in li_list:
                    try:
                        a_tag = li.find_element(By.TAG_NAME, 'a')
                        title = a_tag.text.strip()
                        href = a_tag.get_attribute('href')
                        text = li.text.strip()
                        rows.append(("N/A","LAcity",title, text, href))
                    except Exception as e:
                        continue

                for source, site, title, text, href in rows:
                    
                    print("\n========== ARTICLE ==========")
                    print(f"Title: {title}")
                    print(f"URL: {href}")
                    print(f"Text: {text}")
                    print("=============================\n")
                    
                self.save_headline_rows(rows)
                self.logger.info(f"Scraped {len(rows)} headlines from LAcity search and saved to all_headlines.csv.")


        finally:
            driver.quit()
