import getpass
import os
import platform
import shutil
import socket
import sys
from pathlib import Path

from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause


def run():
    module_header("System Information", "System")
    hostname = socket.gethostname()
    try:
        local_addresses = sorted({item[4][0] for item in socket.getaddrinfo(hostname, None)})
    except OSError:
        local_addresses = []

    home = Path.home()
    disk = shutil.disk_usage(home)
    data = {
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "architecture": platform.architecture()[0],
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "python_executable": sys.executable,
        "hostname": hostname,
        "username": getpass.getuser(),
        "home": str(home),
        "working_directory": os.getcwd(),
        "cpu_count": os.cpu_count(),
        "local_addresses": local_addresses,
        "disk_total": disk.total,
        "disk_used": disk.used,
        "disk_free": disk.free,
    }

    table = Table(title="Local System Information", show_header=False, border_style="red")
    table.add_column("Field", style="bold red")
    table.add_column("Value", style="white")
    for key, value in data.items():
        if isinstance(value, list):
            value = "\n".join(value) or "None"
        table.add_row(key.replace("_", " ").title(), str(value if value not in (None, "") else "Unknown"))
    console.print(table)

    path = save_log("system_info", hostname, data)
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
