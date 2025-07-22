import os
from abc import ABC, abstractmethod
import logging
import csv
import threading
from datetime import datetime

class BaseScraper(ABC):
    _csv_lock = threading.Lock()
    _csv_file = 'all_headlines.csv'
    _csv_header_written = False
    _csv_columns = ['Date Published', 'Publication', 'Headline', 'Meta Description', 'Link']

    def __init__(self, name, url, logger=None):
        self.name = name
        self.url = url
        self.logger = logger or logging.getLogger(self.name)

        # Check once if header needs to be written (across runs)
        if not BaseScraper._csv_header_written:
            if not os.path.exists(BaseScraper._csv_file) or os.path.getsize(BaseScraper._csv_file) == 0:
                BaseScraper._csv_header_written = False  # File doesn't exist or is empty
            else:
                BaseScraper._csv_header_written = True   # File has content; header assumed written

    @abstractmethod
    def scrape(self):
        """Main method to perform scraping. Should be implemented by subclasses."""
        pass

    def save_headline_rows(self, rows):
        """Append rows to the common CSV file. Each row is a list matching _csv_columns."""
        with BaseScraper._csv_lock:
            write_header = not BaseScraper._csv_header_written
            with open(BaseScraper._csv_file, 'a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                if write_header:
                    writer.writerow(BaseScraper._csv_columns)
                    BaseScraper._csv_header_written = True
                for row in rows:
                    print(f"[INFO] {self.name}: Saving row: {row}")
                    writer.writerow(row)
        print(f"[INFO] {self.name}: {len(rows)} headlines saved to {BaseScraper._csv_file}")
