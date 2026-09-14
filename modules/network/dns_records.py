MADE_BY = "Made by unbeau"

import dns.resolver
from rich.table import Table
from rich import box
from rich.prompt import Prompt
from core.ui import console, module_header, pause
from core.validators import normalize_domain
from core.logger import save_log

def run():
    module_header("DNS RECORD LOOKUP", "Network")
    domain = normalize_domain(Prompt.ask("[red]Domain[/red]"))
    types = ["A", "AAAA", "MX", "TXT", "NS"]
    result = {}
    table = Table(box=box.SIMPLE)
    table.add_column("Type", style="red")
    table.add_column("Value")
    for rtype in types:
        try:
            answers = dns.resolver.resolve(domain, rtype)
            values = [str(x) for x in answers]
            result[rtype] = values
            for value in values:
                table.add_row(rtype, value)
        except Exception:
            result[rtype] = []
    console.print(table)
    save_log("dns_records", domain, result)
    pause()
