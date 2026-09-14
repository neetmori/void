import statistics
import time
from urllib.parse import urlparse

import requests
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.table import Table

from core.config import CONFIG
from core.logger import save_log
from core.ui import console, module_header, pause


def run():
    module_header("Local HTTP Stress Test", "Local Testing")
    console.print("[yellow]Only loopback targets are accepted.[/yellow]\n")
    url = Prompt.ask("URL", default="http://127.0.0.1:8000")
    parsed = urlparse(url)
    if parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        console.print("[red]Blocked. Only loopback targets are allowed.[/red]")
        pause()
        return

    count = IntPrompt.ask("Requests", default=20)
    count = min(max(1, count), CONFIG["max_local_stress_requests"])
    timeout_raw = Prompt.ask("Timeout seconds", default="3")
    try:
        timeout = float(timeout_raw)
        if timeout <= 0 or timeout > 10:
            raise ValueError
    except ValueError:
        console.print("[red]Timeout must be greater than 0 and no more than 10 seconds.[/red]")
        pause()
        return

    session = requests.Session()
    session.headers.update({"User-Agent": "VOID/1.0"})
    latencies = []
    statuses = {}
    failures = []
    started = time.perf_counter()

    for index in range(count):
        request_started = time.perf_counter()
        try:
            response = session.get(url, timeout=timeout)
            latency_ms = (time.perf_counter() - request_started) * 1000
            latencies.append(latency_ms)
            statuses[response.status_code] = statuses.get(response.status_code, 0) + 1
        except requests.RequestException as exc:
            failures.append({"request": index + 1, "error": str(exc)})

    elapsed = max(time.perf_counter() - started, 0.000001)
    completed = len(latencies)
    success = sum(value for status, value in statuses.items() if status < 500)

    table = Table(title="Local Load Test Results", show_header=False, border_style="red")
    table.add_column("Field", style="bold red")
    table.add_column("Value", style="white")
    table.add_row("Target", url)
    table.add_row("Requests", str(count))
    table.add_row("Completed", str(completed))
    table.add_row("Successful", str(success))
    table.add_row("Failures", str(len(failures)))
    table.add_row("Duration", f"{elapsed:.3f} s")
    table.add_row("Throughput", f"{count / elapsed:.2f} requests/s")
    if latencies:
        sorted_latencies = sorted(latencies)
        p50 = sorted_latencies[min(len(sorted_latencies) - 1, int(len(sorted_latencies) * 0.50))]
        p95 = sorted_latencies[min(len(sorted_latencies) - 1, int(len(sorted_latencies) * 0.95))]
        p99 = sorted_latencies[min(len(sorted_latencies) - 1, int(len(sorted_latencies) * 0.99))]
        table.add_row("Minimum Latency", f"{min(latencies):.2f} ms")
        table.add_row("Average Latency", f"{statistics.mean(latencies):.2f} ms")
        table.add_row("Median Latency", f"{statistics.median(latencies):.2f} ms")
        table.add_row("Maximum Latency", f"{max(latencies):.2f} ms")
        table.add_row("P50", f"{p50:.2f} ms")
        table.add_row("P95", f"{p95:.2f} ms")
        table.add_row("P99", f"{p99:.2f} ms")
    console.print(table)

    status_table = Table(title="HTTP Status Distribution", border_style="red")
    status_table.add_column("Status", style="bold red")
    status_table.add_column("Count", justify="right", style="white")
    for status, amount in sorted(statuses.items()):
        status_table.add_row(str(status), str(amount))
    if status_table.row_count:
        console.print(status_table)

    if failures:
        console.print(Panel("\n".join(item["error"] for item in failures[:10]), title="Request Errors", border_style="yellow"))

    path = save_log(
        "local_stress",
        url,
        {
            "requests": count,
            "timeout": timeout,
            "completed": completed,
            "successful": success,
            "failures": failures,
            "statuses": statuses,
            "latencies_ms": latencies,
            "duration_seconds": elapsed,
            "requests_per_second": count / elapsed,
        },
    )
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
