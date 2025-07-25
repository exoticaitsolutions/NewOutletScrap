import csv
import os
import random
import urllib.parse
from utils.config import load_config
from .base import BaseScraper
import time
from datetime import datetime, timedelta
from utils.chrome_driver import get_chrome_driver
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta, timezone
from dateutil import parser

class LAistScraper(BaseScraper):
    def __init__(self, url, logger=None):
        super().__init__('LAistScraper', url, logger)

    def scrape(self):
        self.logger.info(f"Starting scrape for {self.url}")
        config = load_config()
        driver = get_chrome_driver()
        rows = []
        seen_urls = self.load_existing_urls()
        cutoff_days = config.get('cutoff_days', 7)
        cutoff_date = datetime.now() - timedelta(days=cutoff_days)

        try:
            driver.get(self.url)
            time.sleep(random.uniform(9, 11))

            article_links = driver.find_elements(By.CSS_SELECTOR, 'div.PromoA-title > a')
            urls = [a.get_attribute('href') for a in article_links if a.get_attribute('href')]

            for url in urls:
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                try:
                    driver.get(url)
                    time.sleep(random.uniform(4, 6))

                    headline = ''
                    meta_desc = ''
                    date_text = ''
                    published_date = None

                    try:
                        headline = driver.find_element(By.TAG_NAME, 'h1').text.strip()
                    except:
                        pass

                    try:
                        paragraph = driver.find_element(By.CSS_SELECTOR, '.ArticlePage-articleBody p')
                        meta_desc = paragraph.text.strip()
                    except:
                        pass

                    try:
                        date_published = driver.find_element(By.CSS_SELECTOR, "div.ArticlePage-datePublished")
                        date_text = date_published.text.strip()

                        cleaned_date = date_text.replace("Published ", "").strip()
                        try:
                            published_date = datetime.strptime(cleaned_date, "%b %d, %Y %I:%M %p")
                        except ValueError:
                            published_date = datetime.strptime(cleaned_date, "%B %d, %Y")

                    except Exception as e:
                        self.logger.warning(f"Couldn't parse date for {url}: {e}")
                        continue


                    if published_date and published_date >= cutoff_date:
                        rows.append([
                            published_date.strftime('%Y-%m-%d'),
                            'LAist',
                            headline,
                            meta_desc,
                            url
                        ])
                        seen_urls.add(url)
                    else:
                        self.logger.info(f"Old or invalid article: {url}")
                        
                except Exception as e:
                    self.logger.warning(f"Error scraping article: {url} | {e}")
                    continue

            if rows:
                self.save_headline_rows(rows)
                self.logger.info(f"Saved {len(rows)} unique recent articles to all_headlines.csv")
            else:
                self.logger.info("No recent unique articles found to save.")

        finally:
            driver.quit()

        self.logger.info(f"Scraping finished. Total articles saved: {len(rows)}.")


    def scrape_by_keywords(self):
        config = load_config()
        driver = get_chrome_driver()
        time.sleep(random.uniform(2, 4))

        keywords = config.get('keywords', [])
        base_url = config.get('sites', {}).get('laist_keyword', {}).get('url', self.url)
        rows = []
        seen_urls = self.load_existing_urls()
        cutoff_days = config.get('cutoff_days', 7)
        cutoff_date = datetime.now().date() - timedelta(days=cutoff_days)

        articles_to_scrape = []

        try:
            for keyword in keywords:
                search_url = f"{base_url}/search?q={keyword}#gsc.tab=0&gsc.q={keyword}&gsc.sort=date"
                self.logger.info(f"Searching for keyword: {keyword}")
                self.logger.info(f"URL: {search_url}")
                driver.get(search_url)
                time.sleep(random.uniform(4, 5))

                articles = driver.find_elements(By.CSS_SELECTOR, "div.gsc-table-result")
                self.logger.info(f"Found {len(articles)} articles for keyword '{keyword}'")

                for article in articles:
                    try:
                        title_elem = article.find_element(By.CSS_SELECTOR, "a.gs-title")
                        title = title_elem.get_attribute("textContent").strip()
                        url = title_elem.get_attribute("href")
                        if not url or url in seen_urls:
                            continue

                        try:
                            snippet_elem = article.find_element(By.CSS_SELECTOR, ".gs-snippet")
                            snippet_text = snippet_elem.text.strip()
                            if "..." in snippet_text:
                                _, desc = snippet_text.split("...", 1)
                                desc = desc.strip()
                            else:
                                desc = snippet_text
                        except:
                            desc = "No description"

                        articles_to_scrape.append({
                            "title": title,
                            "url": url,
                            "desc": desc
                        })

                    except Exception as e:
                        self.logger.warning(f"Error collecting article info: {e}")
                        continue

            self.logger.info(f"Collected {len(articles_to_scrape)} unique article URLs across all keywords.")

            for article in articles_to_scrape:
                url = article["url"]
                title = article["title"]
                desc = article["desc"]

                if url in seen_urls:
                    continue

                try:
                    driver.get(url)
                    time.sleep(random.uniform(4, 6))

                    try:
                        post_date_elem = driver.find_element(By.CSS_SELECTOR, 'div.ArticlePage-datePublished')
                        date_text = post_date_elem.text.strip().replace("Published", "").strip()

                        try:
                            published_date = parser.parse(date_text).date()
                        except Exception as e:
                            self.logger.warning(f"Date parse failed for {url}: {e}")
                            continue

                        if published_date < cutoff_date:
                            self.logger.info(f"[SKIPPED - Old article] {url}")
                            continue

                    except Exception as e:
                        self.logger.warning(f"Date parse failed for {url}: {e}")
                        continue

                    rows.append([
                        published_date.strftime('%Y-%m-%d'),
                        'LAist',
                        title,
                        desc,
                        url,
                    ])
                    seen_urls.add(url)

                except Exception as e:
                    self.logger.warning(f"Error scraping article detail from {url}: {e}")
                    continue

            if rows:
                self.save_headline_rows(rows)
                self.logger.info(f"Saved {len(rows)} articles to all_headlines.csv.")
            else:
                self.logger.info("No recent articles found to save.")

        finally:
            driver.quit()
