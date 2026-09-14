MADE_BY = "Made by unbeau"

import socket
from rich.prompt import Prompt
from core.ui import console, module_header, pause
from core.logger import save_log
from core.validators import valid_ip

def run():
    module_header("REVERSE DNS", "Network")
    target = Prompt.ask("[red]IP[/red]").strip()
    if not valid_ip(target):
        console.print("[red]Invalid IP.[/red]")
        pause()
        return
    try:
        hostname, aliases, addresses = socket.gethostbyaddr(target)
        result = {"hostname": hostname, "aliases": aliases, "addresses": addresses}
        console.print(f"\nHostname: [green]{hostname}[/green]")
        save_log("reverse_dns", target, result)
    except Exception as e:
        console.print(f"[red]Reverse DNS failed: {e}[/red]")
    pause()
