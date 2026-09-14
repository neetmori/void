MADE_BY = "Made by unbeau"

import whois
from rich.table import Table
from rich import box
from rich.prompt import Prompt
from core.ui import console, module_header, pause
from core.logger import save_log
from core.validators import normalize_domain

def run():
    module_header("DOMAIN WHOIS", "OSINT")
    domain = normalize_domain(Prompt.ask("[red]Domain[/red]"))
    try:
        data = whois.whois(domain)
        fields = ["domain_name", "registrar", "creation_date", "expiration_date", "updated_date", "name_servers", "status"]
        table = Table(box=box.SIMPLE)
        table.add_column("Field", style="red")
        table.add_column("Value")
        result = {}
        for field in fields:
            value = data.get(field)
            result[field] = value
            table.add_row(field, str(value or "-"))
        console.print(table)
        save_log("whois", domain, result)
    except Exception as e:
        console.print(f"[red]WHOIS error: {e}[/red]")
    pause()
