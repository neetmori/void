MADE_BY = "Made by unbeau"

import requests
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from core.ui import console, module_header, pause
from core.validators import ensure_url
from core.config import CONFIG
from core.logger import save_log

def run():
    module_header("REDIRECT LOOKUP", "Web / Lookup")
    url = ensure_url(Prompt.ask("[red]URL[/red]"))
    try:
        response = requests.get(url, timeout=CONFIG["request_timeout"], allow_redirects=True)
        chain = [{"status": x.status_code, "url": x.url, "location": x.headers.get("Location")} for x in response.history]
        chain.append({"status": response.status_code, "url": response.url, "location": None})
        table = Table(box=box.SIMPLE)
        table.add_column("#", style="red")
        table.add_column("Status")
        table.add_column("URL")
        for i, item in enumerate(chain, 1):
            table.add_row(str(i), str(item["status"]), item["url"])
        console.print(table)
        save_log("redirect_lookup", url, chain)
    except Exception as e:
        console.print(f"[red]Lookup error: {e}[/red]")
    pause()
