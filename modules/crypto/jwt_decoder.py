MADE_BY = "Made by unbeau"

import base64
import json
from rich.prompt import Prompt
from core.ui import console, module_header, pause

def decode_part(value):
    value += "=" * (-len(value) % 4)
    return json.loads(base64.urlsafe_b64decode(value.encode()).decode())

def run():
    module_header("JWT DECODER", "Encoding")
    token = Prompt.ask("[red]JWT[/red]").strip()
    parts = token.split(".")
    if len(parts) < 2:
        console.print("[red]Invalid JWT format.[/red]")
        pause()
        return
    try:
        console.print("\n[bold]Header[/bold]")
        console.print_json(json.dumps(decode_part(parts[0])))
        console.print("\n[bold]Payload[/bold]")
        console.print_json(json.dumps(decode_part(parts[1])))
        console.print("\n[dim]Signature is not verified by this decoder.[/dim]")
    except Exception as e:
        console.print(f"[red]Decode error: {e}[/red]")
    pause()
