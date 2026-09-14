from urllib.parse import urljoin, urlparse

import requests
from rich.panel import Panel
from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause


def normalize_url(value):
    value = value.strip()
    if not value.startswith(("http://", "https://")):
        value = "https://" + value
    return value


def classify_redirect(source, destination):
    source_host = urlparse(source).hostname or ""
    destination_host = urlparse(destination).hostname or ""
    source_scheme = urlparse(source).scheme
    destination_scheme = urlparse(destination).scheme
    changes = []
    if source_host.lower() != destination_host.lower():
        changes.append("cross-host")
    if source_scheme != destination_scheme:
        changes.append(f"{source_scheme}->{destination_scheme}")
    return ", ".join(changes) or "same-origin"


def run():
    module_header("Redirect Lookup", "Web")
    target = normalize_url(console.input("[bold white]URL:[/bold white] "))

    session = requests.Session()
    session.headers.update({"User-Agent": "VOID/1.0"})
    chain = []
    current = target
    visited = set()

    try:
        for index in range(15):
            if current in visited:
                chain.append({"index": index + 1, "url": current, "loop": True})
                break
            visited.add(current)
            response = session.get(current, timeout=15, allow_redirects=False)
            location = response.headers.get("Location")
            destination = urljoin(current, location) if location else None
            chain.append({
                "index": index + 1,
                "url": current,
                "status": response.status_code,
                "reason": response.reason,
                "location": location,
                "destination": destination,
                "classification": classify_redirect(current, destination) if destination else "final",
                "server": response.headers.get("Server"),
                "cache_control": response.headers.get("Cache-Control"),
                "hsts": response.headers.get("Strict-Transport-Security"),
            })
            if response.status_code not in {301, 302, 303, 307, 308} or not destination:
                break
            current = destination
    except requests.RequestException as exc:
        console.print(f"[red]Redirect lookup failed: {exc}[/red]")
        pause()
        return

    table = Table(title="Redirect Chain", border_style="red")
    table.add_column("#", style="bold red", justify="right")
    table.add_column("Status")
    table.add_column("URL", style="white")
    table.add_column("Destination")
    table.add_column("Change")
    for item in chain:
        if item.get("loop"):
            table.add_row(str(item["index"]), "LOOP", item["url"], "-", "redirect loop")
            continue
        table.add_row(
            str(item["index"]),
            str(item.get("status") or ""),
            item.get("url") or "",
            item.get("destination") or "Final response",
            item.get("classification") or "",
        )
    console.print(table)

    final = chain[-1] if chain else {}
    findings = []
    if any(item.get("loop") for item in chain):
        findings.append("Redirect loop detected")
    if len(chain) > 6:
        findings.append("Long redirect chain")
    for item in chain:
        if item.get("classification") == "https->http":
            findings.append("HTTPS downgrade detected")
        if "cross-host" in str(item.get("classification")):
            findings.append(f"Cross-host redirect: {item.get('url')} -> {item.get('destination')}")
    if findings:
        console.print(Panel("\n".join(dict.fromkeys(findings)), title="Findings", border_style="yellow"))

    path = save_log("redirect_lookup", target, {"chain": chain, "findings": list(dict.fromkeys(findings))})
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
