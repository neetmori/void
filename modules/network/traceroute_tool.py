MADE_BY = "Made by unbeau"

import subprocess
from rich.prompt import Prompt
from core.ui import console, module_header, pause

def run():
    module_header("TRACEROUTE", "Network")
    target = Prompt.ask("[red]Host[/red]").strip()
    try:
        result = subprocess.run(["traceroute", target], capture_output=True, text=True, timeout=60)
        console.print(result.stdout or result.stderr)
    except FileNotFoundError:
        console.print("[yellow]Install traceroute with: sudo pacman -S traceroute[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    pause()
