MADE_BY = "Made by unbeau"

import hashlib
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from core.ui import console, module_header, pause

def run():
    module_header("HASH GENERATOR", "Cryptography")
    text = Prompt.ask("[red]Text[/red]")
    data = text.encode()
    values = {
        "MD5": hashlib.md5(data).hexdigest(),
        "SHA1": hashlib.sha1(data).hexdigest(),
        "SHA256": hashlib.sha256(data).hexdigest(),
        "SHA512": hashlib.sha512(data).hexdigest()
    }
    table = Table(box=box.SIMPLE)
    table.add_column("Algorithm", style="red")
    table.add_column("Hash")
    for k, v in values.items():
        table.add_row(k, v)
    console.print(table)
    pause()
