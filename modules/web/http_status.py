import time
from urllib.parse import urlparse

import requests
from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause


def normalize_url(value):
    value = value.strip()
    if not value.startswith(("http://", "https://")):
        value = "https://" + value
    return value


def run():
    module_header("HTTP Status Check", "Web")
    target = normalize_url(console.input("[bold white]URL:[/bold white] "))
    started = time.perf_counter()
    try:
        response = requests.get(target, timeout=15, allow_redirects=True, headers={"User-Agent": "VOID/1.0"})
    except requests.RequestException as exc:
        console.print(f"[red]Request failed: {exc}[/red]")
        pause()
        return
    elapsed_ms = (time.perf_counter() - started) * 1000

    table = Table(title="HTTP Diagnostics", show_header=False, border_style="red")
    table.add_column("Field", style="bold red")
    table.add_column("Value", style="white")
    table.add_row("Requested URL", target)
    table.add_row("Final URL", response.url)
    table.add_row("Status", f"{response.status_code} {response.reason}")
    table.add_row("Elapsed", f"{elapsed_ms:.2f} ms")
    table.add_row("Redirects", str(len(response.history)))
    table.add_row("Scheme", urlparse(response.url).scheme)
    table.add_row("Host", str(urlparse(response.url).hostname or ""))
    table.add_row("HTTP Version", f"HTTP/{response.raw.version / 10:.1f}" if response.raw.version else "Unknown")
    table.add_row("Content Type", response.headers.get("Content-Type", "Not provided"))
    table.add_row("Content Encoding", response.headers.get("Content-Encoding", "Not provided"))
    table.add_row("Reported Length", response.headers.get("Content-Length", "Not provided"))
    table.add_row("Received Bytes", str(len(response.content)))
    table.add_row("Server", response.headers.get("Server", "Not disclosed"))
    table.add_row("Date", response.headers.get("Date", "Not provided"))
    table.add_row("Cache Control", response.headers.get("Cache-Control", "Not provided"))
    console.print(table)

    redirects = [
        {
            "status": item.status_code,
            "url": item.url,
            "location": item.headers.get("Location"),
        }
        for item in response.history
    ]
    if redirects:
        redirect_table = Table(title="Redirects", border_style="red")
        redirect_table.add_column("Status", style="bold red")
        redirect_table.add_column("URL", style="white")
        redirect_table.add_column("Location")
        for item in redirects:
            redirect_table.add_row(str(item["status"]), item["url"], str(item["location"] or ""))
        console.print(redirect_table)

    path = save_log(
        "http_status",
        target,
        {
            "final_url": response.url,
            "status": response.status_code,
            "reason": response.reason,
            "elapsed_ms": elapsed_ms,
            "redirects": redirects,
            "headers": dict(response.headers),
            "received_bytes": len(response.content),
        },
    )
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
