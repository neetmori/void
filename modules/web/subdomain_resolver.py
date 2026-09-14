MADE_BY = "Made by unbeau"

import socket
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from core.ui import console, module_header, pause
from core.validators import normalize_domain
from core.config import CONFIG
from core.logger import save_log

def run():
    module_header("SUBDOMAIN RESOLVER", "Web Recon")
    domain = normalize_domain(Prompt.ask("[red]Domain[/red]"))
    table = Table(box=box.SIMPLE)
    table.add_column("Subdomain")
    table.add_column("IP")
    found = []
    for sub in CONFIG["subdomains"]:
        hostname = f"{sub}.{domain}"
        try:
            ip = socket.gethostbyname(hostname)
            table.add_row(hostname, ip)
            found.append({"hostname": hostname, "ip": ip})
        except socket.gaierror:
            pass
    console.print(table)
    console.print(f"\nFound: [bold]{len(found)}[/bold]")
    save_log("subdomain_resolver", domain, found)
    pause()
