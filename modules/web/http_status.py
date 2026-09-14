MADE_BY = "Made by unbeau"

import time
import requests
from rich.prompt import Prompt
from rich.panel import Panel
from core.ui import console, module_header, pause
from core.validators import ensure_url
from core.config import CONFIG

def run():
    module_header("HTTP STATUS CHECK", "Web")
    url = ensure_url(Prompt.ask("[red]URL[/red]"))
    try:
        start = time.time()
        response = requests.get(url, timeout=CONFIG["request_timeout"], allow_redirects=True)
        elapsed = time.time() - start
        console.print(Panel(f"URL: {response.url}\nStatus: {response.status_code}\nTime: {elapsed:.3f}s\nSize: {len(response.content)} bytes", border_style="red"))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    pause()
