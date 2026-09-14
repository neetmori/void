MADE_BY = "Made by unbeau"

import socket
import requests
import dns.resolver
import whois
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from core.ui import console, module_header, pause
from core.validators import normalize_domain
from core.logger import save_log

def run():
    module_header("DOMAIN LOOKUP", "OSINT / Lookup")
    domain = normalize_domain(Prompt.ask("[red]Domain[/red]"))
    result = {"domain": domain}
    try:
        result["addresses"] = socket.gethostbyname_ex(domain)[2]
    except Exception:
        result["addresses"] = []
    for record_type in ["MX", "NS", "TXT"]:
        try:
            result[record_type.lower()] = [str(x) for x in dns.resolver.resolve(domain, record_type)]
        except Exception:
            result[record_type.lower()] = []
    try:
        data = whois.whois(domain)
        result["registrar"] = data.get("registrar")
        result["creation_date"] = data.get("creation_date")
        result["expiration_date"] = data.get("expiration_date")
    except Exception:
        result["registrar"] = None
        result["creation_date"] = None
        result["expiration_date"] = None
    table = Table(box=box.SIMPLE)
    table.add_column("Field", style="red")
    table.add_column("Value")
    for key, value in result.items():
        table.add_row(key.replace("_", " ").title(), str(value or "-"))
    console.print(table)
    save_log("domain_lookup", domain, result)
    pause()
