MADE_BY = "Made by unbeau"

import re
from rich.prompt import Prompt
from core.ui import console, module_header, pause

def run():
    module_header("HASH ANALYZER", "Cryptography")
    value = Prompt.ask("[red]Hash[/red]").strip()
    result = []
    if re.fullmatch(r"[a-fA-F0-9]+", value):
        result = {32:["MD5"],40:["SHA-1"],64:["SHA-256"],96:["SHA-384"],128:["SHA-512"]}.get(len(value), [])
    console.print(f"\nLength: {len(value)}")
    console.print("Possible type: " + (", ".join(result) if result else "Unknown"))
    pause()
