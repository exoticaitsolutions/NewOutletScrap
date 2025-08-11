import random
from .base import BaseScraper 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import time
from datetime import datetime, timedelta, timezone
from dateutil import parser 
from utils.chrome_driver import get_chrome_driver
from utils.config import load_config
from selenium.webdriver.support.ui import Select


class LATimesScraper(BaseScraper):
    def __init__(self, url, logger=None, max_items=20):
        super().__init__('LATimesScraper', url, logger)
        self.max_items = max_items

    def scrape(self):
        self.logger.info(f"Starting scrape for {self.url}")
        driver = get_chrome_driver()
        rows = []
        seen_urls = self.load_existing_urls()
        today = datetime.now()
        seven_days_ago = today - timedelta(days=7)

        try:
            driver.get(self.url)
            time.sleep(random.uniform(4, 5))

            collected = 0

            while collected < self.max_items:
                try:
                    ul = driver.find_element(By.CSS_SELECTOR, 'ul.list-menu.list-i-menu')
                    li_elements = ul.find_elements(By.TAG_NAME, 'li')
                    self.logger.info(f"Found {len(li_elements)} <li> elements")
                except Exception as e:
                    self.logger.warning(f"Could not find article list container: {e}")
                    break

                for li in li_elements:
                    if collected >= self.max_items:
                        break

                    try:
                        title_element = li.find_element(By.CSS_SELECTOR, '.promo-title a')
                        title = title_element.text.strip()
                        link = title_element.get_attribute('href')

                        if not link or link in seen_urls:
                            self.logger.info(f"[SKIP] URL already in CSV: {link}")
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

                        rows.append([
                            article_date.strftime('%Y-%m-%d'),
                            'LAtimes',
                            title,
                            'N/A',
                            link,
                        ])
                        seen_urls.add(link)
                        collected += 1
                        print(f"[{collected}] Added: {link}")

                    except Exception as e:
                        self.logger.warning(f"Error parsing <li> item: {e}")

                if collected < self.max_items:
                    try:
                        load_more = driver.find_element(By.CSS_SELECTOR, 'div.list-pagination button.button-load-more')
                        driver.execute_script("arguments[0].click();", load_more)
                        time.sleep(random.uniform(3, 4))
                    except (NoSuchElementException, ElementClickInterceptedException):
                        self.logger.info("No more 'Load More' button or click failed.")
                        break

        finally:
            driver.quit()

        self.save_headline_rows(rows)
        self.logger.info(f"Scraped and saved {len(rows)} new articles.")




    def scrape_by_keywords(self):
            config = load_config()
            driver = get_chrome_driver()
            time.sleep(random.uniform(2, 4))

            keywords = config.get('keywords', [])
            base_url = config.get('sites', {}).get('latimes_keyword', {}).get('url', self.url)
            rows = []
            seen_urls = self.load_existing_urls()

            try:
                for keyword in keywords:
                    search_url = f"{base_url}/search?q={(keyword)}&s=1"
                    self.logger.info(f"Searching for keyword: {keyword}")
                    driver.get(search_url)
                    time.sleep(random.uniform(4,5))
                    cutoff_days = config.get('cutoff_days', 7)
                    cutoff_date = datetime.now().date() - timedelta(days=cutoff_days)

                    promos = driver.find_elements(By.CSS_SELECTOR, 'div.promo-wrapper')
                    self.logger.info(f"Found {len(promos)} articles for keyword '{keyword}'")
                    
                    for promo in promos:
                        try:
                            title_element = promo.find_element(By.CSS_SELECTOR, 'h3.promo-title a')
                            title = title_element.text.strip()
                            link = title_element.get_attribute('href')
                          
                            if link in seen_urls:
                                self.logger.info(f"[SKIP] URL already seen or saved: {link}")
                                continue
                            seen_urls.add(link)


                            try:
                                description_element = promo.find_element(By.CSS_SELECTOR, '.promo-content .promo-description')
                                description = description_element.text
                            except:
                                description = "N/A"

                            try:
                                time_tag = promo.find_element(By.CSS_SELECTOR, 'time')
                                datetime_str = time_tag.get_attribute('datetime')
                                time_text = promo.find_element(By.CSS_SELECTOR, 'time span[data-element="date-time-content"]').text.strip()
                                published_dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00')).date()
                            except Exception as e:
                                self.logger.warning(f"Failed to parse date for {link}: {e}")
                                published_dt = None
                                time_text = "NA"

                            if published_dt and published_dt >= cutoff_date:
                                rows.append([time_text, "LAtimes", title, description, link])
                        except Exception as e:
                            self.logger.info(f" Error extracting promo: {e}")
                            
                self.save_headline_rows(rows)
                self.logger.info(f"Scraped {len(rows)} headlines from Reuters {keywords} search and saved to all_headlines.csv.")
                
            except Exception as e:
                self.logger.error(f"Error scraping {self.url}: {e}")
            finally:
                driver.quit()



