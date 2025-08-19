import os
import csv
import glob
import yaml
import threading
import logging
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

# Google APIs
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class BaseScraper(ABC):
    _csv_lock = threading.Lock()
    _csv_header_written = {}
    _csv_columns = ['Date Published', 'Publication', 'Headline', 'Meta Description', 'Link']

    # ==== Google API Config ====
    SHEETS_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    CREDENTIALS_FILE = 'credentials.json'
    TOKEN_FILE = 'token.pickle'
   
    SPREADSHEET_ID = None          
    SHEET_NAME = "Sheet1"

    def __init__(self, name, url, logger=None, config_path="config/scraper_config.yaml"):
        self.name = name
        self.url = url
        self.logger = logger or logging.getLogger(self.name)


        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        csv_base_path = config["csv_base_path"]
        csv_prefix = config["csv_filename_prefix"]
        days_to_keep = config["csv_days_to_keep"]

        # BaseScraper.TARGET_FOLDER_ID = config.get("google_drive_folder_id")
        BaseScraper.SPREADSHEET_ID = config.get("spreadsheet_id")

        today_str = datetime.now().strftime('%Y-%m-%d')
        self._csv_file = os.path.join(csv_base_path, f'{csv_prefix}{today_str}.csv')

        csv_dir = os.path.dirname(self._csv_file)
        if not os.path.exists(csv_dir):
            os.makedirs(csv_dir)
            self.logger.info(f"[{self.name}] Created directory: {csv_dir}")

        if self._csv_file not in BaseScraper._csv_header_written:
            BaseScraper._csv_header_written[self._csv_file] = (
                os.path.exists(self._csv_file) and os.path.getsize(self._csv_file) > 0
            )

        self.cleanup_old_csvs(csv_dir, csv_prefix, days_to_keep)

    @abstractmethod
    def scrape(self):
        pass

    # === CSV Handling ===
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
        """Save to CSV, then upload to Drive, and optionally Google Sheets."""
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

        if BaseScraper.SPREADSHEET_ID:
            self.save_to_google_sheets(rows)

    def cleanup_old_csvs(self, folder, prefix, days_to_keep):
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


    def find_existing_file(self, service, filename):
        query = f"name='{filename}' and '{self.TARGET_FOLDER_ID}' in parents and trashed=false"
        results = service.files().list(q=query, fields="files(id)").execute()
        files = results.get('files', [])
        return files[0]['id'] if files else None


    # === Google Sheets ===
    def authenticate_sheets(self):
        creds = None
        if os.path.exists(self.TOKEN_FILE):
            with open(self.TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.CREDENTIALS_FILE, self.SHEETS_SCOPES)
                creds = flow.run_local_server(port=0)
            with open(self.TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
        return build('sheets', 'v4', credentials=creds)

    def save_to_google_sheets(self, rows):
        try:
            service = self.authenticate_sheets()

            # check if header exists
            result = service.spreadsheets().values().get(
                spreadsheetId=self.SPREADSHEET_ID,
                range=f"{self.SHEET_NAME}!A1:A1"
            ).execute()
            values = result.get("values", [])

            if not values:
                header_body = {"values": [BaseScraper._csv_columns]}
                service.spreadsheets().values().append(
                    spreadsheetId=self.SPREADSHEET_ID,
                    range=f"{self.SHEET_NAME}!A1",
                    valueInputOption="RAW",
                    insertDataOption="INSERT_ROWS",
                    body=header_body
                ).execute()

            # append rows
            body = {"values": rows}
            service.spreadsheets().values().append(
                spreadsheetId=self.SPREADSHEET_ID,
                range=f"{self.SHEET_NAME}!A1",
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body=body
            ).execute()

            print(f"{len(rows)} headlines also saved to Google Sheets")

        except Exception as e:
            self.logger.error(f"Google Sheets append failed: {e}")
            print(f"Google Sheets append failed: {e}")
