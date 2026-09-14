MADE_BY = "Made by unbeau"

import requests
from rich.table import Table
from rich import box
from rich.prompt import Prompt
from core.ui import console, module_header, pause
from core.logger import save_log
from core.validators import valid_ip
from core.config import CONFIG

def run():
    module_header("IP LOOKUP", "OSINT")
    target = Prompt.ask("[red]IP[/red]").strip()
    if not valid_ip(target):
        console.print("[red]Invalid IP address.[/red]")
        pause()
        return
    try:
        response = requests.get(f"https://ipwho.is/{target}", timeout=CONFIG["request_timeout"])
        data = response.json()
        if not data.get("success", True):
            console.print("[red]Lookup failed.[/red]")
            pause()
            return
        fields = {
            "IP": data.get("ip"),
            "Type": data.get("type"),
            "Continent": data.get("continent"),
            "Country": data.get("country"),
            "Region": data.get("region"),
            "City": data.get("city"),
            "Latitude": data.get("latitude"),
            "Longitude": data.get("longitude"),
            "Timezone": data.get("timezone", {}).get("id"),
            "ISP": data.get("connection", {}).get("isp"),
            "ASN": data.get("connection", {}).get("asn"),
            "Organization": data.get("connection", {}).get("org")
        }
        table = Table(box=box.SIMPLE)
        table.add_column("Field", style="red")
        table.add_column("Value")
        for key, value in fields.items():
            table.add_row(key, str(value or "-"))
        console.print(table)
        console.print(f"\n[dim]Log: {save_log('ip_lookup', target, data)}[/dim]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    pause()
