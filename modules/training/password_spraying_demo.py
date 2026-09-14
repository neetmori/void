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
from rich.prompt import Prompt
from core.ui import console, module_header, pause

def run():
    module_header("LOCAL PASSWORD SPRAY TEST", "Training / Local Only")
    target = Prompt.ask("[red]Local login endpoint[/red]", default="http://127.0.0.1:8000/login").strip()
    if not require_local_target(target):
        console.print("[red]Blocked: only localhost targets are allowed.[/red]")
        pause()
        return

    users = ["training-user-1", "training-user-2", "training-user-3"]
    password = "ExamplePassword1"

    for username in users:
        try:
            response = requests.post(
                target,
                json={"username": username, "password": password},
                timeout=2
            )
            console.print(f"{username}: HTTP {response.status_code}")
        except requests.RequestException as e:
            console.print(f"{username}: {e}")

    console.print("\n[dim]This module cannot target remote hosts.[/dim]")
    pause()
