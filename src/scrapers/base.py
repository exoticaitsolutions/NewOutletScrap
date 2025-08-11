import os
import csv
import glob
import yaml
import threading
import logging
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    _csv_lock = threading.Lock()
    _csv_header_written = {}
    _csv_columns = ['Date Published', 'Publication', 'Headline', 'Meta Description', 'Link']

    def __init__(self, name, url, logger=None, config_path="config/scraper_config.yaml"):
        self.name = name
        self.url = url
        self.logger = logger or logging.getLogger(self.name)

        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        csv_base_path = config["csv_base_path"]
        csv_prefix = config["csv_filename_prefix"]
        days_to_keep = config["csv_days_to_keep"]

        today_str = datetime.now().strftime('%Y-%m-%d')
        self._csv_file = os.path.join(csv_base_path, f'all_headlines_{today_str}.csv')

        csv_dir = os.path.dirname(self._csv_file)
        if not os.path.exists(csv_dir):
            os.makedirs(csv_dir)
            self.logger.info(f"[{self.name}] Created directory: {csv_dir}")

        if self._csv_file not in BaseScraper._csv_header_written:
            BaseScraper._csv_header_written[self._csv_file] = os.path.exists(self._csv_file) and os.path.getsize(self._csv_file) > 0

        # Cleanup old CSVs
        self.cleanup_old_csvs(csv_dir, csv_prefix, days_to_keep)

    @abstractmethod
    def scrape(self):
        pass

    def load_existing_urls(self):
        existing_urls = set()
        if os.path.exists(self._csv_file):
            with open(self._csv_file, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 5:
                        existing_urls.add(row[4])
        return existing_urls

    def save_headline_rows(self, rows):
        with BaseScraper._csv_lock:
            write_header = not BaseScraper._csv_header_written[self._csv_file]
            with open(self._csv_file, 'a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                if write_header:
                    writer.writerow(BaseScraper._csv_columns)
                    BaseScraper._csv_header_written[self._csv_file] = True
                for row in rows:
                    self.logger.info(f"[{self.name}] Saving row: {row}")
                    writer.writerow(row)
            print(f"[INFO] {self.name}: {len(rows)} headlines saved to {self._csv_file}")

    def cleanup_old_csvs(self, folder, prefix, days_to_keep):
        """Delete CSV files older than days_to_keep."""
        cutoff = datetime.now() - timedelta(days=days_to_keep)
        for file in glob.glob(os.path.join(folder, f"{prefix}*.csv")):
            date_str = os.path.basename(file).replace(prefix, "").replace(".csv", "")
            try:
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                if file_date < cutoff:
                    os.remove(file)
                    self.logger.info(f"[{self.name}] Deleted old CSV: {file}")
            except ValueError:
                continue
