MADE_BY = "Made by unbeau"

import requests
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from core.ui import console, module_header, pause
from core.validators import normalize_domain
from core.config import CONFIG
from core.logger import save_log

def run():
    module_header("CERTIFICATE TRANSPARENCY", "OSINT / Lookup")
    domain = normalize_domain(Prompt.ask("[red]Domain[/red]"))
    try:
        response = requests.get("https://crt.sh/", params={"q": f"%.{domain}", "output": "json"}, timeout=max(CONFIG["request_timeout"], 15))
        data = response.json()
        names = []
        seen = set()
        for item in data:
            for name in str(item.get("name_value", "")).splitlines():
                name = name.strip().lower()
                if name and name not in seen:
                    seen.add(name)
                    names.append(name)
        table = Table(box=box.SIMPLE)
        table.add_column("Certificate Name", style="white")
        for name in names[:150]:
            table.add_row(name)
        console.print(table)
        console.print(f"\nUnique names: [bold]{len(names)}[/bold]")
        save_log("certificate_transparency", domain, {"names": names})
    except Exception as e:
        console.print(f"[red]Lookup error: {e}[/red]")
    pause()
