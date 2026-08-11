import httpx
import ipaddress
import socket
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Set

_PRIVATE_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
]

def _is_safe_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    hostname = parsed.hostname
    if not hostname:
        return False
    try:
        ip = ipaddress.ip_address(socket.gethostbyname(hostname))
        for network in _PRIVATE_NETWORKS:
            if ip in network:
                return False
    except Exception:
        return False
    return True

async def fetch_html(url: str) -> str | None:
    if not _is_safe_url(url):
        return None
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
