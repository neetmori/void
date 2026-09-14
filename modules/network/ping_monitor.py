MADE_BY = "Made by unbeau"

import subprocess
from rich.prompt import Prompt, IntPrompt
from core.ui import console, module_header, pause

def run():
    module_header("PING MONITOR", "Network")
    target = Prompt.ask("[red]Host[/red]").strip()
    count = max(1, min(IntPrompt.ask("Count", default=4), 20))
    try:
        result = subprocess.run(["ping", "-c", str(count), target], capture_output=True, text=True, timeout=30)
        console.print(result.stdout or result.stderr)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    pause()
