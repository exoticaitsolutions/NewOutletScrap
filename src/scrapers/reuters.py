import os
import yaml
import time
import random
from .base import BaseScraper
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from datetime import datetime, timedelta
from utils.chrome_driver import get_chrome_driver
from utils.config import load_config
from urllib.parse import urljoin
from dateutil import parser
from utils.date_parser import parse_relative_date 


class ReutersScraper(BaseScraper):
    def __init__(self, url, logger=None):
        super().__init__('ReutersScraper', url, logger)

    def scrape(self):
        config = load_config()
        driver = get_chrome_driver()
        cutoff_days = config.get('cutoff_days', 7)
        cutoff_date = datetime.now() - timedelta(days=cutoff_days)

        rows = []
        seen_urls = self.load_existing_urls()
        article_info_list = []

        try:
            self.logger.info(f"Starting scrape for {self.url}")
            time.sleep(random.uniform(3, 4))
            keywords = config.get('keywords', [])
            base_url = config.get('sites', {}).get('reuters', {}).get('url', self.url)
            
            driver.get(base_url)
            time.sleep(random.uniform(4, 6)) 

            for keyword in keywords:
                self.logger.info(f"\nScraping keyword: {keyword}")
                search_url = f"{base_url}site-search/?query={keyword}&sort=newest"
                self.logger.info(f"[DEBUG] Reuters search URL: {search_url}")

                driver.get(search_url)
                time.sleep(random.uniform(6, 8))
                
                articles = driver.find_elements(By.CSS_SELECTOR, 'li[data-testid="StoryCard"]')
                self.logger.info(f"Found {len(articles)} articles for keyword '{keyword}'")
                
                for article in articles:
                    try:
                        news_title = article.find_element(By.CSS_SELECTOR, '[data-testid="TitleHeading"]').text.strip()
                        news_link = article.find_element(By.CSS_SELECTOR, '[data-testid="TitleLink"]')
                        rel_url = news_link.get_attribute('href')
                        full_url = urljoin(base_url, rel_url)

                        try:
                            date_elem = article.find_element(By.CSS_SELECTOR, 'time[data-testid="DateLineText"]')
                            date_text = date_elem.text.strip()
                            article_date = parse_relative_date(date_text)
                        except Exception as e:
                            self.logger.warning(f"Could not parse date for article '{news_title}': {e}")
                            continue

                        if full_url not in seen_urls:
                            article_info_list.append((article_date, news_title, full_url))

                    except Exception as e:
                        self.logger.warning(f"Skipping article due to error: {e}")
                        continue

            for article_date, title, url in article_info_list:
                if article_date < cutoff_date:
                    continue

                self.logger.info(f"Processing article: {title} | {url}")

                try:
                    driver.get(url)
                    start_time = time.time()
                    time.sleep(min(7, random.uniform(6.5, 7)))

                    try:
                        paragraphs = driver.find_elements(By.CSS_SELECTOR, 'div.article-body__content__17Yit p')
                        meta_desc = " ".join(p.text.strip() for p in paragraphs if p.text.strip())
                    except Exception as e:
                        self.logger.warning(f"Failed to extract content from article: {e}")
                        meta_desc = ""

                    rows.append([article_date.strftime('%Y-%m-%d'), "Reuters", title, meta_desc, url])
                    seen_urls.add(url)
                    self.logger.info(f"Saved row: {[article_date.strftime('%Y-%m-%d'), 'Reuters', title, meta_desc, url]}")

                except TimeoutException:
                    self.logger.warning(f"Timeout loading article: {url}")
                    continue
                except Exception as article_error:
                    self.logger.warning(f"Error scraping article page: {article_error}")
                    continue

            self.save_headline_rows(rows)
            self.logger.info(f"Scraped {len(rows)} headlines from Reuters search and saved to all_headlines.csv.")

        except Exception as e:
            self.logger.error(f"Error scraping {self.url}: {e}")

        finally:
            driver.quit()
