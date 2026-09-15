import re
from urllib.parse import quote

import requests
from rich.table import Table

from core.ui import console, module_header, pause

SITES = {
    "TikTok": "https://www.tiktok.com/@{username}",
    "Instagram": "https://www.instagram.com/{username}/",
    "YouTube": "https://www.youtube.com/@{username}",
    "Facebook": "https://www.facebook.com/{username}",
    "Roblox": "https://www.roblox.com/search/users?keyword={username}",
}

BLOCKED_CODES = {401, 403, 429}
NOT_FOUND_CODES = {404, 410}

NOT_FOUND_MARKERS = {
    "TikTok": ("couldn't find this account", "couldn’t find this account"),
    "Instagram": ("page isn't available", "sorry, this page isn't available"),
    "YouTube": ("this page isn't available", "404 not found"),
    "Facebook": ("this content isn't available", "page isn't available"),
}

BLOCK_MARKERS = (
    "captcha",
    "challenge",
    "too many requests",
    "access denied",
    "temporarily blocked",
)

def extract_title(text):
    match = re.search(r"<title[^>]*>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    return re.sub(r"\s+", " ", match.group(1)).strip()[:160]

def classify_response(site, username, response):
    status = response.status_code
    body = response.text[:300_000].lower()
    title = (extract_title(response.text[:200_000]) or "").lower()

    if status in BLOCKED_CODES or any(marker in body for marker in BLOCK_MARKERS):
        return "Blocked"

    if status in NOT_FOUND_CODES:
        return "Not Found"

    if any(marker in body for marker in NOT_FOUND_MARKERS.get(site, ())):
        return "Not Found"

    if status != 200:
        return "Unknown"

    needle = username.lower()
    final_url = response.url.lower()

    if site == "TikTok" and f"/@{needle}" in final_url:
        return "Found"
    if site == "Instagram" and f"instagram.com/{needle}" in final_url:
        return "Found"
    if site == "YouTube" and f"youtube.com/@{needle}" in final_url:
        return "Found"
    if site == "Facebook" and f"facebook.com/{needle}" in final_url:
        return "Found"

    if needle in title or needle in body:
        return "Found"

    return "Unknown"

def check_roblox(session, username):
    url = f"https://www.roblox.com/search/users?keyword={quote(username)}"
    api_url = "https://users.roblox.com/v1/users/search"

    try:
        response = session.get(
            api_url,
            params={"keyword": username, "limit": 10},
            timeout=10,
        )
        if response.status_code in BLOCKED_CODES:
            return {
                "site": "Roblox",
                "url": url,
                "final_url": url,
                "status": response.status_code,
                "result": "Blocked",
            }
        if response.status_code != 200:
            return {
                "site": "Roblox",
                "url": url,
                "final_url": url,
                "status": response.status_code,
                "result": "Unknown",
            }

        data = response.json().get("data", [])
        exact = next(
            (item for item in data if str(item.get("name", "")).lower() == username.lower()),
            None,
        )
        if exact:
            profile_url = f"https://www.roblox.com/users/{exact['id']}/profile"
            return {
                "site": "Roblox",
                "url": url,
                "final_url": profile_url,
                "status": response.status_code,
                "result": "Found",
                "title": exact.get("displayName") or exact.get("name"),
            }

        return {
            "site": "Roblox",
            "url": url,
            "final_url": url,
            "status": response.status_code,
            "result": "Not Found",
        }
    except (requests.RequestException, ValueError) as exc:
        return {
            "site": "Roblox",
            "url": url,
            "error": str(exc),
            "result": "Unknown",
        }

def check_public_profile(session, site, template, username):
    if site == "Roblox":
        return check_roblox(session, username)

    url = template.format(username=quote(username, safe="._-"))
    try:
        response = session.get(url, timeout=10, allow_redirects=True)
        result = classify_response(site, username, response)
        return {
            "site": site,
            "url": url,
            "final_url": response.url,
            "status": response.status_code,
            "result": result,
            "title": extract_title(response.text[:200_000]) if result == "Found" else None,
            "content_type": response.headers.get("Content-Type"),
        }
    except requests.RequestException as exc:
        return {
            "site": site,
            "url": url,
            "error": str(exc),
            "result": "Unknown",
        }

def run():
    module_header("Username Lookup", "OSINT")
    username = console.input("[bold white]Username:[/bold white] ").strip().lstrip("@")
    if not username:
        console.print("[red]Username is required.[/red]")
        pause()
        return

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36 VOID/1.0"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }
    )

    results = [
        check_public_profile(session, site, template, username)
        for site, template in SITES.items()
    ]

    table = Table(title=f"Public Social Profiles · {username}", border_style="red")
    table.add_column("Site", style="bold red")
    table.add_column("HTTP")
    table.add_column("Result")
    table.add_column("Title", style="white")
    table.add_column("URL")

    for item in results:
        table.add_row(
            item["site"],
            str(item.get("status") or "ERR"),
            item.get("result", "Unknown"),
            str(item.get("title") or item.get("error") or ""),
            item.get("final_url") or item["url"],
        )

    console.print(table)
    console.print(
        "[dim]Found means that public evidence matched the requested handle. "
        "Not Found means the public endpoint/page indicated no match. Blocked means the platform "
        "refused automated access. Unknown means VOID could not make a reliable determination. "
        "Matching usernames across services does not prove the accounts belong to the same person.[/dim]"
    )

    found = [item for item in results if item.get("result") == "Found"]
    console.print(f"[dim]Public profile matches: {len(found)}[/dim]")
    pause()
