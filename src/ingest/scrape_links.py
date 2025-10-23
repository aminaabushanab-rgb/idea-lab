import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def scrape_article_links(url: str, prefix: str) -> set[str]:
    """
    Fetches a webpage and extracts all links that start with a specific prefix.
    Returns a set of unique, absolute URLs.
    """
    print(f"  > Scraping {url} for links starting with '{prefix}'...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        html = requests.get(url, headers=headers, timeout=10).text
    except Exception as e:
        print(f"  > Failed to fetch {url}: {e}")
        return set()

    soup = BeautifulSoup(html, "html.parser")
    all_a_tags = soup.find_all('a')
    unique_links = set()

    for tag in all_a_tags:
        href = tag.get('href')
        
        if href and href.startswith(prefix):
            absolute_url = urljoin(url, href)
            if absolute_url.startswith("http"):
                unique_links.add(absolute_url)
            
    return unique_links
