import platform
import re
import socket
import subprocess
import time

from rich.panel import Panel
from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause


def build_command(target, count, timeout):
    system = platform.system().lower()
    if system == "windows":
        return ["ping", "-n", str(count), "-w", str(int(timeout * 1000)), target]
    return ["ping", "-c", str(count), "-W", str(max(1, int(timeout))), target]


def parse_times(output):
    matches = re.findall(r"(?:time[=<]|tempo[=<])\s*([0-9.]+)\s*ms", output, flags=re.IGNORECASE)
    return [float(value) for value in matches]


def run():
    module_header("Ping Monitor", "Network")
    target = console.input("[bold white]Host or IP:[/bold white] ").strip()
    count_raw = console.input("[bold white]Packets [4]:[/bold white] ").strip()
    timeout_raw = console.input("[bold white]Per-packet timeout seconds [2]:[/bold white] ").strip()

    try:
        count = int(count_raw or "4")
        timeout = float(timeout_raw or "2")
        if not 1 <= count <= 10:
            raise ValueError("Packet count must be between 1 and 10")
        if timeout <= 0 or timeout > 10:
            raise ValueError("Timeout must be greater than 0 and no more than 10 seconds")
        addresses = sorted({item[4][0] for item in socket.getaddrinfo(target, None)})
    except (ValueError, OSError, socket.gaierror) as exc:
        console.print(f"[red]Input or resolution error: {exc}[/red]")
        pause()
        return

    command = build_command(target, count, timeout)
    started = time.perf_counter()
    try:
        process = subprocess.run(command, capture_output=True, text=True, timeout=(count * timeout) + 10)
    except (OSError, subprocess.TimeoutExpired) as exc:
        console.print(f"[red]Ping failed: {exc}[/red]")
        pause()
        return
    elapsed_ms = (time.perf_counter() - started) * 1000
    output = (process.stdout or "") + (process.stderr or "")
    times = parse_times(output)

    table = Table(title="Ping Diagnostics", show_header=False, border_style="red")
    table.add_column("Field", style="bold red")
    table.add_column("Value", style="white")
    table.add_row("Target", target)
    table.add_row("Resolved Addresses", "\n".join(addresses))
    table.add_row("Packets Requested", str(count))
    table.add_row("Exit Code", str(process.returncode))
    table.add_row("Replies Parsed", str(len(times)))
    table.add_row("Loss Estimate", f"{(1 - len(times) / count) * 100:.1f}%")
    if times:
        table.add_row("Minimum RTT", f"{min(times):.2f} ms")
        table.add_row("Average RTT", f"{sum(times) / len(times):.2f} ms")
        table.add_row("Maximum RTT", f"{max(times):.2f} ms")
    table.add_row("Command Duration", f"{elapsed_ms:.2f} ms")
    console.print(table)
    console.print(Panel(output.strip() or "No ping output.", title="Raw Ping Output", border_style="red"))

    path = save_log(
        "ping_monitor",
        target,
        {
            "addresses": addresses,
            "packets_requested": count,
            "timeout": timeout,
            "exit_code": process.returncode,
            "round_trip_times_ms": times,
            "loss_percent_estimate": (1 - len(times) / count) * 100,
            "duration_ms": elapsed_ms,
            "output": output,
        },
    )
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
