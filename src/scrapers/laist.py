from .base import BaseScraper


import time
from datetime import datetime
from utils.chrome_driver import get_chrome_driver
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta

class LAistScraper(BaseScraper):
    def __init__(self, url, logger=None):
        super().__init__('LAistScraper', url, logger)

    def scrape(self):
        self.logger.info(f"Starting scrape for {self.url}")

        
        driver = get_chrome_driver()
        rows = []
        try:
            driver.get(self.url)
            time.sleep(10)

            article_links = driver.find_elements(By.CSS_SELECTOR, 'div.PromoA-title > a')

            urls = [a.get_attribute('href') for a in article_links if a.get_attribute('href')]
            
            print("try to search")
            next_page = driver.find_element(By.CLASS_NAME,"ListD-nextPage")
            print("Nect page button found-------------")
            
            for url in urls:
                try:
                    driver.get(url)
                    time.sleep(5)

                    try:
                        headline = driver.find_element(By.TAG_NAME, 'h1').text.strip()
                    except:
                        headline = ''

                    paragraphs = driver.find_elements(By.CSS_SELECTOR, 'article p')
                    body_text = '\n'.join(p.text for p in paragraphs if p.text.strip())

                    date_published = datetime.now().strftime('%Y-%m-%d')

                    rows.append([
                        date_published,
                        'LAist',
                        headline,
                        body_text,
                        url
                    ])
                    
                    print("\n========== ARTICLE ==========")
                    print(f"Date: {date_published}")
                    print(f"Source: LAist")
                    print(f"Headline: {headline}")
                    print(f"URL: {url}")
                    print(f"Body:\n{body_text[:500]}...") 
                    print("=============================\n")
                    
                    self.save_headline_rows(rows)
                    self.logger.info(f"Scraped {len(rows)} headlines from DowntownLA search and saved to all_headlines.csv.")
                except Exception as e:
                    self.logger.warning(f"Error scraping article: {url} | {e}")
                    continue

                try:
                    load_more = driver.find_element(By.CSS_SELECTOR, 'div.ListD-nextPage a')
                    if load_more.is_displayed():
                        driver.execute_script("arguments[0].scrollIntoView();", load_more)
                        load_more.click()
                        time.sleep(5)
                    else:
                        break
                except:
                    break

        finally:
            driver.quit()

        self.logger.info(f"Finished scraping {len(rows)} articles.")
        return rows
    
    
    
    


# class LAistScraper(BaseScraper):
#     def __init__(self, url, logger=None):
#         super().__init__('LAistScraper', url, logger)

#     def scrape(self):
#         self.logger.info(f"Starting scrape for {self.url}")
#         driver = get_chrome_driver()
#         rows = []
#         seen_urls = set()
#         seven_days_ago = datetime.now() - timedelta(days=7)
#         source = "LAist"

#         try:
#             driver.get(self.url)
#             time.sleep(3)

#             while True:
#                 article_containers = driver.find_elements(By.CSS_SELECTOR, 'div.PromoA')
#                 new_urls = []

#                 for container in article_containers:
#                     try:
#                         a_tag = container.find_element(By.CSS_SELECTOR, 'div.PromoA-title a')
#                         url = a_tag.get_attribute('href')
#                         if url in seen_urls:
#                             continue
#                         seen_urls.add(url)

#                         # Meta Description
#                         try:
#                             meta_desc = container.find_element(By.CSS_SELECTOR, 'div.PromoA-description').text.strip()
#                         except:
#                             meta_desc = ''

#                         new_urls.append((url, meta_desc))
#                     except:
#                         continue

#                 if not new_urls:
#                     break

#                 for url, meta_desc in new_urls:
#                     try:
#                         driver.get(url)
#                         time.sleep(2)

#                         headline = driver.find_element(By.TAG_NAME, 'h1').text.strip()
#                         paragraphs = driver.find_elements(By.CSS_SELECTOR, 'article p')
#                         body_text = '\n'.join(p.text for p in paragraphs if p.text.strip())

#                         try:
#                             date_element = driver.find_element(By.CSS_SELECTOR, 'time')
#                             date_str = date_element.get_attribute('datetime')
#                             date_published = datetime.strptime(date_str[:10], '%Y-%m-%d')
#                         except Exception:
#                             date_published = datetime.now()

#                         if date_published < seven_days_ago:
#                             self.logger.info("Reached article older than 7 days. Stopping.")
#                             return rows

#                         rows.append([
#                             date_published.strftime('%Y-%m-%d'),
#                             source,
#                             headline,
#                             meta_desc,
#                             # body_text,
#                             url
#                         ])

#                         print("\n========== ARTICLE ==========")
#                         print(f"Date: {date_published.strftime('%Y-%m-%d')}")
#                         print(f"Source: {source}")
#                         print(f"Headline: {headline}")
#                         print(f"URL: {url}")
#                         print(f"Meta Desc: {meta_desc}")
#                         # print(f"Body:\n{body_text[:500]}...")
#                         print("=============================\n")

#                         self.save_headline_rows(rows)
#                         self.logger.info(f"Scraped {len(rows)} headlines from {source} and saved to {source}_all_headlines.csv.")
#                     except Exception as e:
#                         self.logger.warning(f"Error scraping article: {url} | {e}")
#                         continue

#                 # Try clicking "Load More" button
#                 try:
#                     load_more = driver.find_element(By.CSS_SELECTOR, 'div.ListD-nextPage a')
#                     if load_more.is_displayed():
#                         driver.execute_script("arguments[0].scrollIntoView();", load_more)
#                         load_more.click()
#                         time.sleep(5)
#                     else:
#                         break
#                 except:
#                     break

#         finally:
#             driver.quit()

#         self.logger.info(f"Finished scraping {len(rows)} articles.")
#         return rows