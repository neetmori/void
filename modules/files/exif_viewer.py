MADE_BY = "Made by unbeau"

from pathlib import Path
from PIL import Image, ExifTags
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from core.ui import console, module_header, pause

def run():
    module_header("EXIF METADATA VIEWER", "Files")
    path = Path(Prompt.ask("[red]Image path[/red]").strip()).expanduser()
    if not path.is_file():
        console.print("[red]File not found.[/red]")
        pause()
        return
    try:
        image = Image.open(path)
        exif = image.getexif()
        table = Table(box=box.SIMPLE)
        table.add_column("Tag", style="red")
        table.add_column("Value")
        if not exif:
            console.print("[yellow]No EXIF metadata found.[/yellow]")
        else:
            for key, value in exif.items():
                name = ExifTags.TAGS.get(key, str(key))
                table.add_row(name, str(value)[:500])
            console.print(table)
    except Exception as e:
        console.print(f"[red]EXIF error: {e}[/red]")
    pause()
