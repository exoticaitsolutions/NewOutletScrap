import pytest
from src.scrapers.reuters import ReutersScraper

def test_reuters_scraper_init():
    url = "https://www.reuters.com/"
    scraper = ReutersScraper(url)
    assert scraper.url == url
    assert scraper.name == 'ReutersScraper'

# Note: For real scraping, use Selenium's mock or patching for unit tests. 