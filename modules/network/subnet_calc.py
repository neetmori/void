MADE_BY = "Made by unbeau"

import ipaddress
from rich.table import Table
from rich import box
from rich.prompt import Prompt
from core.ui import console, module_header, pause

def run():
    module_header("CIDR / SUBNET CALCULATOR", "Network")
    value = Prompt.ask("[red]CIDR[/red]", default="192.168.1.0/24").strip()
    try:
        network = ipaddress.ip_network(value, strict=False)
        table = Table(box=box.SIMPLE)
        table.add_column("Field", style="red")
        table.add_column("Value")
        rows = {
            "Network": network.network_address,
            "Broadcast": network.broadcast_address,
            "Netmask": network.netmask,
            "Hostmask": network.hostmask,
            "Prefix": network.prefixlen,
            "Total Addresses": network.num_addresses,
            "IP Version": network.version
        }
        for k, v in rows.items():
            table.add_row(k, str(v))
        console.print(table)
    except Exception as e:
        console.print(f"[red]Invalid CIDR: {e}[/red]")
    pause()
