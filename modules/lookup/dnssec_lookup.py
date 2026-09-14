MADE_BY = "Made by unbeau"

import dns.resolver
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from core.ui import console, module_header, pause
from core.validators import normalize_domain
from core.logger import save_log

def run():
    module_header("DNSSEC LOOKUP", "OSINT / Lookup")
    domain = normalize_domain(Prompt.ask("[red]Domain[/red]"))
    result = {}
    for kind in ["DNSKEY", "DS"]:
        try:
            result[kind] = [str(x) for x in dns.resolver.resolve(domain, kind)]
        except Exception:
            result[kind] = []
    table = Table(box=box.SIMPLE)
    table.add_column("Type", style="red")
    table.add_column("Value")
    for kind, values in result.items():
        if values:
            for value in values:
                table.add_row(kind, value)
        else:
            table.add_row(kind, "Not found")
    console.print(table)
    save_log("dnssec_lookup", domain, result)
    pause()
