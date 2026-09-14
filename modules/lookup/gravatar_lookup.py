import hashlib

import requests
from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause


def run():
    module_header("Gravatar Lookup", "OSINT")
    email = console.input("[bold white]Email:[/bold white] ").strip().lower()
    if "@" not in email:
        console.print("[red]Invalid email address.[/red]")
        pause()
        return

    digest = hashlib.md5(email.encode("utf-8")).hexdigest()
    avatar_url = f"https://www.gravatar.com/avatar/{digest}"
    profile_url = f"https://www.gravatar.com/{digest}.json"

    try:
        avatar_response = requests.get(avatar_url, params={"d": "404", "s": "200"}, timeout=12, headers={"User-Agent": "VOID/1.0"})
        avatar_exists = avatar_response.status_code == 200
        profile_response = requests.get(profile_url, timeout=12, headers={"User-Agent": "VOID/1.0"})
        profile = profile_response.json() if profile_response.status_code == 200 else {}
    except (requests.RequestException, ValueError) as exc:
        console.print(f"[red]Gravatar lookup failed: {exc}[/red]")
        pause()
        return

    entry = (profile.get("entry") or [{}])[0] if profile else {}
    table = Table(title="Gravatar Public Profile", show_header=False, border_style="red")
    table.add_column("Field", style="bold red")
    table.add_column("Value", style="white")
    table.add_row("Email Hash", digest)
    table.add_row("Avatar Exists", str(avatar_exists))
    table.add_row("Avatar URL", avatar_url if avatar_exists else "Not published")
    fields = [
        ("Display Name", entry.get("displayName")),
        ("Preferred Username", entry.get("preferredUsername")),
        ("Profile URL", entry.get("profileUrl")),
        ("About", entry.get("aboutMe")),
        ("Current Location", entry.get("currentLocation")),
        ("Thumbnail", entry.get("thumbnailUrl")),
    ]
    for label, value in fields:
        if value not in (None, ""):
            table.add_row(label, str(value))

    accounts = []
    for account in entry.get("accounts") or []:
        item = f"{account.get('shortname') or account.get('domain') or 'account'}: {account.get('url') or account.get('username') or ''}"
        accounts.append(item)
    if accounts:
        table.add_row("Public Accounts", "\n".join(accounts))

    urls = []
    for url in entry.get("urls") or []:
        urls.append(f"{url.get('title') or 'URL'}: {url.get('value') or ''}")
    if urls:
        table.add_row("Public URLs", "\n".join(urls))

    photos = [photo.get("value") for photo in entry.get("photos") or [] if photo.get("value")]
    if photos:
        table.add_row("Photos", "\n".join(photos))

    console.print(table)
    path = save_log("gravatar_lookup", email, {"hash": digest, "avatar_exists": avatar_exists, "avatar_url": avatar_url if avatar_exists else None, "profile": entry})
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
