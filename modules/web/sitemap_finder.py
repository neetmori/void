MADE_BY = "Made by unbeau"

import requests
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from core.ui import console, module_header, pause
from core.validators import ensure_url
from core.config import CONFIG

def run():
    module_header("SITEMAP FINDER", "Web")
    base = ensure_url(Prompt.ask("[red]Website[/red]")).rstrip("/")
    paths = ["/sitemap.xml", "/sitemap_index.xml", "/sitemap.txt"]
    table = Table(box=box.SIMPLE)
    table.add_column("URL")
    table.add_column("Status")
    for path in paths:
        url = base + path
        try:
            response = requests.get(url, timeout=CONFIG["request_timeout"])
            table.add_row(url, str(response.status_code))
        except Exception:
            table.add_row(url, "ERROR")
    console.print(table)
    pause()
