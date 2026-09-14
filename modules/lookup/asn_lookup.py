import re

import requests
from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause


def normalize_asn(value):
    value = value.strip().upper()
    if value.startswith("AS"):
        value = value[2:]
    if not value.isdigit() or int(value) <= 0:
        raise ValueError
    return int(value)


def fetch_json(url):
    response = requests.get(url, timeout=15, headers={"User-Agent": "VOID/1.0"})
    response.raise_for_status()
    data = response.json()
    if data.get("status") not in (None, "ok"):
        raise ValueError(data.get("status_message") or "API request failed")
    return data.get("data", data)


def run():
    module_header("ASN Lookup", "OSINT")
    raw = console.input("[bold white]ASN:[/bold white] ").strip()
    try:
        asn = normalize_asn(raw)
    except ValueError:
        console.print("[red]Invalid ASN. Use a value such as AS13335 or 13335.[/red]")
        pause()
        return

    try:
        overview = fetch_json(f"https://api.bgpview.io/asn/{asn}")
        prefixes = fetch_json(f"https://api.bgpview.io/asn/{asn}/prefixes")
        peers = fetch_json(f"https://api.bgpview.io/asn/{asn}/peers")
    except (requests.RequestException, ValueError) as exc:
        console.print(f"[red]ASN lookup failed: {exc}[/red]")
        pause()
        return

    table = Table(title=f"ASN Intelligence · AS{asn}", show_header=False, border_style="red")
    table.add_column("Field", style="bold red")
    table.add_column("Value", style="white")
    table.add_row("ASN", f"AS{asn}")
    table.add_row("Name", str(overview.get("name") or "Unknown"))
    table.add_row("Description", str(overview.get("description_short") or overview.get("description_full") or "Unknown"))
    table.add_row("Country", str(overview.get("country_code") or "Unknown"))
    table.add_row("Website", str(overview.get("website") or "Unknown"))
    table.add_row("Email", str(overview.get("email_contacts") or "Unknown"))
    table.add_row("Abuse Contacts", str(overview.get("abuse_contacts") or "Unknown"))
    table.add_row("Traffic Estimation", str(overview.get("traffic_estimation") or "Unknown"))
    table.add_row("Traffic Ratio", str(overview.get("traffic_ratio") or "Unknown"))
    table.add_row("Owner Address", str(overview.get("owner_address") or "Unknown"))
    console.print(table)

    ipv4 = prefixes.get("ipv4_prefixes") or []
    ipv6 = prefixes.get("ipv6_prefixes") or []
    prefix_table = Table(title="Announced Prefixes", border_style="red")
    prefix_table.add_column("Family", style="bold red")
    prefix_table.add_column("Prefix", style="white")
    prefix_table.add_column("Name")
    prefix_table.add_column("Description")
    prefix_table.add_column("Country")
    for family, items in (("IPv4", ipv4), ("IPv6", ipv6)):
        for item in items[:100]:
            prefix_table.add_row(
                family,
                str(item.get("prefix") or ""),
                str(item.get("name") or ""),
                str(item.get("description") or ""),
                str(item.get("country_code") or ""),
            )
    if prefix_table.row_count:
        console.print(prefix_table)

    peer4 = peers.get("ipv4_peers") or []
    peer6 = peers.get("ipv6_peers") or []
    peer_table = Table(title="BGP Peers", border_style="red")
    peer_table.add_column("Family", style="bold red")
    peer_table.add_column("ASN", style="white")
    peer_table.add_column("Name")
    peer_table.add_column("Description")
    peer_table.add_column("Country")
    seen = set()
    for family, items in (("IPv4", peer4), ("IPv6", peer6)):
        for item in items[:100]:
            key = (family, item.get("asn"))
            if key in seen:
                continue
            seen.add(key)
            peer_table.add_row(
                family,
                f"AS{item.get('asn')}" if item.get("asn") else "",
                str(item.get("name") or ""),
                str(item.get("description") or ""),
                str(item.get("country_code") or ""),
            )
    if peer_table.row_count:
        console.print(peer_table)

    log_data = {
        "overview": overview,
        "ipv4_prefixes": ipv4,
        "ipv6_prefixes": ipv6,
        "ipv4_peers": peer4,
        "ipv6_peers": peer6,
    }
    path = save_log("asn_lookup", f"AS{asn}", log_data)
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
