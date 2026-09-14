MADE_BY = "Made by unbeau"

import socket
from rich.table import Table
from rich import box
from rich.prompt import Prompt
from core.ui import console, module_header, pause
from core.config import CONFIG
from core.logger import save_log

def run():
    module_header("TCP PORT SCANNER", "Network")
    target = Prompt.ask("[red]Authorized host or IP[/red]").strip()
    ports_text = Prompt.ask("Ports", default=",".join(map(str, CONFIG["default_ports"])))
    try:
        ip = socket.gethostbyname(target)
        ports = [int(x.strip()) for x in ports_text.split(",") if x.strip().isdigit() and 1 <= int(x.strip()) <= 65535]
    except Exception as e:
        console.print(f"[red]Invalid target: {e}[/red]")
        pause()
        return
    table = Table(box=box.SIMPLE)
    table.add_column("Port")
    table.add_column("Status")
    table.add_column("Service")
    result = []
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(CONFIG["port_timeout"])
        state = sock.connect_ex((ip, port))
        sock.close()
        if state == 0:
            try:
                service = socket.getservbyport(port, "tcp")
            except Exception:
                service = "unknown"
            table.add_row(str(port), "[green]OPEN[/green]", service)
            result.append({"port": port, "status": "open", "service": service})
    console.print(table)
    save_log("port_scan", target, {"resolved_ip": ip, "results": result})
    pause()
