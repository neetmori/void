import ipaddress
import socket

import dns.exception
import dns.resolver
from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause


def run():
    module_header("Reverse DNS", "Network")
    target = console.input("[bold white]IP address:[/bold white] ").strip()
    try:
        ip = ipaddress.ip_address(target)
    except ValueError:
        console.print("[red]Invalid IP address.[/red]")
        pause()
        return

    result = {
        "ip": str(ip),
        "version": ip.version,
        "reverse_pointer": ip.reverse_pointer,
        "hostname": None,
        "aliases": [],
        "addresses": [],
        "ptr_records": [],
    }

    try:
        hostname, aliases, addresses = socket.gethostbyaddr(str(ip))
        result["hostname"] = hostname
        result["aliases"] = aliases
        result["addresses"] = addresses
    except OSError:
        pass

    try:
        answer = dns.resolver.resolve(ip.reverse_pointer, "PTR", lifetime=6)
        result["ptr_records"] = [item.to_text().rstrip(".") for item in answer]
        result["ttl"] = answer.rrset.ttl if answer.rrset else None
    except dns.exception.DNSException as exc:
        result["dns_error"] = str(exc)

    forward_checks = {}
    for hostname in list(dict.fromkeys(([result["hostname"]] if result["hostname"] else []) + result["ptr_records"])):
        try:
            info = socket.getaddrinfo(hostname, None)
            resolved = sorted({item[4][0] for item in info})
            forward_checks[hostname] = {
                "addresses": resolved,
                "contains_original": str(ip) in resolved,
            }
        except OSError as exc:
            forward_checks[hostname] = {"error": str(exc), "contains_original": False}
    result["forward_checks"] = forward_checks

    table = Table(title=f"Reverse DNS · {ip}", show_header=False, border_style="red")
    table.add_column("Field", style="bold red")
    table.add_column("Value", style="white")
    table.add_row("IP Version", str(ip.version))
    table.add_row("Reverse Pointer", ip.reverse_pointer)
    table.add_row("Socket Hostname", result["hostname"] or "Not resolved")
    table.add_row("Aliases", "\n".join(result["aliases"]) or "None")
    table.add_row("PTR Records", "\n".join(result["ptr_records"]) or "None")
    table.add_row("PTR TTL", str(result.get("ttl") or "Unknown"))
    table.add_row("Forward Confirmed", "\n".join(f"{host}: {data.get('contains_original', False)}" for host, data in forward_checks.items()) or "Not available")
    console.print(table)

    path = save_log("reverse_dns", str(ip), result)
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
