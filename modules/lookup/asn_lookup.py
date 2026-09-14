MADE_BY = "Made by unbeau"

import requests
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from core.ui import console, module_header, pause
from core.config import CONFIG
from core.validators import valid_ip
from core.logger import save_log

def run():
    module_header("ASN LOOKUP", "OSINT / Lookup")
    target = Prompt.ask("[red]IP[/red]").strip()
    if not valid_ip(target):
        console.print("[red]Invalid IP address.[/red]")
        pause()
        return
    try:
        data = requests.get(f"https://ipwho.is/{target}", timeout=CONFIG["request_timeout"]).json()
        connection = data.get("connection", {})
        result = {
            "ip": data.get("ip"),
            "asn": connection.get("asn"),
            "organization": connection.get("org"),
            "isp": connection.get("isp"),
            "domain": connection.get("domain"),
            "country": data.get("country")
        }
        table = Table(box=box.SIMPLE)
        table.add_column("Field", style="red")
        table.add_column("Value")
        for k, v in result.items():
            table.add_row(k.replace("_", " ").title(), str(v or "-"))
        console.print(table)
        save_log("asn_lookup", target, result)
    except Exception as e:
        console.print(f"[red]Lookup error: {e}[/red]")
    pause()
