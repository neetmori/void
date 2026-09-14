MADE_BY = "Made by unbeau"

import base64
import hashlib
import requests
from urllib.parse import urljoin
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from core.ui import console, module_header, pause
from core.validators import ensure_url
from core.config import CONFIG
from core.logger import save_log

def run():
    module_header("FAVICON HASH", "OSINT / Lookup")
    base = ensure_url(Prompt.ask("[red]Website URL[/red]"))
    url = urljoin(base, "/favicon.ico")
    try:
        response = requests.get(url, timeout=CONFIG["request_timeout"])
        response.raise_for_status()
        data = response.content
        result = {
            "url": url,
            "md5": hashlib.md5(data).hexdigest(),
            "sha1": hashlib.sha1(data).hexdigest(),
            "sha256": hashlib.sha256(data).hexdigest(),
            "size": len(data)
        }
        table = Table(box=box.SIMPLE)
        table.add_column("Field", style="red")
        table.add_column("Value")
        for k, v in result.items():
            table.add_row(k.upper(), str(v))
        console.print(table)
        save_log("favicon_hash", base, result)
    except Exception as e:
        console.print(f"[red]Lookup error: {e}[/red]")
    pause()
