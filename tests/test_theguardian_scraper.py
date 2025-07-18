import pytest
from src.scrapers.theguardian import TheGuardianScraper

def test_theguardian_scraper_init():
    url = "https://www.theguardian.com/us-news/"
    scraper = TheGuardianScraper(url)
    assert scraper.url == url
    assert scraper.name == 'TheGuardianScraper'

# Note: For real scraping, use Selenium's mock or patching for unit tests. 