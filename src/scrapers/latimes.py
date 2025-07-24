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
    def __init__(self, url, logger=None, max_items=50):
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
            time.sleep(random.uniform(4,5))

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
                    print(f"\n Searching keyword: {keyword}")
                    print(f" URL: {search_url}")
                    driver.get(search_url)
                    time.sleep(random.uniform(4,5))
                    
                
                    print("I reached here------------")
                    today = datetime.now(timezone.utc)
                    cutoff_date = today - timedelta(days=7)

                    promos = driver.find_elements(By.CSS_SELECTOR, 'div.promo-wrapper')
                    print(f"Found {len(promos)} articles for keyword '{keyword}'")
                    
                    for promo in promos:
                        try:
                            title_element = promo.find_element(By.CSS_SELECTOR, 'h3.promo-title a')
                            title = title_element.text.strip()
                            link = title_element.get_attribute('href')

                            try:
                                description_element = promo.find_element(By.CSS_SELECTOR, '.promo-content .promo-description')
                                description = description_element.text
                            except:
                                description = "N/A"

                            try:
                                span_time_element = promo.find_element(By.CSS_SELECTOR, 'time span[data-element="date-time-content"]')
                                time_text = span_time_element.text.strip()
                            except:
                                time_text = "N/A"

                            time_element = promo.find_element(By.CSS_SELECTOR, 'time')
                            date_str = time_element.get_attribute('datetime')

                            try:
                                published_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                            except ValueError:
                                published_date = datetime.strptime(date_str, '%B %d, %Y')
                                published_date = published_date.replace(tzinfo=timezone.utc)

                            if published_date >= cutoff_date:
                                print("========== ARTICLE ==========")
                                print(f"Title: {title}")
                                print(f"Link: {link}")
                                print(f"Description: {description}")
                                print(f"Published Date: {published_date.strftime('%Y-%m-%d')}")
                                print(f"Displayed Date: {time_text}")
                                print("=============================\n")
                            
                                rows.append([time_text, "LAtimes", title, description, link])
                        except Exception as e:
                            print(f" Error extracting promo: {e}")
            finally:
                driver.quit()

            self.save_headline_rows(rows)
            self.logger.info(f"Scraped {len(rows)} headlines from Reuters {keywords} search and saved to all_headlines.csv.")


