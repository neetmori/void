from urllib.parse import urljoin

import requests
from rich.panel import Panel
from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause

PATHS = ["/.well-known/security.txt", "/security.txt"]


def normalize_origin(value):
    value = value.strip()
    if not value.startswith(("http://", "https://")):
        value = "https://" + value
    parsed = requests.utils.urlparse(value)
    return f"{parsed.scheme}://{parsed.netloc}"


def parse_security_txt(text):
    fields = {}
    comments = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            comments.append(line[1:].strip())
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields.setdefault(key.strip(), []).append(value.strip())
    return fields, comments


def run():
    module_header("security.txt Lookup", "Web")
    origin = normalize_origin(console.input("[bold white]Domain or URL:[/bold white] "))
    found = None
    attempts = []

    for path in PATHS:
        url = urljoin(origin, path)
        try:
            response = requests.get(url, timeout=12, allow_redirects=True, headers={"User-Agent": "VOID/1.0"})
            attempts.append({"url": url, "status": response.status_code, "final_url": response.url, "content_type": response.headers.get("Content-Type")})
            if response.status_code == 200 and response.text.strip():
                found = response
                break
        except requests.RequestException as exc:
            attempts.append({"url": url, "error": str(exc)})

    if not found:
        console.print(Panel("No published security.txt file was found at the standard locations.", border_style="yellow"))
        path = save_log("security_txt_lookup", origin, {"attempts": attempts})
        console.print(f"[dim]Log saved to {path}[/dim]")
        pause()
        return

    fields, comments = parse_security_txt(found.text)
    table = Table(title=f"security.txt · {found.url}", border_style="red")
    table.add_column("Field", style="bold red")
    table.add_column("Value", style="white")
    preferred_order = ["Contact", "Expires", "Encryption", "Acknowledgments", "Preferred-Languages", "Canonical", "Policy", "Hiring"]
    ordered = preferred_order + sorted(key for key in fields if key not in preferred_order)
    for key in ordered:
        values = fields.get(key)
        if values:
            table.add_row(key, "\n".join(values))
    console.print(table)

    expiry = (fields.get("Expires") or [None])[0]
    canonical = fields.get("Canonical") or []
    contacts = fields.get("Contact") or []
    summary = Table(title="Publication Summary", show_header=False, border_style="red")
    summary.add_column("Field", style="bold red")
    summary.add_column("Value", style="white")
    summary.add_row("Requested Origin", origin)
    summary.add_row("Published URL", found.url)
    summary.add_row("HTTP Status", str(found.status_code))
    summary.add_row("Content Type", found.headers.get("Content-Type", "Not provided"))
    summary.add_row("Contacts", str(len(contacts)))
    summary.add_row("Canonical URLs", str(len(canonical)))
    summary.add_row("Expires", str(expiry or "Not provided"))
    console.print(summary)

    path = save_log("security_txt_lookup", origin, {"url": found.url, "fields": fields, "comments": comments, "attempts": attempts, "raw": found.text})
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
