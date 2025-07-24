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


                    if url in seen_urls:
                        self.logger.info(f"Already exists in CSV: {url}")
                        
                        continue
                    if published_date and published_date >= cutoff_date:
                        rows.append([
                            published_date.strftime('%Y-%m-%d'),
                            'LAist',
                            headline,
                            meta_desc,
                            url
                        ])

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
        cutoff_date = datetime.now() - timedelta(days=cutoff_days)

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
                        redirect_url = title_elem.get_attribute("href")

                        if not redirect_url:
                            continue
                        if redirect_url in seen_urls:
                            print(f"[SKIPPED - Already in CSV] {redirect_url}")
                            continue

                        try:
                            snippet_elem = article.find_element(By.CSS_SELECTOR, ".gs-snippet")
                            snippet_text = snippet_elem.text.strip()

                            if "..." in snippet_text:
                                date_info_str, desc = snippet_text.split("...", 1)
                                date_info_str = date_info_str.strip()
                                desc = desc.strip()
                            else:
                                date_info_str = "Unknown"
                                desc = snippet_text
                        except Exception as e:
                            date_info_str = "Unknown"
                            desc = "No description"

                        # try:
                        #     published_date = datetime.strptime(date_info_str, "%b %d, %Y")
                        # except Exception as e:
                        #     print(f"[SKIPPED - Invalid date] {redirect_url} - Date info: {date_info_str}")
                        #     continue

                        if date_info_str < cutoff_date:
                            print(f"[SKIPPED - Old article] {redirect_url}")
                            continue

                        rows.append([
                            date_info_str.strftime('%Y-%m-%d'),
                            'LAist',
                            title,
                            desc,
                            redirect_url,
                        ])
                        # seen_urls.add(redirect_url)

                        driver.execute_script("window.open('');")
                        driver.switch_to.window(driver.window_handles[1])
                        driver.get(redirect_url)
                        time.sleep(2)
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])

                    except Exception as e:
                        print(" Error scraping article:", e)
                        continue

            if rows:
                self.save_headline_rows(rows)
                self.logger.info(f"Scraped {len(rows)} headlines from Reuters {keywords} search and saved to all_headlines.csv.")
            else:
                self.logger.info(" No new articles found to save.")

        finally:
            driver.quit()
