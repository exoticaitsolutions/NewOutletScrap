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
from datetime import datetime, timedelta, timezone


class LacityScraper(BaseScraper):
    def __init__(self, url, logger=None):
        super().__init__('LacityScraper', url, logger)


    def parse_date(self, date_text):
        try:
            return datetime.strptime(date_text.strip(), "%B %d, %Y").replace(tzinfo=timezone.utc)
        except Exception:
            return None

    def scrape(self):
        config = load_config()
        driver = get_chrome_driver()
        seen_urls = self.load_existing_urls()
        rows = []

        try:
            self.logger.info(f"Starting scrape for {self.url}")
            keywords = config.get('keywords', [])
            base_url = config.get('sites', {}).get('lacity', {}).get('url', self.url)
            cutoff_days = config.get('cutoff_days', 7)
            cutoff_date = datetime.now() - timedelta(days=cutoff_days)
            seen_urls = self.load_existing_urls()

            for keyword in keywords:
                print(f"\nScraping keyword: {keyword}")
                search_url = f"{base_url}search/site?keys={keyword.replace(' ', '%20')}"
                driver.get(search_url)
                time.sleep(random.uniform(9,11))

                li_list = driver.find_elements(By.CSS_SELECTOR, 'ol.list-group.node_search-results li.list-group-item')
                self.logger.info(f"Found {len(li_list)} articles for keyword '{keyword}'")
                print(f"Found {len(li_list)} articles for keyword '{keyword}'")

                article_links = []
                for li in li_list:
                    try:
                        a_tag = li.find_element(By.TAG_NAME, 'a')
                        title = a_tag.text.strip()
                        href = a_tag.get_attribute('href')
                        text = li.text.strip()

                        if href in seen_urls:
                            continue

                        article_links.append((title, text, href))
                    except Exception:
                        continue
                    
                for title, text, href in article_links:
                    try:
                        driver.get(href)
                        time.sleep(random.uniform(4,6))

                        try:
                            date_div = driver.find_element(By.CSS_SELECTOR, 'div.field--name-field-date')
                            date_text = date_div.text.strip()
                            if "Posted on" in date_text:
                                date_str = date_text.replace("Posted on", "").strip()
                                published_date = datetime.strptime(date_str, "%m/%d/%Y")

                                if published_date >= cutoff_date:
                                    formatted_date = published_date.strftime("%Y-%m-%d")
                                    rows.append((formatted_date, "LAcity", title, text, href))
                        except NoSuchElementException:
                            continue
                    except Exception:
                        continue

            self.save_headline_rows(rows)
            self.logger.info(f"Scraped {len(rows)} new headlines from LAcity and saved to all_headlines.csv")

        finally:
            driver.quit()



# import os
# import time
# import csv
# from datetime import datetime, timedelta, timezone
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import NoSuchElementException
# from utils.chrome_driver import get_chrome_driver
# from utils.config import load_config
# from .base import BaseScraper

# class LacityScraper(BaseScraper):
#     def __init__(self, url, logger=None):
#         super().__init__('LacityScraper', url, logger)

#     def parse_date(self, date_text):
#         try:
#             return datetime.strptime(date_text.strip(), "%B %d, %Y").replace(tzinfo=timezone.utc)
#         except Exception:
#             return None

#     def scrape(self):
#         self.logger.info(f"Starting scrape for {self.url}")
#         config = load_config()
#         keywords = config.get('keywords', [])
#         cutoff_days = config.get('cutoff_days', 7)
#         cutoff_date = datetime.now(timezone.utc) - timedelta(days=cutoff_days)
#         base_url = config.get('sites', {}).get('lacity', {}).get('url', self.url)

#         driver = get_chrome_driver()
#         seen_urls = self.load_existing_urls()
#         all_rows = []

#         try:
#             for keyword in keywords:
#                 print(f"\n Scraping keyword: {keyword}")
#                 # https://lacity.gov/search/site?keys=homelessness
#                 search_url = f"{base_url}search/site?keys={keyword}"

#                 driver.get(search_url)
#                 time.sleep(10)

#                 articles = driver.find_elements(By.CSS_SELECTOR, 'div.gsc-webResult.gsc-result')
#                 self.logger.info(f"Found {len(articles)} results for keyword: '{keyword}'")
                
                
#                 for result in articles:
#                     try:
#                         title_elem = result.find_element(By.CSS_SELECTOR, "a.gs-title")
#                         title = title_elem.text.strip()
#                         url = title_elem.get_attribute("data-ctorig") or title_elem.get_attribute("href")

#                         try:
#                             snippet_elem = result.find_element(By.CSS_SELECTOR, ".gs-snippet")
#                             snippet = snippet_elem.text.strip()
#                         except:
#                             snippet = "No snippet available"

#                         print("Title:", title)
#                         print("URL:", url)
#                         print("Snippet:", snippet)
#                         print("-" * 50)

#                     except Exception as e:
#                         print("Error parsing result:", e)
#                         continue
                                
                
                # for article in articles:
                #     try:
                #         link_elem = article.find_element(By.CSS_SELECTOR, 'a')
                #         link = link_elem.get_attribute("href")
                #         if not link:
                #             continue

                #         if link in seen_urls:
                #             self.logger.info(f"[SKIP] URL already in CSV: {link}")
                #             continue

                #         link_elem.click()
                #         time.sleep(2)
                #         driver.switch_to.window(driver.window_handles[-1])

                #         try:
                #             title = driver.find_element(By.CSS_SELECTOR, 'h1').text.strip()
                #         except NoSuchElementException:
                #             title = ""

                #         try:
                #             meta_desc = driver.find_element(By.CSS_SELECTOR, 'meta[name="description"]').getAttribute('content').strip()
                #         except NoSuchElementException:
                #             meta_desc = ""

                #         try:
                #             date_text = driver.find_element(By.CSS_SELECTOR, 'span.date-display-single').text.strip()
                #             published_date = self.parse_date(date_text)
                #         except NoSuchElementException:
                #             published_date = None

                #         if not published_date:
                #             self.logger.info(f"Skipping article (no date): {link}")
                #         elif published_date >= cutoff_date:
                #             row = [
                #                 published_date.strftime("%Y-%m-%d"),
                #                 "LAcity",
                #                 title,
                #                 meta_desc,
                #                 link
                #             ]
                #             all_rows.append(row)
                #             seen_urls.add(link)
                #         else:
                #             self.logger.info(f"Skipping old article: {link} — {published_date}")

                #         driver.close()
                #         driver.switch_to.window(driver.window_handles[0])

                #     except Exception as e:
                #         self.logger.warning(f"Error parsing article: {e}")
                #         if len(driver.window_handles) > 1:
                #             driver.close()
                #             driver.switch_to.window(driver.window_handles[0])

        # finally:
        #     driver.quit()

        # self.save_headline_rows(all_rows)
        # self.logger.info(f"Saved {len(all_rows)} new articles.")

