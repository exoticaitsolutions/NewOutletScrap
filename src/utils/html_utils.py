from bs4 import BeautifulSoup

def extract_article_links(html, link_selector):
    """Extracts article links from HTML using a CSS selector."""
    soup = BeautifulSoup(html, 'html.parser')
    return [a['href'] for a in soup.select(link_selector) if a.has_attr('href')] 