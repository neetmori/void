import platform
import re
import socket
import subprocess

from rich.panel import Panel
from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause


def build_command(target, max_hops, timeout):
    system = platform.system().lower()
    if system == "windows":
        return ["tracert", "-d", "-h", str(max_hops), "-w", str(int(timeout * 1000)), target]
    return ["traceroute", "-n", "-m", str(max_hops), "-w", str(timeout), target]


def parse_hops(output):
    hops = []
    for line in output.splitlines():
        stripped = line.strip()
        match = re.match(r"^(\d+)\s+(.*)$", stripped)
        if not match:
            continue
        hop = int(match.group(1))
        rest = match.group(2)
        addresses = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b|\b[0-9a-fA-F:]{2,}\b", rest)
        times = [float(value) for value in re.findall(r"([0-9.]+)\s*ms", rest)]
        hops.append({"hop": hop, "addresses": list(dict.fromkeys(addresses)), "times_ms": times, "raw": stripped})
    return hops


def run():
    module_header("Traceroute", "Network")
    target = console.input("[bold white]Host or IP:[/bold white] ").strip()
    max_hops_raw = console.input("[bold white]Maximum hops [20]:[/bold white] ").strip()
    timeout_raw = console.input("[bold white]Per-hop timeout seconds [2]:[/bold white] ").strip()

    try:
        max_hops = int(max_hops_raw or "20")
        timeout = float(timeout_raw or "2")
        if not 1 <= max_hops <= 30:
            raise ValueError("Maximum hops must be between 1 and 30")
        if timeout <= 0 or timeout > 10:
            raise ValueError("Timeout must be greater than 0 and no more than 10 seconds")
        addresses = sorted({item[4][0] for item in socket.getaddrinfo(target, None)})
    except (ValueError, OSError, socket.gaierror) as exc:
        console.print(f"[red]Input or resolution error: {exc}[/red]")
        pause()
        return

    command = build_command(target, max_hops, timeout)
    try:
        process = subprocess.run(command, capture_output=True, text=True, timeout=(max_hops * timeout) + 20)
    except FileNotFoundError:
        console.print("[red]Traceroute command is not installed on this system.[/red]")
        pause()
        return
    except (OSError, subprocess.TimeoutExpired) as exc:
        console.print(f"[red]Traceroute failed: {exc}[/red]")
        pause()
        return

    output = (process.stdout or "") + (process.stderr or "")
    hops = parse_hops(output)

    table = Table(title=f"Traceroute · {target}", border_style="red")
    table.add_column("Hop", style="bold red", justify="right")
    table.add_column("Address", style="white")
    table.add_column("RTT")
    table.add_column("Reverse DNS")
    for item in hops:
        address = item["addresses"][0] if item["addresses"] else "*"
        hostname = ""
        if address != "*":
            try:
                hostname = socket.gethostbyaddr(address)[0]
            except OSError:
                hostname = ""
        rtt = ", ".join(f"{value:.2f} ms" for value in item["times_ms"]) or "*"
        table.add_row(str(item["hop"]), address, rtt, hostname)
        item["reverse_dns"] = hostname or None
    if table.row_count:
        console.print(table)
    console.print(Panel(output.strip() or "No traceroute output.", title="Raw Traceroute Output", border_style="red"))

    path = save_log("traceroute", target, {"resolved_addresses": addresses, "max_hops": max_hops, "timeout": timeout, "exit_code": process.returncode, "hops": hops, "output": output})
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
