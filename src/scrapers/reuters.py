import os
import yaml
import time
import random
from .base import BaseScraper
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime, timedelta
from utils.chrome_driver import get_chrome_driver
from utils.config import load_config
from urllib.parse import urljoin
from dateutil import parser


class ReutersScraper(BaseScraper):
    def __init__(self, url, logger=None):
        super().__init__('ReutersScraper', url, logger)

    def scrape(self):
        config = load_config()
        driver = get_chrome_driver()
        time.sleep(3)

        rows = []
        seen_urls = set()
        article_urls = []

        try:
            self.logger.info(f"Starting scrape for {self.url}")
            time.sleep(random.uniform(3, 4))
            keywords = config.get('keywords', [])
            base_url = config.get('sites', {}).get('reuters', {}).get('url', self.url)

            for i, keyword in enumerate(keywords):
                print(f"\n Scraping keyword: {keyword}")
                search_url = f"{base_url}site-search/?query={keyword.replace(' ', '%20')}"
                print(f"[DEBUG] Reuters search URL: {search_url}")

                driver.get(base_url)
                time.sleep(random.uniform(3, 5)) 

                driver.get(search_url)
                time.sleep(random.uniform(4, 6))
                
                articles = driver.find_elements(By.CSS_SELECTOR, 'li[data-testid="StoryCard"]')
                print(f"Found {len(articles)} articles for keyword '{keyword}'")
                
            

                for article in articles:
                    try:
                        news_title = article.find_element(By.CSS_SELECTOR, '[data-testid="TitleHeading"]').text.strip()
                        news_link = article.find_element(By.CSS_SELECTOR, '[data-testid="TitleLink"]')
                        rel_url = news_link.get_attribute('href')
                        full_url = urljoin(base_url, rel_url)

                        try:
                            date_elem = article.find_element(By.CSS_SELECTOR, 'time[data-testid="DateLineText"]')
                            date_text = date_elem.text.strip()
                            article_date = parser.parse(date_text)
                        except Exception as e:
                            self.logger.warning(f"Could not parse date for article '{news_title}': {e}")
                            continue

                        if article_date < datetime.now() - timedelta(days=7):
                            print(f" Skipping old article dated {article_date.date()}")
                            continue

                        if full_url not in seen_urls:
                            seen_urls.add(full_url)
                            article_urls.append((article_date.strftime('%Y-%m-%d'), news_title, full_url))

                    except Exception as e:
                        self.logger.warning(f"Skipping article due to error: {e}")
                        continue

                for date, title, url in article_urls:
                    try:
                        driver.get(url)
                        time.sleep(4)

                        try:
                            paragraphs = driver.find_elements(By.CSS_SELECTOR, 'div.article-body__content__17Yit p')
                            meta_desc = " ".join(p.text.strip() for p in paragraphs if p.text.strip())
                        except Exception as e:
                            self.logger.warning(f"Failed to extract content from article: {e}")
                            meta_desc = ""

                        print("\n========== ARTICLE ==========")
                        print("Date:", date)
                        print("Title:", title)
                        print("Source: Reuters")
                        print("Description:", meta_desc[:500])
                        print("URL:", url)
                        print("=============================\n")

                        rows.append([date, "Reuters", title, meta_desc, url])
                        self.logger.info(f"Saving row: {[date, 'Reuters', title, meta_desc, url]}")
                        # self.logger.info(f"Saving row: {[date, 'Reuters', title, meta_desc[:100], url]}")

                    except Exception as article_error:
                        self.logger.warning(f"Error scraping article page: {article_error}")
                        continue

            self.save_headline_rows(rows)
            self.logger.info(f"Scraped {len(rows)} headlines from Reuters {keywords} search and saved to all_headlines.csv.")

        except Exception as e:
            self.logger.error(f"Error scraping {self.url}: {e}")

        finally:
            driver.quit()

