from urllib.parse import urljoin, urlparse

import requests
from rich.panel import Panel
from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause


def normalize_origin(value):
    value = value.strip()
    if not value.startswith(("http://", "https://")):
        value = "https://" + value
    parsed = urlparse(value)
    return f"{parsed.scheme}://{parsed.netloc}"


def parse_robots(text):
    groups = []
    current = {"user_agents": [], "allow": [], "disallow": [], "crawl_delay": [], "other": []}
    sitemaps = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip()
        if key == "user-agent":
            if current["user_agents"] and (current["allow"] or current["disallow"] or current["crawl_delay"] or current["other"]):
                groups.append(current)
                current = {"user_agents": [], "allow": [], "disallow": [], "crawl_delay": [], "other": []}
            current["user_agents"].append(value)
        elif key == "allow":
            current["allow"].append(value)
        elif key == "disallow":
            current["disallow"].append(value)
        elif key == "crawl-delay":
            current["crawl_delay"].append(value)
        elif key == "sitemap":
            sitemaps.append(value)
        else:
            current["other"].append(f"{key}: {value}")
    if current["user_agents"] or current["allow"] or current["disallow"] or current["crawl_delay"] or current["other"]:
        groups.append(current)
    return groups, sitemaps


def run():
    module_header("robots.txt Analyzer", "Web")
    origin = normalize_origin(console.input("[bold white]Domain or URL:[/bold white] "))
    url = urljoin(origin, "/robots.txt")

    try:
        response = requests.get(url, timeout=12, allow_redirects=True, headers={"User-Agent": "VOID/1.0"})
    except requests.RequestException as exc:
        console.print(f"[red]robots.txt request failed: {exc}[/red]")
        pause()
        return

    if response.status_code != 200:
        console.print(Panel(f"robots.txt returned HTTP {response.status_code}.", border_style="yellow"))
        path = save_log("robots_analyzer", origin, {"url": url, "status": response.status_code, "headers": dict(response.headers)})
        console.print(f"[dim]Log saved to {path}[/dim]")
        pause()
        return

    groups, sitemaps = parse_robots(response.text)
    summary = Table(title="robots.txt Summary", show_header=False, border_style="red")
    summary.add_column("Field", style="bold red")
    summary.add_column("Value", style="white")
    summary.add_row("Requested URL", url)
    summary.add_row("Final URL", response.url)
    summary.add_row("Groups", str(len(groups)))
    summary.add_row("Sitemaps", str(len(sitemaps)))
    summary.add_row("Bytes", str(len(response.content)))
    summary.add_row("Content Type", response.headers.get("Content-Type", "Not provided"))
    console.print(summary)

    rules = Table(title="Crawler Rules", border_style="red")
    rules.add_column("User-Agent", style="bold white")
    rules.add_column("Allow")
    rules.add_column("Disallow")
    rules.add_column("Crawl Delay")
    for group in groups:
        rules.add_row(
            "\n".join(group["user_agents"]) or "*",
            "\n".join(group["allow"]) or "-",
            "\n".join(group["disallow"]) or "-",
            "\n".join(group["crawl_delay"]) or "-",
        )
    if rules.row_count:
        console.print(rules)

    if sitemaps:
        sitemap_table = Table(title="Published Sitemaps", border_style="red")
        sitemap_table.add_column("URL", style="white")
        for sitemap in sitemaps:
            sitemap_table.add_row(sitemap)
        console.print(sitemap_table)

    path = save_log("robots_analyzer", origin, {"url": response.url, "groups": groups, "sitemaps": sitemaps, "raw": response.text})
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
