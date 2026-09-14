MADE_BY = "Made by unbeau"

import requests
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from core.ui import console, module_header, pause
from core.config import CONFIG
from core.logger import save_log

def run():
    module_header("GITHUB USER LOOKUP", "OSINT / Lookup")
    username = Prompt.ask("[red]GitHub username[/red]").strip()
    try:
        response = requests.get(f"https://api.github.com/users/{username}", timeout=CONFIG["request_timeout"], headers={"Accept": "application/vnd.github+json"})
        if response.status_code == 404:
            console.print("[yellow]User not found.[/yellow]")
            pause()
            return
        data = response.json()
        fields = ["login", "name", "html_url", "company", "blog", "location", "bio", "public_repos", "followers", "following", "created_at", "updated_at"]
        table = Table(box=box.SIMPLE)
        table.add_column("Field", style="red")
        table.add_column("Value")
        result = {}
        for field in fields:
            value = data.get(field)
            result[field] = value
            table.add_row(field.replace("_", " ").title(), str(value or "-"))
        console.print(table)
        save_log("github_user_lookup", username, result)
    except Exception as e:
        console.print(f"[red]Lookup error: {e}[/red]")
    pause()
