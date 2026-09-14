MADE_BY = "Made by unbeau"

import requests
from urllib.parse import urljoin
from rich.prompt import Prompt
from core.ui import console, module_header, pause
from core.validators import ensure_url
from core.config import CONFIG
from core.logger import save_log

def run():
    module_header("SECURITY.TXT LOOKUP", "OSINT / Lookup")
    base = ensure_url(Prompt.ask("[red]Website URL[/red]"))
    candidates = ["/.well-known/security.txt", "/security.txt"]
    found = []
    for path in candidates:
        url = urljoin(base, path)
        try:
            response = requests.get(url, timeout=CONFIG["request_timeout"])
            if response.status_code == 200 and response.text.strip():
                found.append({"url": url, "content": response.text[:5000]})
        except Exception:
            pass
    if not found:
        console.print("[yellow]security.txt not found.[/yellow]")
    else:
        for item in found:
            console.print(f"\n[red]{item['url']}[/red]")
            console.print(item["content"])
    save_log("security_txt_lookup", base, {"found": found})
    pause()
