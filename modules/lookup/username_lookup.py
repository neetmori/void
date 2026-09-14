MADE_BY = "Made by unbeau"

import requests
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from core.ui import console, module_header, pause
from core.config import CONFIG
from core.logger import save_log

def run():
    module_header("USERNAME LOOKUP", "OSINT / Lookup")
    username = Prompt.ask("[red]Username[/red]").strip()
    table = Table(box=box.SIMPLE)
    table.add_column("Platform", style="red")
    table.add_column("Status")
    table.add_column("URL")
    results = []
    headers = {"User-Agent": "VOID-OSINT/3.1"}
    for name, template in CONFIG.get("username_sites", {}).items():
        url = template.format(username=username)
        try:
            response = requests.get(url, headers=headers, timeout=CONFIG["request_timeout"], allow_redirects=True)
            found = response.status_code == 200
            status = "FOUND" if found else "NOT FOUND"
        except Exception:
            found = False
            status = "ERROR"
        table.add_row(name, status, url)
        results.append({"platform": name, "url": url, "status": status})
    console.print(table)
    save_log("username_lookup", username, results)
    pause()
