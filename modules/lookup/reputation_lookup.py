MADE_BY = "Made by unbeau"

import json
import base64
import requests
from pathlib import Path
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from core.ui import console, module_header, pause
from core.config import BASE_DIR, CONFIG
from core.validators import valid_ip, normalize_domain, ensure_url
from core.logger import save_log

def load_key():
    path = BASE_DIR / "api_keys.json"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("virustotal")
    except Exception:
        return None

def entity_id(kind, value):
    if kind == "URL":
        return base64.urlsafe_b64encode(value.encode()).decode().strip("=")
    return value

def run():
    module_header("REPUTATION LOOKUP", "OSINT / Lookup")
    key = load_key()
    if not key:
        console.print("[yellow]VirusTotal API key not configured.[/yellow]")
        console.print("[dim]Copy api_keys.json.example to api_keys.json and add your own key.[/dim]")
        pause()
        return
    kind = Prompt.ask("Type", choices=["IP", "DOMAIN", "URL", "HASH"], default="DOMAIN")
    value = Prompt.ask(f"[red]{kind}[/red]").strip()
    endpoints = {
        "IP": "ip_addresses",
        "DOMAIN": "domains",
        "URL": "urls",
        "HASH": "files"
    }
    if kind == "IP" and not valid_ip(value):
        console.print("[red]Invalid IP.[/red]")
        pause()
        return
    if kind == "DOMAIN":
        value = normalize_domain(value)
    if kind == "URL":
        value = ensure_url(value)
    identifier = entity_id(kind, value)
    url = f"https://www.virustotal.com/api/v3/{endpoints[kind]}/{identifier}"
    try:
        response = requests.get(url, headers={"x-apikey": key}, timeout=CONFIG["request_timeout"])
        if response.status_code >= 400:
            console.print(f"[red]API error: HTTP {response.status_code}[/red]")
            pause()
            return
        data = response.json().get("data", {}).get("attributes", {})
        stats = data.get("last_analysis_stats", {})
        table = Table(box=box.SIMPLE)
        table.add_column("Result", style="red")
        table.add_column("Count")
        for name in ["malicious", "suspicious", "harmless", "undetected", "timeout"]:
            if name in stats:
                table.add_row(name.title(), str(stats.get(name)))
        console.print(table)
        save_log("reputation_lookup", value, {"type": kind, "stats": stats})
    except Exception as e:
        console.print(f"[red]Lookup error: {e}[/red]")
    pause()
