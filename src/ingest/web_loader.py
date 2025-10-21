import requests, trafilatura

def fetch_clean_text(url: str, timeout: int = 20) -> str:
    html = requests.get(url, timeout=timeout).text
    txt = trafilatura.extract(html) or ""
    return txt.strip()

