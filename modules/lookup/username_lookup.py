import re

import requests
from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause

SITES = {
    "GitHub": "https://github.com/{username}",
    "GitLab": "https://gitlab.com/{username}",
    "Reddit": "https://www.reddit.com/user/{username}/",
    "Keybase": "https://keybase.io/{username}",
    "Dev.to": "https://dev.to/{username}",
    "Medium": "https://medium.com/@{username}",
    "Codeberg": "https://codeberg.org/{username}",
    "HackerOne": "https://hackerone.com/{username}",
    "PyPI": "https://pypi.org/user/{username}/",
}


def extract_title(text):
    match = re.search(r"<title[^>]*>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    return re.sub(r"\s+", " ", match.group(1)).strip()[:160]


def run():
    module_header("Username Lookup", "OSINT")
    username = console.input("[bold white]Username:[/bold white] ").strip()
    if not username:
        console.print("[red]Username is required.[/red]")
        pause()
        return

    session = requests.Session()
    session.headers.update({"User-Agent": "VOID/1.0"})
    results = []
    for site, template in SITES.items():
        url = template.format(username=username)
        try:
            response = session.get(url, timeout=10, allow_redirects=True)
            exists = response.status_code == 200
            results.append({
                "site": site,
                "url": url,
                "final_url": response.url,
                "status": response.status_code,
                "exists": exists,
                "title": extract_title(response.text[:200_000]) if exists else None,
                "content_type": response.headers.get("Content-Type"),
            })
        except requests.RequestException as exc:
            results.append({"site": site, "url": url, "error": str(exc), "exists": False})

    table = Table(title=f"Public Profiles · {username}", border_style="red")
    table.add_column("Site", style="bold red")
    table.add_column("Status")
    table.add_column("Profile")
    table.add_column("Title", style="white")
    table.add_column("URL")
    for item in results:
        table.add_row(
            item["site"],
            str(item.get("status") or "ERR"),
            "Found" if item.get("exists") else "Not confirmed",
            str(item.get("title") or item.get("error") or ""),
            item.get("final_url") or item["url"],
        )
    console.print(table)

    found = [item for item in results if item.get("exists")]
    path = save_log("username_lookup", username, {"found_count": len(found), "results": results})
    console.print(f"[dim]Confirmed public profiles: {len(found)}[/dim]")
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
