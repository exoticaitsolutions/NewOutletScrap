from .base import BaseScraper 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import time
import datetime
from dateutil import parser 
from utils.chrome_driver import get_chrome_driver

class LATimesScraper(BaseScraper):
    def __init__(self, url, logger=None, max_items=50):
        super().__init__('LATimesScraper', url, logger)
        self.max_items = max_items


    def scrape(self):
        self.logger.info(f"Starting scrape for {self.url}")
        driver = get_chrome_driver()
        rows = []
        seen_urls = set()
        today = datetime.datetime.now()
        seven_days_ago = today - datetime.timedelta(days=7)

        try:
            driver.get(self.url)
            time.sleep(5)

            while len(seen_urls) < self.max_items:
                ul = driver.find_element(By.CSS_SELECTOR, 'ul.list-menu.list-i-menu')
                li_elements = ul.find_elements(By.TAG_NAME, 'li')

                for li in li_elements:
                    if len(seen_urls) >= self.max_items:
                        break

                    try:
                        title_element = li.find_element(By.CSS_SELECTOR, '.promo-title a')
                        title = title_element.text.strip()
                        link = title_element.get_attribute('href')

                        if link in seen_urls:
                            continue

                        time_element = li.find_element(By.CSS_SELECTOR, 'time.promo-timestamp span[data-element="date-time-content"]')
                        timestamp_text = time_element.text.strip()

                       
                        try:
                            article_date = parser.parse(timestamp_text)
                            if article_date < seven_days_ago:
                                continue  
                        except Exception as e:
                            self.logger.warning(f"Failed to parse date: {timestamp_text} — {e}")
                            continue

                        seen_urls.add(link)
                        rows.append([
                            article_date.strftime('%Y-%m-%d'),
                            'LAtimes',
                            title,
                            'N/A',
                            link,
                        ])

                        print("\n========== ARTICLE ==========")
                        print(f"Date: {article_date}")
                        print(f"Source: LAtimes")
                        print(f"Headline: {title}")
                        print(f"URL: {link}")
                        print("=============================\n")

                    except Exception as e:
                        self.logger.warning(f"Error parsing article li: {e}")

                if len(seen_urls) < self.max_items:
                    try:
                        load_more = driver.find_element(By.CSS_SELECTOR, 'div.list-pagination button.button-load-more')
                        driver.execute_script("arguments[0].click();", load_more)
                        time.sleep(3)
                    except (NoSuchElementException, ElementClickInterceptedException):
                        self.logger.info("No more 'Load More' button or click failed.")
                        break

        finally:
            driver.quit()
        self.save_headline_rows(rows)

