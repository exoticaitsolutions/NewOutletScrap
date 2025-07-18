import pytest
from src.scrapers.latimes import LATimesScraper

def test_latimes_scraper_init():
    url = "https://www.latimes.com/"
    scraper = LATimesScraper(url)
    assert scraper.url == url
    assert scraper.name == 'LATimesScraper'

# Note: For real scraping, use Selenium's mock or patching for unit tests. 