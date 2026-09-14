import socket
import time

from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause


def parse_ports(value):
    ports = set()
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_raw, end_raw = part.split("-", 1)
            start = int(start_raw)
            end = int(end_raw)
            if start > end:
                start, end = end, start
            for port in range(start, end + 1):
                ports.add(port)
        else:
            ports.add(int(part))
    if not ports:
        raise ValueError("No ports supplied")
    if any(port < 1 or port > 65535 for port in ports):
        raise ValueError("Ports must be between 1 and 65535")
    if len(ports) > 100:
        raise ValueError("A maximum of 100 ports can be checked per run")
    return sorted(ports)


def service_name(port):
    try:
        return socket.getservbyport(port, "tcp")
    except OSError:
        return "unknown"


def resolve_target(target):
    info = socket.getaddrinfo(target, None, type=socket.SOCK_STREAM)
    addresses = []
    for item in info:
        address = item[4][0]
        if address not in addresses:
            addresses.append(address)
    return addresses


def check_port(address, port, timeout):
    family = socket.AF_INET6 if ":" in address else socket.AF_INET
    started = time.perf_counter()
    with socket.socket(family, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        result = sock.connect_ex((address, port))
    elapsed_ms = (time.perf_counter() - started) * 1000
    return result == 0, elapsed_ms, result


def run():
    module_header("TCP Port Scanner", "Network")
    target = console.input("[bold white]Host or IP:[/bold white] ").strip()
    port_text = console.input("[bold white]Ports, for example 22,80,443 or 8000-8010:[/bold white] ").strip()
    timeout_raw = console.input("[bold white]Timeout seconds [0.7]:[/bold white] ").strip()

    try:
        ports = parse_ports(port_text)
        timeout = float(timeout_raw or "0.7")
        if timeout <= 0 or timeout > 10:
            raise ValueError("Timeout must be greater than 0 and no more than 10 seconds")
        addresses = resolve_target(target)
    except (ValueError, OSError, socket.gaierror) as exc:
        console.print(f"[red]Input or resolution error: {exc}[/red]")
        pause()
        return

    results = []
    for address in addresses:
        for port in ports:
            try:
                is_open, elapsed_ms, code = check_port(address, port, timeout)
                results.append({
                    "address": address,
                    "port": port,
                    "service": service_name(port),
                    "open": is_open,
                    "elapsed_ms": elapsed_ms,
                    "result_code": code,
                })
            except OSError as exc:
                results.append({"address": address, "port": port, "service": service_name(port), "open": False, "error": str(exc)})

    table = Table(title=f"TCP Port Check · {target}", border_style="red")
    table.add_column("Address", style="white")
    table.add_column("Port", style="bold red", justify="right")
    table.add_column("Service")
    table.add_column("State")
    table.add_column("Latency", justify="right")
    for item in results:
        table.add_row(
            item["address"],
            str(item["port"]),
            item["service"],
            "Open" if item.get("open") else "Closed/Filtered",
            f"{item.get('elapsed_ms', 0):.2f} ms" if "elapsed_ms" in item else "-",
        )
    console.print(table)

    open_ports = [item for item in results if item.get("open")]
    path = save_log("port_scanner", target, {"addresses": addresses, "ports": ports, "timeout": timeout, "open_ports": open_ports, "results": results})
    console.print(f"[dim]Open ports: {len(open_ports)} of {len(results)} checks[/dim]")
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
