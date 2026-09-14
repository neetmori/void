MADE_BY = "Made by unbeau"

import re
import requests
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from core.ui import console, module_header, pause
from core.validators import ensure_url
from core.config import CONFIG
from core.logger import save_log

def run():
    module_header("TECHNOLOGY LOOKUP", "Web / Lookup")
    url = ensure_url(Prompt.ask("[red]URL[/red]"))
    try:
        response = requests.get(url, timeout=CONFIG["request_timeout"], allow_redirects=True)
        text = response.text.lower()
        headers = {k.lower(): v for k, v in response.headers.items()}
        findings = []
        server = headers.get("server")
        powered = headers.get("x-powered-by")
        if server:
            findings.append(("Server", server))
        if powered:
            findings.append(("X-Powered-By", powered))
        signatures = {
            "WordPress": ["wp-content", "wp-includes"],
            "React": ["react", "__next_data__"],
            "Next.js": ["_next/", "__next_data__"],
            "Vue": ["vue", "__vue__"],
            "Bootstrap": ["bootstrap"],
            "jQuery": ["jquery"],
            "Cloudflare": ["cf-ray", "cloudflare"]
        }
        for name, markers in signatures.items():
            if any(marker in text or marker in headers for marker in markers):
                findings.append(("Detected", name))
        table = Table(box=box.SIMPLE)
        table.add_column("Type", style="red")
        table.add_column("Value")
        for kind, value in findings or [("Detected", "No obvious public signatures found")]:
            table.add_row(kind, value)
        console.print(table)
        save_log("technology_lookup", url, findings)
    except Exception as e:
        console.print(f"[red]Lookup error: {e}[/red]")
    pause()
