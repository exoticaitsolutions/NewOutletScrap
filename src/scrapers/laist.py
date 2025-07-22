import csv
import os
from .base import BaseScraper
import time
from datetime import datetime
from utils.chrome_driver import get_chrome_driver
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta


class LAistScraper(BaseScraper):
    def __init__(self, url, logger=None):
        super().__init__('LAistScraper', url, logger)
        self.csv_path = 'all_headlines.csv'

    def save_headline_rows(self, rows):
        """Save headlines to CSV (overwrite or append if needed)."""
        file_exists = os.path.exists(self.csv_path)
        with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Date', 'Source', 'Headline', 'Short Description', 'URL'])
            writer.writerows(rows)

    def scrape(self):
        self.logger.info(f"Starting scrape for {self.url}")

        driver = get_chrome_driver()
        rows = []
        seen_urls = set()

        try:
            driver.get(self.url)
            time.sleep(10)

            article_links = driver.find_elements(By.CSS_SELECTOR, 'div.PromoA-title > a')
            urls = [a.get_attribute('href') for a in article_links if a.get_attribute('href')]

            for url in urls:
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                try:
                    driver.get(url)
                    time.sleep(5)

                    try:
                        headline = driver.find_element(By.TAG_NAME, 'h1').text.strip()
                    except:
                        headline = ''

                    try:
                        paragraph = driver.find_element(By.CSS_SELECTOR, '.ArticlePage-articleBody p')
                        meta_desc = paragraph.text.strip()
                    except:
                        meta_desc = ''

                    date_published = datetime.now().strftime('%Y-%m-%d')

                    rows.append([
                        date_published,
                        'LAist',
                        headline,
                        meta_desc,
                        url
                    ])

                    print("\n========== ARTICLE ==========")
                    print(f"Date: {date_published}")
                    print(f"Source: LAist")
                    print(f"Headline: {headline}")
                    print(f"URL: {url}")
                    print(f"Body:\n{meta_desc}...")
                    print("=============================\n")

                except Exception as e:
                    self.logger.warning(f"Error scraping article: {url} | {e}")
                    continue

            if rows:
                self.save_headline_rows(rows)
                self.logger.info(f"Saved {len(rows)} unique articles to {self.csv_path}.")
            else:
                self.logger.info("No unique articles found to save.")

        finally:
            driver.quit()

        self.logger.info(f"Scraping finished. Total articles saved: {len(rows)}.")
        return rows


