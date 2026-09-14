MADE_BY = "Made by unbeau"

import ipaddress
from urllib.parse import urlparse

LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}

def require_local_target(value):
    parsed = urlparse(value if "://" in value else f"http://{value}")
    host = parsed.hostname or value
    if host in LOCAL_HOSTS:
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False

import requests
from rich.prompt import Prompt, IntPrompt
from core.ui import console, module_header, pause

MAX_REQUESTS = 100

def run():
    module_header("LOCAL LOAD TEST", "Training / Local Only")
    target = Prompt.ask("[red]Local URL[/red]", default="http://127.0.0.1:8000").strip()
    if not require_local_target(target):
        console.print("[red]Blocked: only localhost targets are allowed.[/red]")
        pause()
        return

    count = IntPrompt.ask("Requests", default=25)
    count = max(1, min(count, MAX_REQUESTS))

    ok = 0
    failed = 0

    for _ in range(count):
        try:
            response = requests.get(target, timeout=2)
            if response.ok:
                ok += 1
            else:
                failed += 1
        except requests.RequestException:
            failed += 1

    console.print(f"Successful: {ok}")
    console.print(f"Failed: {failed}")
    console.print(f"Limit: {MAX_REQUESTS}")
    console.print("\n[dim]Remote destinations are blocked.[/dim]")
    pause()
