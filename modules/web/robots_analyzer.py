MADE_BY = "Made by unbeau"

import requests
from rich.prompt import Prompt
from core.ui import console, module_header, pause
from core.validators import ensure_url
from core.config import CONFIG

def run():
    module_header("ROBOTS.TXT ANALYZER", "Web")
    base = ensure_url(Prompt.ask("[red]Website[/red]")).rstrip("/")
    url = base + "/robots.txt"
    try:
        response = requests.get(url, timeout=CONFIG["request_timeout"])
        console.print(f"\nStatus: {response.status_code}\n")
        console.print(response.text[:12000] if response.ok else "[yellow]robots.txt not found.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    pause()
