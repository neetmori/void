import socket
from pathlib import Path

from rich.table import Table

from core.config import BASE_DIR
from core.logger import save_log
from core.ui import console, module_header, pause


def load_candidates():
    path = BASE_DIR / "wordlists" / "subdomains.txt"
    if not path.is_file():
        return []
    values = []
    for line in path.read_text(encoding="utf-8").splitlines():
        value = line.strip().lower()
        if value and not value.startswith("#") and value not in values:
            values.append(value)
    return values[:100]


def resolve_name(name):
    info = socket.getaddrinfo(name, None)
    ipv4 = sorted({item[4][0] for item in info if item[0] == socket.AF_INET})
    ipv6 = sorted({item[4][0] for item in info if item[0] == socket.AF_INET6})
    canonical = socket.getfqdn(name)
    return ipv4, ipv6, canonical


def run():
    module_header("Subdomain Resolver", "Web")
    domain = console.input("[bold white]Domain:[/bold white] ").strip().lower().rstrip(".")
    if not domain or "." not in domain:
        console.print("[red]A valid domain is required.[/red]")
        pause()
        return

    candidates = load_candidates()
    if not candidates:
        console.print("[red]No subdomain candidates are available in wordlists/subdomains.txt.[/red]")
        pause()
        return

    results = []
    for label in candidates:
        hostname = f"{label}.{domain}"
        try:
            ipv4, ipv6, canonical = resolve_name(hostname)
            if ipv4 or ipv6:
                results.append({"hostname": hostname, "ipv4": ipv4, "ipv6": ipv6, "canonical": canonical})
        except socket.gaierror:
            continue
        except OSError as exc:
            results.append({"hostname": hostname, "error": str(exc), "ipv4": [], "ipv6": [], "canonical": None})

    table = Table(title=f"Resolved Subdomains · {domain}", border_style="red")
    table.add_column("Hostname", style="bold white")
    table.add_column("IPv4")
    table.add_column("IPv6")
    table.add_column("Canonical Name")
    for item in results:
        if not item.get("ipv4") and not item.get("ipv6"):
            continue
        table.add_row(
            item["hostname"],
            "\n".join(item.get("ipv4") or []) or "-",
            "\n".join(item.get("ipv6") or []) or "-",
            str(item.get("canonical") or "-"),
        )
    if table.row_count:
        console.print(table)
    else:
        console.print("[yellow]No names from the bounded candidate list resolved.[/yellow]")

    path = save_log("subdomain_resolver", domain, {"candidates_checked": len(candidates), "resolved": results})
    console.print(f"[dim]Checked {len(candidates)} candidates. Resolved {sum(1 for item in results if item.get('ipv4') or item.get('ipv6'))}.[/dim]")
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
