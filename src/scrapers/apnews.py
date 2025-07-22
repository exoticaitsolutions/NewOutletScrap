from email import parser
import os
import random
import time
import yaml
from .base import BaseScraper
from selenium.webdriver.common.by import By
from utils.chrome_driver import get_chrome_driver
from datetime import datetime, timedelta
from utils.config import load_config
from selenium.webdriver.support.ui import Select

from dateutil import parser  
from datetime import datetime, timedelta
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

class ApnewsScraper(BaseScraper):
    def __init__(self, url, logger=None):
        super().__init__('ApnewsScraper', url, logger)

    def scrape(self):
        self.logger.info(f"Starting scrape for {self.url}")
        config = load_config()
        driver = get_chrome_driver()

        rows = []
        try:
            keywords = config.get('keywords', [])
            base_url = config.get('sites', {}).get('apnews', {}).get('url', self.url)

            for keyword in keywords:
                print(f"\n🔍 Scraping keyword: {keyword}")
                search_url = f"{base_url}search?q={keyword.replace(' ', '+')}"
                driver.get(search_url)
                time.sleep(4)

                try:
                    dropdown = driver.find_element(By.CLASS_NAME, "Select-control")
                    dropdown.click()
                    time.sleep(1)
                    options = driver.find_elements(By.CLASS_NAME, "Select-option")
                    for option in options:
                        if "Newest" in option.text:
                            option.click()
                            break
                    time.sleep(4)
                except Exception as e:
                    self.logger.warning(f"[WARN] Could not apply 'Newest' filter: {e}")

                last_height = driver.execute_script("return document.body.scrollHeight")
                scroll_attempt = 0
                while scroll_attempt < 5: 
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(3)
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
                    scroll_attempt += 1

                containers = driver.find_elements(By.CSS_SELECTOR, "div.PagePromo")

                for container in containers:
                    try:
                        title = container.find_element(By.CSS_SELECTOR, '.PagePromo-title span').text.strip()
                        url = container.find_element(By.CSS_SELECTOR, '.PagePromo-title a').get_attribute('href')
                        try:
                            description = container.find_element(By.CSS_SELECTOR, '.PagePromo-description span').text.strip()
                        except:
                            description = ""
                        try:
                            date_text = container.find_element(By.CSS_SELECTOR, '.PagePromo-date span').text.strip()
                        except:
                            date_text = datetime.now().strftime('%Y-%m-%d')

                        try:
                            article_date = parser.parse(date_text)
                        except Exception as e:
                            self.logger.warning(f"Could not parse date '{date_text}': {e}")
                            continue

                        if article_date >= datetime.now() - timedelta(days=7):
                            print("\n========== ARTICLE ==========")
                            print("Date:", date_text)
                            print("Title:", title)
                            print("Description:", description)
                            print("URL:", url)
                            print("=============================\n")

                            rows.append([
                                article_date.strftime('%Y-%m-%d'),
                                'AP News',
                                title,
                                description,
                                url
                            ])
                        else:
                            print(f" Skipping old article: {date_text}")

                    except Exception as e:
                        self.logger.warning(f"[WARN] Skipping article block due to error: {e}")
                        continue

            self.save_headline_rows(rows)
            self.logger.info(f"Scraped {len(rows)} headlines from AP News search and saved to all_headlines.csv.")
        except Exception as e:
            self.logger.error(f"Error scraping {self.url}: {e}")
        finally:
            driver.quit()




