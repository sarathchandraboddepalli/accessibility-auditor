import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Set

async def fetch_html(url: str) -> str | None:
    headers = {
        "User-Agent": "GIGW-Accessibility-Auditor/1.0 (Government Compliance Scanner)",
        "Accept": "text/html,application/xhtml+xml",
    }
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                return response.text
    except Exception:
        return None
    return None

def extract_links(html: str, base_url: str, domain: str) -> Set[str]:
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)
        if parsed.netloc == domain and parsed.scheme in ("http", "https"):
            clean = full_url.split("#")[0].rstrip("/")
            links.add(clean)
    return links

def get_page_title(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find("title")
    return title_tag.get_text(strip=True) if title_tag else None
