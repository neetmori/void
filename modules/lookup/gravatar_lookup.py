MADE_BY = "Made by unbeau"

import hashlib
import requests
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from core.ui import console, module_header, pause
from core.config import CONFIG
from core.logger import save_log

def run():
    module_header("GRAVATAR LOOKUP", "OSINT / Lookup")
    email = Prompt.ask("[red]Email[/red]").strip().lower()
    digest = hashlib.md5(email.encode()).hexdigest()
    profile = f"https://www.gravatar.com/{digest}.json"
    try:
        response = requests.get(profile, timeout=CONFIG["request_timeout"])
        if response.status_code != 200:
            console.print("[yellow]No public Gravatar profile found.[/yellow]")
            pause()
            return
        entry = response.json().get("entry", [{}])[0]
        result = {
            "display_name": entry.get("displayName"),
            "profile_url": entry.get("profileUrl"),
            "preferred_username": entry.get("preferredUsername"),
            "about_me": entry.get("aboutMe"),
            "location": entry.get("currentLocation")
        }
        table = Table(box=box.SIMPLE)
        table.add_column("Field", style="red")
        table.add_column("Value")
        for k, v in result.items():
            table.add_row(k.replace("_", " ").title(), str(v or "-"))
        console.print(table)
        save_log("gravatar_lookup", email, result)
    except Exception as e:
        console.print(f"[red]Lookup error: {e}[/red]")
    pause()
