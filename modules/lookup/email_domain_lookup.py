MADE_BY = "Made by unbeau"

import dns.resolver
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from core.ui import console, module_header, pause
from core.validators import valid_email, normalize_domain
from core.logger import save_log

def get_records(domain, kind):
    try:
        return [str(x) for x in dns.resolver.resolve(domain, kind)]
    except Exception:
        return []

def run():
    module_header("EMAIL DOMAIN LOOKUP", "OSINT / Lookup")
    value = Prompt.ask("[red]Email or domain[/red]").strip()
    domain = value.rsplit("@", 1)[1] if "@" in value else normalize_domain(value)
    if "@" in value and not valid_email(value):
        console.print("[red]Invalid email format.[/red]")
        pause()
        return
    mx = get_records(domain, "MX")
    txt = get_records(domain, "TXT")
    dmarc = get_records(f"_dmarc.{domain}", "TXT")
    spf = [x for x in txt if "v=spf1" in x.lower()]
    result = {"domain": domain, "mx": mx, "spf": spf, "dmarc": dmarc}
    table = Table(box=box.SIMPLE)
    table.add_column("Type", style="red")
    table.add_column("Value")
    for key in ["mx", "spf", "dmarc"]:
        values = result[key] or ["Not found"]
        for item in values:
            table.add_row(key.upper(), item)
    console.print(table)
    save_log("email_domain_lookup", value, result)
    pause()
