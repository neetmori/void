MADE_BY = "Made by unbeau"

import os
import platform
from rich.table import Table
from rich import box
from core.ui import console, module_header, pause

def run():
    module_header("SYSTEM INFORMATION", "System")
    values = {
        "System": platform.system(),
        "Hostname": platform.node(),
        "Kernel": platform.release(),
        "Architecture": platform.machine(),
        "Python": platform.python_version(),
        "User": os.getenv("USER") or os.getenv("USERNAME"),
        "Directory": os.getcwd()
    }
    table = Table(box=box.SIMPLE)
    table.add_column("Field", style="red")
    table.add_column("Value")
    for k, v in values.items():
        table.add_row(k, str(v))
    console.print(table)
    pause()
