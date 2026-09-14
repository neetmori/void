MADE_BY = "Made by unbeau"

import time
import requests
from urllib.parse import urlparse
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel
from core.ui import console, module_header, pause
from core.config import CONFIG

def run():
    module_header("LOCAL HTTP STRESS TEST", "Local Testing")
    console.print("[yellow]Only localhost targets are accepted.[/yellow]\n")
    url = Prompt.ask("URL", default="http://127.0.0.1:8000")
    parsed = urlparse(url)
    if parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        console.print("[red]Blocked. Only localhost is allowed.[/red]")
        pause()
        return
    count = IntPrompt.ask("Requests", default=20)
    count = min(max(1, count), CONFIG["max_local_stress_requests"])
    ok = 0
    failed = 0
    start = time.time()
    for _ in range(count):
        try:
            response = requests.get(url, timeout=3)
            if response.status_code < 500:
                ok += 1
            else:
                failed += 1
        except Exception:
            failed += 1
    elapsed = max(time.time() - start, 0.0001)
    console.print(Panel(f"Success: {ok}\nFailed: {failed}\nTime: {elapsed:.2f}s\nRequests/s: {count / elapsed:.2f}", border_style="red"))
    pause()
