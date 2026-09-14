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
    module_header("WEB HEADER ANALYZER", "Web")
    url = ensure_url(Prompt.ask("[red]URL[/red]"))
    headers_to_check = {
        "Strict-Transport-Security": "HSTS",
        "Content-Security-Policy": "CSP",
        "X-Frame-Options": "Frame protection",
        "X-Content-Type-Options": "MIME protection",
        "Referrer-Policy": "Referrer policy",
        "Permissions-Policy": "Permissions policy"
    }
    try:
        response = requests.get(url, timeout=CONFIG["request_timeout"], allow_redirects=True)
        table = Table(box=box.SIMPLE)
        table.add_column("Header")
        table.add_column("Status")
        table.add_column("Value")
        result = {}
        for header in headers_to_check:
            value = response.headers.get(header)
            result[header] = value
            table.add_row(header, "[green]PRESENT[/green]" if value else "[red]MISSING[/red]", str(value or "-"))
        console.print(f"\nHTTP status: [bold]{response.status_code}[/bold]\n")
        console.print(table)
        save_log("header_analysis", url, result)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    pause()
