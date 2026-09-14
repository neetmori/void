MADE_BY = "Made by unbeau"

import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.align import Align
from rich import box

console = Console()

BANNER = r"""
[bold white]
██╗   ██╗ ██████╗ ██╗██████╗
██║   ██║██╔═══██╗██║██╔══██╗
██║   ██║██║   ██║██║██║  ██║
╚██╗ ██╔╝██║   ██║██║██║  ██║
 ╚████╔╝ ╚██████╔╝██║██████╔╝
  ╚═══╝   ╚═════╝ ╚═╝╚═════╝
[/bold white]
[bold red] C Y B E R S E C U R I T Y   F R A M E W O R K [/bold red]
"""

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def draw_header():
    clear_screen()
    console.print(Align.center(BANNER))

def module_header(name, category):
    draw_header()
    console.print(Panel(f"[bold white]{name}[/bold white]\n[dim]Category: {category}[/dim]", title="[bold red]VOID // MODULE[/bold red]", border_style="red"))

def pause():
    Prompt.ask("\n[bold red]Press ENTER to return[/bold red]")

def menu_table(rows):
    table = Table(box=box.ROUNDED, border_style="red", header_style="bold bright_red", expand=True)
    table.add_column("ID", width=4, max_width=4, no_wrap=True, justify="center", style="bold red")
    table.add_column("Tool", ratio=1, style="bold white")
    for row in rows:
        table.add_row(row[0], row[1])
    return table
