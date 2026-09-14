from urllib.parse import urljoin, urlparse

import requests
from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause

COMMON_PATHS = [
    "/sitemap.xml",
    "/sitemap_index.xml",
    "/sitemap-index.xml",
    "/sitemap.txt",
    "/wp-sitemap.xml",
]


def normalize_origin(value):
    value = value.strip()
    if not value.startswith(("http://", "https://")):
        value = "https://" + value
    parsed = urlparse(value)
    return f"{parsed.scheme}://{parsed.netloc}"


def discover_from_robots(origin):
    try:
        response = requests.get(urljoin(origin, "/robots.txt"), timeout=10, headers={"User-Agent": "VOID/1.0"})
        if response.status_code != 200:
            return []
        found = []
        for line in response.text.splitlines():
            if line.lower().startswith("sitemap:"):
                value = line.split(":", 1)[1].strip()
                if value:
                    found.append(value)
        return found
    except requests.RequestException:
        return []


def run():
    module_header("Sitemap Finder", "Web")
    origin = normalize_origin(console.input("[bold white]Domain or URL:[/bold white] "))
    candidates = [urljoin(origin, path) for path in COMMON_PATHS]
    candidates.extend(discover_from_robots(origin))
    candidates = list(dict.fromkeys(candidates))

    results = []
    for url in candidates:
        try:
            response = requests.get(url, timeout=10, allow_redirects=True, headers={"User-Agent": "VOID/1.0"})
            content_type = response.headers.get("Content-Type", "")
            looks_like_sitemap = response.status_code == 200 and (
                "xml" in content_type.lower()
                or "text/plain" in content_type.lower()
                or "<urlset" in response.text[:1000].lower()
                or "<sitemapindex" in response.text[:1000].lower()
            )
            results.append({
                "url": url,
                "final_url": response.url,
                "status": response.status_code,
                "content_type": content_type,
                "bytes": len(response.content),
                "valid_candidate": looks_like_sitemap,
            })
        except requests.RequestException as exc:
            results.append({"url": url, "error": str(exc), "valid_candidate": False})

    table = Table(title="Sitemap Discovery", border_style="red")
    table.add_column("Status", style="bold red")
    table.add_column("Published")
    table.add_column("URL", style="white")
    table.add_column("Content Type")
    table.add_column("Bytes", justify="right")
    for item in results:
        table.add_row(
            str(item.get("status") or "ERR"),
            "Yes" if item.get("valid_candidate") else "No",
            item.get("final_url") or item.get("url") or "",
            item.get("content_type") or item.get("error") or "",
            str(item.get("bytes") or 0),
        )
    console.print(table)

    path = save_log("sitemap_finder", origin, {"candidates": results})
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
