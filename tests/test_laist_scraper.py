import pytest
from src.scrapers.laist import LAistScraper

def test_laist_scraper_init():
    url = "https://laist.com/"
    scraper = LAistScraper(url)
    assert scraper.url == url
    assert scraper.name == 'LAistScraper'

# Note: For real scraping, use Selenium's mock or patching for unit tests. 