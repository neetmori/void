import ipaddress

from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause


def run():
    module_header("CIDR Calculator", "Network")
    target = console.input("[bold white]Network or IP/CIDR:[/bold white] ").strip()
    try:
        network = ipaddress.ip_network(target, strict=False)
    except ValueError as exc:
        console.print(f"[red]Invalid network: {exc}[/red]")
        pause()
        return

    hosts = network.num_addresses
    if network.version == 4:
        usable = max(hosts - 2, 0) if network.prefixlen <= 30 else hosts
        first_host = network.network_address if network.prefixlen >= 31 else network.network_address + 1
        last_host = network.broadcast_address if network.prefixlen >= 31 else network.broadcast_address - 1
        netmask = network.netmask
        hostmask = network.hostmask
        broadcast = network.broadcast_address
    else:
        usable = hosts
        first_host = network.network_address
        last_host = network[-1]
        netmask = network.netmask
        hostmask = network.hostmask
        broadcast = None

    reverse_zones = []
    try:
        reverse_zones = [str(item) for item in network.reverse_pointer.split()] if hasattr(network, "reverse_pointer") else []
    except Exception:
        reverse_zones = []

    table = Table(title="CIDR Information", show_header=False, border_style="red")
    table.add_column("Field", style="bold red")
    table.add_column("Value", style="white")
    table.add_row("IP Version", str(network.version))
    table.add_row("Network", str(network.network_address))
    table.add_row("CIDR", str(network.with_prefixlen))
    table.add_row("Prefix Length", str(network.prefixlen))
    table.add_row("Netmask", str(netmask))
    table.add_row("Hostmask", str(hostmask))
    table.add_row("Broadcast", str(broadcast) if broadcast is not None else "Not applicable")
    table.add_row("First Address", str(first_host))
    table.add_row("Last Address", str(last_host))
    table.add_row("Total Addresses", str(hosts))
    table.add_row("Usable Addresses", str(usable))
    table.add_row("Private", str(network.is_private))
    table.add_row("Global", str(network.is_global))
    table.add_row("Loopback", str(network.is_loopback))
    table.add_row("Link Local", str(network.is_link_local))
    table.add_row("Multicast", str(network.is_multicast))
    table.add_row("Reserved", str(network.is_reserved))
    table.add_row("Unspecified", str(network.is_unspecified))
    console.print(table)

    splits = []
    if network.prefixlen < network.max_prefixlen:
        next_prefix = min(network.prefixlen + 1, network.max_prefixlen)
        splits = [str(item) for item in network.subnets(new_prefix=next_prefix)]
        if splits:
            split_table = Table(title=f"Immediate /{next_prefix} Split", border_style="red")
            split_table.add_column("Subnet", style="white")
            for item in splits[:16]:
                split_table.add_row(item)
            console.print(split_table)

    path = save_log(
        "subnet_calc",
        target,
        {
            "version": network.version,
            "network": str(network.network_address),
            "cidr": str(network.with_prefixlen),
            "prefix_length": network.prefixlen,
            "netmask": str(netmask),
            "hostmask": str(hostmask),
            "broadcast": str(broadcast) if broadcast is not None else None,
            "first_address": str(first_host),
            "last_address": str(last_host),
            "total_addresses": hosts,
            "usable_addresses": usable,
            "flags": {
                "private": network.is_private,
                "global": network.is_global,
                "loopback": network.is_loopback,
                "link_local": network.is_link_local,
                "multicast": network.is_multicast,
                "reserved": network.is_reserved,
                "unspecified": network.is_unspecified,
            },
            "immediate_split": splits,
        },
    )
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
