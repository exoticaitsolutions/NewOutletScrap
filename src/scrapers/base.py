import os
import csv
import threading
import logging
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    _csv_lock = threading.Lock()
    _csv_file = 'all_headlines1.csv'
    _csv_header_written = False
    _csv_columns = ['Date Published', 'Publication', 'Headline', 'Meta Description', 'Link']

    def __init__(self, name, url, logger=None):
        self.name = name
        self.url = url
        self.logger = logger or logging.getLogger(self.name)

        if not BaseScraper._csv_header_written:
            if not os.path.exists(BaseScraper._csv_file) or os.path.getsize(BaseScraper._csv_file) == 0:
                BaseScraper._csv_header_written = False
            else:
                BaseScraper._csv_header_written = True

    @abstractmethod
    def scrape(self):
        pass

    def load_existing_urls(self):
        existing_urls = set()
        csv_file = BaseScraper._csv_file  
        if os.path.exists(csv_file):
            with open(csv_file, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 5:
                        existing_urls.add(row[4])
        return existing_urls


    def save_headline_rows(self, rows):
        with BaseScraper._csv_lock:
            write_header = not BaseScraper._csv_header_written
            with open(BaseScraper._csv_file, 'a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                if write_header:
                    writer.writerow(BaseScraper._csv_columns)
                    BaseScraper._csv_header_written = True
                for row in rows:
                    self.logger.info(f"[{self.name}] Saving row: {row}")
                    writer.writerow(row)
            print(f"[INFO] {self.name}: {len(rows)} headlines saved to {BaseScraper._csv_file}")
