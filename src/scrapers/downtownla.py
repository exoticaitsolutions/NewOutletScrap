import os
import time
import yaml
from .base import BaseScraper
from selenium.webdriver.common.by import By
from utils.chrome_driver import get_chrome_driver
from datetime import datetime
from utils.config import load_config

class DowntownLAScraper(BaseScraper):
    def __init__(self, url, logger=None):
        super().__init__('DowntownLAScraper', url, logger)

    def scrape(self):
        self.logger.info(f"Starting scrape for {self.url}")
        config = load_config()
        # Initialize Chrome driver
        driver = get_chrome_driver()

        rows = []
        try:
            keywords = config.get('keywords', [])
            url = config.get('sites', {}).get('downtownla', {}).get('url', self.url)
            for i, keyword in enumerate(keywords):
                search_url = f"{url}search?q={keyword.replace(' ', '+')}"
                driver.get(search_url)
                time.sleep(4)
                ul_element = driver.find_element(By.CLASS_NAME, "site-search")
                li_elements = ul_element.find_elements(By.TAG_NAME, "li")
                for li in li_elements:
                    try:
                        a_tag = li.find_element(By.TAG_NAME, "a")
                        link = a_tag.get_attribute("href")
                        heading = a_tag.text.strip()

                        try:
                            meta_desc = li.find_element(By.CLASS_NAME, "solr_highlight").text.strip()
                        except:
                            meta_desc = ""

                        date_published = "NA"
                        rows.append([
                            date_published,
                            'DowntownLA',
                            heading,
                            meta_desc,
                            link
                        ])
                    except Exception as e:
                        self.logger.error(f"Error processing li element: {e}")
 
            self.save_headline_rows(rows)
            self.logger.info(f"Scraped {len(rows)} headlines from DowntownLA search and saved to all_headlines.csv.")
        except Exception as e:
            self.logger.error(f"Error scraping {self.url}: {e}")
        finally:
            driver.quit() 