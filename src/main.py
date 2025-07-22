import os
import sys
import yaml
from scrapers import ReutersScraper, LATimesScraper, LAistScraper, TheGuardianScraper, DowntownLAScraper, ApnewsScraper, LacityScraper
from utils.config import load_config
from utils.logger_config import loger_config

# Set up logging
logger = loger_config()

# Load config (placeholder)
config = load_config()


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
    if sites.get('apnews', {}).get('enabled', False):
        url = sites['apnews']['url']
        scraper = ApnewsScraper(url, logger=logger)
        scraper.scrape()
    if sites.get('lacity', {}).get('enabled', False):
        url = sites['lacity']['url']
        scraper = LacityScraper(url, logger=logger)
        scraper.scrape()
    logger.info('Scraping complete.')

if __name__ == '__main__':
    main() 