

import os
import time
import yaml
from .base import BaseScraper
from selenium.webdriver.common.by import By
from utils.chrome_driver import get_chrome_driver
from datetime import datetime
from utils.config import load_config

class ApnewsScraper(BaseScraper):
    def __init__(self, url, logger=None):
        super().__init__('ApnewsScraper', url, logger)

    def scrape(self):
        self.logger.info(f"Starting scrape for {self.url}")
        config = load_config()
        # Initialize Chrome driver
        driver = get_chrome_driver()

        rows = []
        try:
            keywords = config.get('keywords', [])
            url = config.get('sites', {}).get('apnews', {}).get('url', self.url)
            for i, keyword in enumerate(keywords):
                search_url = f"{url}search?q={keyword.replace(' ', '+')}"
                driver.get(search_url)
                time.sleep(4)
                
                print(f"[DEBUG] AP News search URL: {search_url}")
                container = driver.find_element(By.CLASS_NAME, "PageList-items")
                articles = container.find_elements(By.CLASS_NAME, "PageList-items-item")
                for article in articles:
                    try:
                        # Step 2: Find the inner .PagePromo div
                        # PagePromo
                        print(article.get_attribute("outerHTML"))  # DEBUG: Show full HTML of article

                        promo = article.find_element(By.CLASS_NAME, "PagePromo")

                        # 2.1 Get updated timestamp and convert
                        timestamp_ms = int(promo.get_attribute("data-updated-date-timestamp"))
                        published_date = datetime.utcfromtimestamp(timestamp_ms / 1000)

                        # 2.2 Title
                        title = promo.find_element(By.CSS_SELECTOR, ".PagePromo-title a").text.strip()

                        # 2.3 Description
                        description = promo.find_element(By.CSS_SELECTOR, ".PagePromo-description a").text.strip()

                        # 2.4 Link
                        link = promo.find_element(By.CSS_SELECTOR, ".PagePromo-title a").get_attribute("href")

                        print("Date:", published_date.strftime("%Y-%m-%d %H:%M"))
                        print("Title:", title)
                        print("Description:", description)
                        print("URL:", link)
                        print("-" * 80)

                    except Exception as e:
                        print("[WARN] Skipping article due to error:", e)
                # ul_element = driver.find_element(By.CLASS_NAME, "site-search")
                # li_elements = ul_element.find_elements(By.TAG_NAME, "li")
                # for li in li_elements:
                #     try:
                #         a_tag = li.find_element(By.TAG_NAME, "a")
                #         link = a_tag.get_attribute("href")
                #         heading = a_tag.text.strip()

                #         try:
                #             meta_desc = li.find_element(By.CLASS_NAME, "solr_highlight").text.strip()
                #         except:
                #             meta_desc = ""

                #         date_published = "NA"
                #         rows.append([
                #             date_published,
                #             'DowntownLA',
                #             heading,
                #             meta_desc,
                #             link
                #         ])
                #     except Exception as e:
                        # self.logger.error(f"Error processing li element: {e}")
 
            self.save_headline_rows(rows)
            self.logger.info(f"Scraped {len(rows)} headlines from DowntownLA search and saved to all_headlines.csv.")
        except Exception as e:
            self.logger.error(f"Error scraping {self.url}: {e}")
        finally:
            driver.quit() 