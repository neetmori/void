MADE_BY = "Made by unbeau"

from urllib.parse import urlparse, parse_qs
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from core.ui import console, module_header, pause
from core.validators import ensure_url

def run():
    module_header("URL PARSER", "Web")
    url = ensure_url(Prompt.ask("[red]URL[/red]"))
    parsed = urlparse(url)
    table = Table(box=box.SIMPLE)
    table.add_column("Field", style="red")
    table.add_column("Value")
    data = {
        "Scheme": parsed.scheme,
        "Hostname": parsed.hostname,
        "Port": parsed.port,
        "Path": parsed.path,
        "Query": parsed.query,
        "Fragment": parsed.fragment,
        "Parameters": parse_qs(parsed.query)
    }
    for k, v in data.items():
        table.add_row(k, str(v))
    console.print(table)
    pause()
