import pytest
from src.scrapers.downtownla import DowntownLAScraper

def test_downtownla_scraper_init():
    url = "https://downtownla.com/articles"
    scraper = DowntownLAScraper(url)
    assert scraper.url == url
    assert scraper.name == 'DowntownLAScraper'

# Note: For real scraping, use Selenium's mock or patching for unit tests. 