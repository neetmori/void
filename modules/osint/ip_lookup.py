import ipaddress
import socket

import requests
from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause


def classify_ip(value):
    ip = ipaddress.ip_address(value)
    return {
        "version": ip.version,
        "private": ip.is_private,
        "global": ip.is_global,
        "loopback": ip.is_loopback,
        "link_local": ip.is_link_local,
        "multicast": ip.is_multicast,
        "reserved": ip.is_reserved,
        "unspecified": ip.is_unspecified,
        "reverse_pointer": ip.reverse_pointer,
    }


def reverse_dns(value):
    try:
        host, aliases, addresses = socket.gethostbyaddr(value)
        return {"hostname": host, "aliases": aliases, "addresses": addresses}
    except OSError:
        return {"hostname": None, "aliases": [], "addresses": []}


def fetch_public_data(value):
    response = requests.get(f"https://ipwho.is/{value}", timeout=12, headers={"User-Agent": "VOID/1.0"})
    response.raise_for_status()
    data = response.json()
    if not data.get("success", True):
        raise ValueError(data.get("message") or "Public IP service rejected the query")
    return data


def add_row(table, label, value):
    if value not in (None, "", [], {}):
        table.add_row(label, str(value))


def run():
    module_header("IP Lookup", "OSINT")
    target = console.input("[bold white]IP address:[/bold white] ").strip()
    try:
        classification = classify_ip(target)
    except ValueError:
        console.print("[red]Invalid IP address.[/red]")
        pause()
        return

    rdns = reverse_dns(target)
    public_data = {}
    if classification["global"]:
        try:
            public_data = fetch_public_data(target)
        except (requests.RequestException, ValueError) as exc:
            public_data = {"error": str(exc)}

    table = Table(title=f"IP Intelligence · {target}", show_header=False, border_style="red")
    table.add_column("Field", style="bold red")
    table.add_column("Value", style="white")
    add_row(table, "IP Version", classification["version"])
    add_row(table, "Global", classification["global"])
    add_row(table, "Private", classification["private"])
    add_row(table, "Loopback", classification["loopback"])
    add_row(table, "Link Local", classification["link_local"])
    add_row(table, "Multicast", classification["multicast"])
    add_row(table, "Reserved", classification["reserved"])
    add_row(table, "Reverse Pointer", classification["reverse_pointer"])
    add_row(table, "Reverse DNS", rdns.get("hostname"))
    add_row(table, "Reverse DNS Aliases", ", ".join(rdns.get("aliases") or []))

    if public_data and "error" not in public_data:
        connection = public_data.get("connection") or {}
        timezone = public_data.get("timezone") or {}
        security = public_data.get("security") or {}
        add_row(table, "Country", public_data.get("country"))
        add_row(table, "Country Code", public_data.get("country_code"))
        add_row(table, "Continent", public_data.get("continent"))
        add_row(table, "Region", public_data.get("region"))
        add_row(table, "City", public_data.get("city"))
        add_row(table, "Postal Code", public_data.get("postal"))
        add_row(table, "Latitude", public_data.get("latitude"))
        add_row(table, "Longitude", public_data.get("longitude"))
        add_row(table, "ASN", connection.get("asn"))
        add_row(table, "Organization", connection.get("org"))
        add_row(table, "ISP", connection.get("isp"))
        add_row(table, "Domain", connection.get("domain"))
        add_row(table, "Timezone", timezone.get("id"))
        add_row(table, "UTC Offset", timezone.get("utc"))
        add_row(table, "Proxy", security.get("proxy"))
        add_row(table, "VPN", security.get("vpn"))
        add_row(table, "Tor", security.get("tor"))
    elif public_data.get("error"):
        add_row(table, "Public Data Error", public_data["error"])

    console.print(table)
    path = save_log("ip_lookup", target, {"classification": classification, "reverse_dns": rdns, "public_data": public_data})
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
