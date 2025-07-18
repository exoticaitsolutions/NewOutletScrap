import logging
import os
import sys
import yaml
from scrapers import ReutersScraper, LATimesScraper, LAistScraper, TheGuardianScraper, DowntownLAScraper

# Set up logging

LOG_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'logs')
)
LOG_FILE = os.path.join(LOG_DIR, 'news_scraper.log')
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
logger = logging.getLogger(__name__)

# Load config (placeholder)

CONFIG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'config/scraper_config.yaml')
)
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
        print(config)
        logger.info('Config loaded successfully.')
else:
    config = {}
    logger.warning('Config file not found, using defaults.')

def main():
    logger.info('Starting news scraping process...')
    sites = config.get('sites', {})
    if sites.get('reuters', {}).get('enabled', False):
        url = sites['reuters']['url']
        scraper = ReutersScraper(url, logger=logger)
        scraper.scrape()
    if sites.get('latimes', {}).get('enabled', False):
        url = sites['latimes']['url']
        scraper = LATimesScraper(url, logger=logger)
        scraper.scrape()
    if sites.get('laist', {}).get('enabled', False):
        url = sites['laist']['url']
        scraper = LAistScraper(url, logger=logger)
        scraper.scrape()
    if sites.get('theguardian', {}).get('enabled', False):
        url = sites['theguardian']['url']
        scraper = TheGuardianScraper(url, logger=logger)
        scraper.scrape()
    if sites.get('downtownla', {}).get('enabled', False):
        url = sites['downtownla']['url']
        scraper = DowntownLAScraper(url, logger=logger)
        scraper.scrape()
    logger.info('Scraping complete.')

if __name__ == '__main__':
    main() 