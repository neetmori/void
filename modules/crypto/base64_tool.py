MADE_BY = "Made by unbeau"

import base64
from rich.prompt import Prompt
from core.ui import console, module_header, pause

def run():
    module_header("BASE64 TOOLKIT", "Encoding")
    option = Prompt.ask("[red]1[/red] Encode  [red]2[/red] Decode")
    if option == "1":
        value = Prompt.ask("Text")
        console.print("\n" + base64.b64encode(value.encode()).decode())
    elif option == "2":
        value = Prompt.ask("Base64")
        try:
            console.print("\n" + base64.b64decode(value).decode())
        except Exception:
            console.print("[red]Invalid Base64.[/red]")
    pause()
