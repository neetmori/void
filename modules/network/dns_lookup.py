MADE_BY = "Made by unbeau"

import socket
from rich.table import Table
from rich import box
from rich.prompt import Prompt
from core.ui import console, module_header, pause
from core.logger import save_log
from core.validators import normalize_domain

def run():
    module_header("DNS LOOKUP", "Network")
    domain = normalize_domain(Prompt.ask("[red]Domain[/red]"))
    try:
        host, aliases, addresses = socket.gethostbyname_ex(domain)
        table = Table(box=box.SIMPLE)
        table.add_column("Type", style="red")
        table.add_column("Value")
        table.add_row("Hostname", host)
        for address in addresses:
            table.add_row("IPv4", address)
        console.print(table)
        save_log("dns_lookup", domain, {"hostname": host, "aliases": aliases, "addresses": addresses})
    except Exception as e:
        console.print(f"[red]DNS error: {e}[/red]")
    pause()
