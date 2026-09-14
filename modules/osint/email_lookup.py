MADE_BY = "Made by unbeau"

import socket
import dns.resolver
from rich.table import Table
from rich import box
from rich.prompt import Prompt
from core.ui import console, module_header, pause
from core.logger import save_log
from core.validators import valid_email

def run():
    module_header("EMAIL LOOKUP", "OSINT")
    email = Prompt.ask("[red]Email[/red]").strip()
    if not valid_email(email):
        console.print("[red]Invalid email format.[/red]")
        pause()
        return
    local, domain = email.rsplit("@", 1)
    result = {"email": email, "local_part": local, "domain": domain, "domain_ips": [], "mx_records": []}
    table = Table(box=box.SIMPLE)
    table.add_column("Field", style="red")
    table.add_column("Value")
    table.add_row("Email", email)
    table.add_row("Local Part", local)
    table.add_row("Domain", domain)
    try:
        ips = socket.gethostbyname_ex(domain)[2]
        result["domain_ips"] = ips
        for ip in ips:
            table.add_row("Domain IP", ip)
    except Exception:
        pass
    try:
        records = dns.resolver.resolve(domain, "MX")
        mx = [str(record.exchange).rstrip(".") for record in records]
        result["mx_records"] = mx
        for item in mx:
            table.add_row("MX", item)
    except Exception:
        table.add_row("MX", "Not found")
    console.print(table)
    console.print("\n[dim]This module analyzes public domain infrastructure and does not access mailboxes.[/dim]")
    save_log("email_lookup", email, result)
    pause()
