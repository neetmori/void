MADE_BY = "Made by unbeau"

import hashlib
from pathlib import Path
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from core.ui import console, module_header, pause

def digest(path, algorithm):
    h = hashlib.new(algorithm)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def run():
    module_header("FILE HASH CALCULATOR", "Files")
    path = Path(Prompt.ask("[red]File path[/red]").strip()).expanduser()
    if not path.is_file():
        console.print("[red]File not found.[/red]")
        pause()
        return
    table = Table(box=box.SIMPLE)
    table.add_column("Algorithm", style="red")
    table.add_column("Hash")
    for algorithm in ["md5", "sha1", "sha256", "sha512"]:
        table.add_row(algorithm.upper(), digest(path, algorithm))
    console.print(table)
    pause()
