import os
import yaml
import time
import random
from .base import BaseScraper
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from datetime import datetime
from utils.chrome_driver import get_chrome_driver
from utils.config import load_config

from datetime import datetime, timedelta




class ReutersScraper(BaseScraper):
    def __init__(self, url, logger=None):
        super().__init__('ReutersScraper', url, logger)

    def scrape(self):
        config = load_config()
        driver = get_chrome_driver()
        cutoff_days = config.get("scrape_days_limit", 1)
        cutoff_date = datetime.utcnow() - timedelta(days=cutoff_days)
        rows = []
        try:
            self.logger.info(f"Starting scrape for {self.url}")
            keywords = config.get('keywords', [])
            url = config.get('sites', {}).get('reuters', {}).get('url', self.url)
            driver.get(url)
            time.sleep(4)  # Wait for the page to load
            for i, keyword in enumerate(keywords):
                search_url = f"{url}site-search/?query={keyword.replace(' ', '%20')}"
                print(f"[DEBUG] Reuters search URL: {search_url}")
                driver.get(search_url)
                time.sleep(random.uniform(4, 6))
                ul_element = driver.find_element(By.CLASS_NAME, "search-results__list__2SxSK")
                li_elements = ul_element.find_elements(By.TAG_NAME, "li")

                for li in li_elements:
                    # try:
                        # Extract datetime
                        published_date_str = li.find_element(By.TAG_NAME, "time").get_attribute("datetime")
                        published_date = datetime.strptime(published_date_str, '%Y-%m-%dT%H:%M:%SZ')

                        # Optional: cutoff check
                        # if published_date < cutoff_date:
                        #     print(f"[INFO] Reached article older than 2 days ({published_date}). Stopping.")
                        #     break

                        # Find only <a> with data-testid="TitleLink" inside this <li>
                        title_link = li.find_element(By.CSS_SELECTOR, 'a[data-testid="TitleLink"]')
                        heading = title_link.text.strip()
                        print(f"[DEBUG] Found headline: {heading}")
                        link = title_link.get_attribute("href")

                        print(f"Opening: {link}")
                        driver.get(link)
                        time.sleep(random.uniform(4, 6))  # Anti-bot delay
                        try:
                            paragraph = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="paragraph-1"]').text.strip()
                        except NoSuchElementException:
                            paragraph = "[No paragraph-1 found]"

                        print(f"[DEBUG] Found paragraph: {paragraph}")
                    # except Exception as e:
                    #     print(f"[WARN] Skipping <li> due to error: {e}")
                     

                
                # html = driver.page_source
                # soup = BeautifulSoup(html, 'html.parser')
                # articles = soup.select('div.search-results__list > div.search-results__item')
                # for article in articles:
                #     headline_tag = article.find('h3', class_='search-results__headline')
                #     headline = headline_tag.get_text(strip=True) if headline_tag else ''
                #     link_tag = headline_tag.find('a') if headline_tag else None
                #     link = f"https://www.reuters.com{link_tag['href']}" if link_tag and link_tag.has_attr('href') else search_url
                #     meta_desc = article.find('p', class_='search-results__description')
                #     meta_desc = meta_desc.get_text(strip=True) if meta_desc else ''
                #     date_tag = article.find('time')
                #     date_published = date_tag['datetime'] if date_tag and date_tag.has_attr('datetime') else ''
                #     if not date_published:
                #         date_published = datetime.now().strftime('%Y-%m-%d')
                #     rows.append([
                #         date_published,
                #         'Reuters',
                #         headline,
                #         meta_desc,
                #         link
                #     ])
            self.save_headline_rows(rows)
            self.logger.info(f"Scraped {len(rows)} headlines from Reuters search and saved to all_headlines.csv.")
        except Exception as e:
            self.logger.error(f"Error scraping {self.url}: {e}")
        finally:
            driver.quit() 