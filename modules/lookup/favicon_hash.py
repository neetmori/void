import base64
import hashlib
import re
from urllib.parse import urljoin, urlparse

import requests
from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause


def normalize_url(value):
    value = value.strip()
    if not value.startswith(("http://", "https://")):
        value = "https://" + value
    return value


def murmurhash3_32(data, seed=0):
    data = bytearray(data)
    length = len(data)
    h1 = seed & 0xFFFFFFFF
    c1 = 0xCC9E2D51
    c2 = 0x1B873593
    rounded = length & ~0x3
    for index in range(0, rounded, 4):
        k1 = data[index] | (data[index + 1] << 8) | (data[index + 2] << 16) | (data[index + 3] << 24)
        k1 = (k1 * c1) & 0xFFFFFFFF
        k1 = ((k1 << 15) | (k1 >> 17)) & 0xFFFFFFFF
        k1 = (k1 * c2) & 0xFFFFFFFF
        h1 ^= k1
        h1 = ((h1 << 13) | (h1 >> 19)) & 0xFFFFFFFF
        h1 = (h1 * 5 + 0xE6546B64) & 0xFFFFFFFF
    k1 = 0
    tail = length & 3
    if tail == 3:
        k1 ^= data[rounded + 2] << 16
    if tail >= 2:
        k1 ^= data[rounded + 1] << 8
    if tail >= 1:
        k1 ^= data[rounded]
        k1 = (k1 * c1) & 0xFFFFFFFF
        k1 = ((k1 << 15) | (k1 >> 17)) & 0xFFFFFFFF
        k1 = (k1 * c2) & 0xFFFFFFFF
        h1 ^= k1
    h1 ^= length
    h1 ^= h1 >> 16
    h1 = (h1 * 0x85EBCA6B) & 0xFFFFFFFF
    h1 ^= h1 >> 13
    h1 = (h1 * 0xC2B2AE35) & 0xFFFFFFFF
    h1 ^= h1 >> 16
    return h1 if h1 < 0x80000000 else h1 - 0x100000000


def discover_favicon(response):
    html = response.text[:500_000]
    patterns = [
        r'<link[^>]+rel=["\'][^"\']*(?:shortcut icon|icon)[^"\']*["\'][^>]+href=["\']([^"\']+)',
        r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\'][^"\']*(?:shortcut icon|icon)[^"\']*["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return urljoin(response.url, match.group(1))
    return urljoin(response.url, "/favicon.ico")


def run():
    module_header("Favicon Hash", "Web")
    target = normalize_url(console.input("[bold white]URL:[/bold white] "))
    session = requests.Session()
    session.headers.update({"User-Agent": "VOID/1.0"})

    try:
        page = session.get(target, timeout=15, allow_redirects=True)
        page.raise_for_status()
        favicon_url = discover_favicon(page)
        favicon = session.get(favicon_url, timeout=15, allow_redirects=True)
        favicon.raise_for_status()
    except requests.RequestException as exc:
        console.print(f"[red]Favicon lookup failed: {exc}[/red]")
        pause()
        return

    data = favicon.content
    encoded = base64.encodebytes(data)
    hashes = {
        "md5": hashlib.md5(data).hexdigest(),
        "sha1": hashlib.sha1(data).hexdigest(),
        "sha256": hashlib.sha256(data).hexdigest(),
        "shodan_mmh3": murmurhash3_32(encoded),
    }

    table = Table(title="Favicon Fingerprint", show_header=False, border_style="red")
    table.add_column("Field", style="bold red")
    table.add_column("Value", style="white")
    table.add_row("Page URL", page.url)
    table.add_row("Favicon URL", favicon.url)
    table.add_row("HTTP Status", str(favicon.status_code))
    table.add_row("Content Type", favicon.headers.get("Content-Type", "Not provided"))
    table.add_row("Bytes", str(len(data)))
    table.add_row("MD5", hashes["md5"])
    table.add_row("SHA-1", hashes["sha1"])
    table.add_row("SHA-256", hashes["sha256"])
    table.add_row("Shodan MMH3", str(hashes["shodan_mmh3"]))
    console.print(table)

    path = save_log("favicon_hash", target, {"page_url": page.url, "favicon_url": favicon.url, "bytes": len(data), "content_type": favicon.headers.get("Content-Type"), "hashes": hashes})
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
