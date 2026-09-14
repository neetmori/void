MADE_BY = "Made by unbeau"

import requests
from rich.prompt import Prompt
from core.ui import console, module_header, pause
from core.config import CONFIG
from core.logger import save_log

def run():
    module_header("MAC VENDOR LOOKUP", "OSINT")
    mac = Prompt.ask("[red]MAC address[/red]").strip()
    try:
        response = requests.get(f"https://api.macvendors.com/{mac}", timeout=CONFIG["request_timeout"])
        vendor = response.text.strip() if response.ok else "Not found"
        console.print(f"\nVendor: [bold green]{vendor}[/bold green]")
        save_log("mac_lookup", mac, {"vendor": vendor})
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    pause()
