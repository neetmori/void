MADE_BY = "Made by unbeau"

import dns.resolver
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from core.ui import console, module_header, pause
from core.validators import normalize_domain
from core.logger import save_log

def run():
    module_header("ADVANCED DNS LOOKUP", "OSINT / Lookup")
    domain = normalize_domain(Prompt.ask("[red]Domain[/red]"))
    types = ["A", "AAAA", "CNAME", "MX", "TXT", "NS", "SOA", "CAA"]
    result = {}
    table = Table(box=box.SIMPLE)
    table.add_column("Type", style="red")
    table.add_column("Value")
    for kind in types:
        try:
            values = [str(x) for x in dns.resolver.resolve(domain, kind)]
        except Exception:
            values = []
        result[kind] = values
        for value in values:
            table.add_row(kind, value)
    console.print(table)
    save_log("advanced_dns", domain, result)
    pause()
