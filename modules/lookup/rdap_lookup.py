MADE_BY = "Made by unbeau"

import requests
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from core.ui import console, module_header, pause
from core.config import CONFIG
from core.logger import save_log

def run():
    module_header("RDAP LOOKUP", "OSINT / Lookup")
    value = Prompt.ask("[red]Domain or IP[/red]").strip()
    url = f"https://rdap.org/domain/{value}" if "." in value and not value.replace(".", "").isdigit() else f"https://rdap.org/ip/{value}"
    try:
        response = requests.get(url, timeout=CONFIG["request_timeout"])
        if response.status_code >= 400:
            console.print(f"[red]RDAP error: HTTP {response.status_code}[/red]")
            pause()
            return
        data = response.json()
        result = {
            "handle": data.get("handle"),
            "name": data.get("name"),
            "type": data.get("objectClassName"),
            "startAddress": data.get("startAddress"),
            "endAddress": data.get("endAddress"),
            "port43": data.get("port43")
        }
        table = Table(box=box.SIMPLE)
        table.add_column("Field", style="red")
        table.add_column("Value")
        for k, v in result.items():
            table.add_row(k, str(v or "-"))
        console.print(table)
        save_log("rdap_lookup", value, result)
    except Exception as e:
        console.print(f"[red]Lookup error: {e}[/red]")
    pause()
