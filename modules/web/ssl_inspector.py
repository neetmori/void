MADE_BY = "Made by unbeau"

import socket
import ssl
from datetime import datetime
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from core.ui import console, module_header, pause
from core.validators import normalize_domain
from core.logger import save_log

def run():
    module_header("SSL / TLS INSPECTOR", "Web")
    host = normalize_domain(Prompt.ask("[red]Domain[/red]"))
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=8) as sock:
            with context.wrap_socket(sock, server_hostname=host) as secure:
                cert = secure.getpeercert()
                cipher = secure.cipher()
                result = {"certificate": cert, "cipher": cipher, "tls_version": secure.version()}
                table = Table(box=box.SIMPLE)
                table.add_column("Field", style="red")
                table.add_column("Value")
                table.add_row("TLS Version", str(secure.version()))
                table.add_row("Cipher", str(cipher[0] if cipher else "-"))
                table.add_row("Issuer", str(cert.get("issuer")))
                table.add_row("Subject", str(cert.get("subject")))
                table.add_row("Valid From", str(cert.get("notBefore")))
                table.add_row("Valid Until", str(cert.get("notAfter")))
                table.add_row("Serial", str(cert.get("serialNumber")))
                console.print(table)
                save_log("ssl_inspector", host, result)
    except Exception as e:
        console.print(f"[red]TLS error: {e}[/red]")
    pause()
